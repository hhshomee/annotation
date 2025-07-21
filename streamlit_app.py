# import streamlit as st
# import json
# import gspread
# from datetime import datetime
# from oauth2client.service_account import ServiceAccountCredentials

# # Load tasks
# with open("tasks.json") as f:
#     tasks = json.load(f)

# # Google Sheets setup
# scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
# import json
# from io import StringIO

# creds_dict = json.loads(st.secrets["gcp_credentials"])
# creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

# client = gspread.authorize(creds)
# SPREADSHEET_ID="1i_WpnrWuhGnAGWxDpWGh_BXHQi8ajdHHOzChGNSVpyE"
# sheet = client.open_by_key(SPREADSHEET_ID).sheet1

# # Track progress
# if "task_index" not in st.session_state:
#     st.session_state.task_index = 0
# if st.session_state.task_index >= len(tasks):
#     st.write("✅ All tasks completed. Thank you for your evaluations!")
#     st.stop()
# task = tasks[st.session_state.task_index]
# st.title("LLM Human Evaluation (Pairwise)")

# # Display inputs
# st.markdown(f"**Query:** {task['query']}")
# st.markdown(f"**Ground Truth Answer:** {task['ground_truth']}")

# st.markdown("### 🅰 Response 1")
# st.markdown(task["response1"])
# if task.get("critique1"):
#     st.markdown(f"**Critique 1:** {task['critique1']}")

# st.markdown("### 🅱 Response 2")
# st.markdown(task["response2"])
# if task.get("critique2"):
#     st.markdown(f"**Critique 2:** {task['critique2']}")

# # Rating questions
# correctness = st.radio("🧠 Correctness: Is Response 1 better than Response 2?", 
#                        options=["Significantly Better", "Slightly Better", "Tie", "Slightly Worse", "Significantly Worse"], horizontal=True)

# completeness = st.radio("📚 Completeness: Is Response 1 better than Response 2?", 
#                         options=["Significantly Better", "Slightly Better", "Tie", "Slightly Worse", "Significantly Worse"], horizontal=True)

# overall = st.radio("🏆 Overall Quality: Is Response 1 better than Response 2?", 
#                    options=["Significantly Better", "Slightly Better", "Tie", "Slightly Worse", "Significantly Worse"], horizontal=True)

# # Submit button
# if st.button("✅ Submit Evaluation"):
#     sheet.append_row([
#         datetime.now().isoformat(),
#         task['id'],
#         correctness,
#         completeness,
#         overall
#     ])
#     st.success("Submission recorded ✅")
#     st.session_state.task_index += 1
#     st.rerun()
# streamlit_app.py

# streamlit_app.py

# streamlit_app.py

import streamlit as st
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

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

# DEBUG INFO - Remove these lines once working
st.write(f"🔍 DEBUG: Total tasks loaded: {len(tasks)}")
st.write(f"🔍 DEBUG: Current task index: {st.session_state.task_index}")
st.write(f"🔍 DEBUG: Task keys: {list(tasks[0].keys()) if tasks else 'No tasks'}")

# Add a reset button for testing
if st.button("🔄 Reset to First Task"):
    st.session_state.task_index = 0
    st.rerun()

# Check if all tasks are completed
if st.session_state.task_index >= len(tasks):
    st.markdown("🎉 All tasks completed! Thank you for your evaluations!")
    st.stop()

# Get current task
task = tasks[st.session_state.task_index]

# Display progress
st.title("LLM Human Evaluation")
st.markdown(f"**Progress: {st.session_state.task_index + 1} / {len(tasks)}**")

# Display task content
st.markdown(f"### 📌 Question:\n{task['question']}")
st.markdown(f"### 📄 Answer:\n{task['answer']}")
st.markdown(f"### 👤 User Profile:\n{task['user_profile']}")

# Likert ratings
specificity = st.slider("Specificity: How specific and detailed is the answer?", 1, 5, 3)
relevance = st.slider("Relevance: How relevant is the answer to the question?", 1, 5, 3)
robustness = st.slider("Robustness: Would the answer still hold if the question was paraphrased?", 1, 5, 3)
profile = st.slider("Profile Awareness: Does the answer reflect the user profile?", 1, 5, 3)

# Single submit button
if st.button("✅ Submit Rating"):
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
    
    st.success("Rating submitted!")
    
    # Move to next task
    st.session_state.task_index += 1
    
    # Rerun the app to show next question
    st.rerun()
