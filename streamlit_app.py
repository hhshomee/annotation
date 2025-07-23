# streamlit_app.py
from datetime import datetime
import streamlit as st
import json
import gspread
import pytz
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(
    page_title="LLM Human Evaluation",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

creds_dict = json.loads(st.secrets["gcp_credentials"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

client = gspread.authorize(creds)
SPREADSHEET_ID = "1i_WpnrWuhGnAGWxDpWGh_BXHQi8ajdHHOzChGNSVpyE"
sheet = client.open_by_key(SPREADSHEET_ID).sheet1

# Load tasks
with open("tasks.json", "r") as f:
    tasks = json.load(f)

# Initialize session state
if "task_index" not in st.session_state:
    st.session_state.task_index = 0

# Check if all tasks are completed
if st.session_state.task_index >= len(tasks):
    st.markdown("🎉 All tasks completed! Thank you for your evaluations!")
    st.stop()

# Get current task
task = tasks[st.session_state.task_index]

# INSTRUCTIONS AT TOP
st.title("LLM Human Evaluation")
st.markdown('<div id="top"></div>', unsafe_allow_html=True)
progress_percentage = (st.session_state.task_index) / len(tasks)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.progress(progress_percentage)
    st.markdown(f"<div style='text-align: center; font-size: 18px; font-weight: bold;'>Task {st.session_state.task_index + 1} of {len(tasks)} ({int(progress_percentage * 100)}% Complete)</div>", unsafe_allow_html=True)

st.markdown("""
### 📋 Instructions
Please carefully review the **question, user profile, and answer** provided. Then examine the **knowledge sources** that were used to generate the response. 
Rate the quality of the answer across **four key dimensions** using the scales below.\n Please make sure to scroll up after submitting ratings for one answer (it doesn't automatically show the top of the page).
""")

st.markdown("---")

# MAIN CONTENT - LEFT AND RIGHT SPLIT
col_left, col_right = st.columns([1, 1])  # Equal width columns

# LEFT SIDE: Question, Profile, Answer
with col_left:
    st.header("📌 Question")
    st.markdown(task['question'])
    
    st.markdown("### 👤 User Profile")
    st.markdown(task['user_profile'])
    
    st.markdown("### 📄 Answer")
    st.markdown(task['answer'])
    st.header("📌 Paraphrased Question")
    st.markdown(task['para_question'])
    
    st.markdown("### 📄 Paraphrased Answer")
    st.markdown(task['para_answer'])


# RIGHT SIDE: Knowledge Sources
with col_right:
    st.header("📚 Knowledge Sources")
    
    if 'knowledge_sources' in task:
        for i, source in enumerate(task['knowledge_sources'], 1):
            with st.expander(f"Source {i}", expanded=True):
                st.markdown(source)
    else:
        st.info("No knowledge sources available for this task.")

st.markdown("---")

# METRICS SECTION - FULL WIDTH
st.header("⭐ Evaluation Metrics")

# Create columns for metrics layout
metrics_col1, metrics_col2 = st.columns(2)

with metrics_col1:
    st.markdown("""
    **🔍 Specificity**  
    *Specificity measures how precisely the answer includes verifiable specific details that are supported by the provided knowledge sources.*  
    - Hazard Type Match - Does the answer correctly reflect the type of hazard discussed in the sources (e.g., heat waves,snowstorms)?
    
    Options are:
    1. No, hazard is incorrect or not discussed or different hazard is mentioned in sources
    2. Partially correct (correct category but vague or overly general)
    3. Yes, matches specific hazard discussed
    """)
    hazard_matching = st.radio(
        "**Rate Hazard Type Matching**", 
        ["No",
         "Partially correct", 
         "Yes"],
        key="hazard_matching"
    )
    st.markdown("""
    **🔍 Specificity**  
   
    - Location, Timeline, and Intensity Match
    Options are:
    1. No, the specific details are incorrect or not mentioned in sources
    2. Partially correct (correct category but vague or overly general)
    3. Yes, matches specific details
    """)
   
    other_matching = st.radio(
        "**Rate Location, timeline and Intensity**", 
        ["No",
         "Partially correct", 
         "Yes"],
        key="other_matching"
    )

  
    # st.markdown("""
    # **🧪 2. Does the Answer Mention Verifiable Factual Details from the Source?**  
    # *(e.g., "heat waves declared disaster in 2018," "911 dispatch data from Chicago," "homebound elderly at risk")*
    # - No verifiable facts or vague
    # - 1–2 verifiable facts
    # - 3 or more verifiable facts from sources
    
    # *(This acts as a **proxy for fine-grained claim-level specificity** but at a **categorical level**.)*
    # """)
    
    # verifiable_facts = st.selectbox(
    #      "Rate Location, timeline, intensity Matching", 
    #      ["No, hazard is incorrect or not discussed or different hazard is mentioned in sources",
    #      "Partially correct (correct category but vague or overly general)", 
    #      "Yes, matches specific hazard discussed"]
    #     key="verifiable_facts"
    # )
    
    # specificity = st.slider("Rate Specificity", 1, 5, 3, key="specificity")
    
    st.markdown("""
    **💪 Robustness (0-1)**  
    *Robustness measures whether the answer maintains its meaning and factual accuracy when the question is paraphrased.*  
    - 1: Yes – The answers are semantically equivalent. They convey the same information and preserve key factual content.
    - 0.5: Partially – The answers are mostly similar but differ in minor facts or phrasing that could affect nuance or detail.
    - 0: No – The answers are meaningfully different or contradict each other in facts, emphasis, or interpretation.
    """)
    
    robustness = st.slider("Rate Robustness",0.0, 1.0, 0.5, step=0.1, key="robustness")

with metrics_col2:
    st.markdown("""
    **🎯 Relevance (0-1)**  
    *Answer Relevance measures whether the answer is relevant to the question asked by the user.*  
    - 1: Yes – The answer is relevant.
    - 0.5: Partially - The answer partially address the concern of the user.
    - 0: No – The answers are failed to address the question.
    """)
    
    relevance = st.slider("Rate Relevance",0.0, 1.0, 0.5, step=0.1, key="relevance")
    
    
st.markdown("---")

# NEXT BUTTON SECTION
col1, col2, col3 = st.columns([1, 1, 1])

with col2:  # Center the button
    if st.button("✅ Submit & Next", type="primary", use_container_width=True):
        # Save to Google Sheets
        chicago_tz = pytz.timezone('America/Chicago')
        chicago_time = datetime.now(chicago_tz)
        sheet.append_row([
            chicago_time.strftime("%B %d, %Y at %I:%M:%S %p %Z"),
            task["id"],
            task["question"],
            task["answer"], 
            task["user_profile"],
            hazard_matching,
            other_matching,
            relevance,
            robustness
        ])
        
        st.success("Rating submitted! ✅")
        st.info("📍 Please scroll to the top of the page to see the next question.")
        
        # Move to next task
        st.session_state.task_index += 1
        
        # Rerun the app to show next question
        import time
        time.sleep(3)
    
        st.rerun()
        

# Reset button for testing (smaller, less prominent)
if st.button("🔄 Reset to First Task", help="For testing purposes"):
    st.session_state.task_index = 0
    st.rerun()
