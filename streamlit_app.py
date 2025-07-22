# streamlit_app.py

import streamlit as st
import json
import gspread
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
st.markdown(f"**Progress: {st.session_state.task_index + 1} / {len(tasks)}**")

st.markdown("""
### 📋 Instructions
Please carefully review the question, user profile, and answer provided. Then examine the knowledge sources that were used to generate the response. 
Rate the quality of the answer across four key dimensions using the scales below. Your evaluation will help improve AI response quality.
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
    **🔍 Specificity (1-5)**  
    *How specific and detailed is the answer?*  
    - 1: Very vague, lacks detail
    - 3: Moderate level of detail  
    - 5: Highly specific with concrete details
    """)
    
    specificity = st.slider("Rate Specificity", 1, 5, 3, key="specificity")
    
    st.markdown("""
    **💪 Robustness (1-5)**  
    *Would the answer still hold if the question was paraphrased?*  
    - 1: Answer is very fragile to rewording
    - 3: Moderately robust to variations
    - 5: Answer works well for similar questions
    """)
    
    robustness = st.slider("Rate Robustness", 1, 5, 3, key="robustness")

with metrics_col2:
    st.markdown("""
    **🎯 Relevance (1-5)**  
    *How relevant is the answer to the question?*  
    - 1: Completely off-topic
    - 3: Partially addresses the question
    - 5: Directly and fully addresses the question
    """)
    
    relevance = st.slider("Rate Relevance", 1, 5, 3, key="relevance")
    
    st.markdown("""
    **👥 Profile Awareness (1-5)**  
    *Does the answer reflect the user profile?*  
    - 1: Ignores user context completely
    - 3: Some consideration of user background
    - 5: Perfectly tailored to user's situation
    """)
    
    profile = st.slider("Rate Profile Awareness", 1, 5, 3, key="profile")

st.markdown("---")

# NEXT BUTTON SECTION
col1, col2, col3 = st.columns([1, 1, 1])

with col2:  # Center the button
    if st.button("✅ Submit & Next", type="primary", use_container_width=True):
        # Save to Google Sheets
        sheet.append_row([
            task["question"],
            task["answer"], 
            task["user_profile"],
            specificity,
            relevance,
            robustness,
            profile
        ])
        
        st.success("Rating submitted! ✅")
        
        # Move to next task
        st.session_state.task_index += 1
        
        # Rerun the app to show next question
        st.rerun()

# Reset button for testing (smaller, less prominent)
if st.button("🔄 Reset to First Task", help="For testing purposes"):
    st.session_state.task_index = 0
    st.rerun()
