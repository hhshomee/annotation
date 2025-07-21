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

import streamlit as st
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
import json
from io import StringIO

creds_dict = json.loads(st.secrets["gcp_credentials"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

client = gspread.authorize(creds)
SPREADSHEET_ID="1i_WpnrWuhGnAGWxDpWGh_BXHQi8ajdHHOzChGNSVpyE"
sheet = client.open_by_key(SPREADSHEET_ID).sheet1

# Load task list (questions, answers, profiles)
with open("tasks.json") as f:
    tasks = json.load(f)

if "task_index" not in st.session_state:
    st.session_state.task_index = 0

st.title("👩‍⚖️ LLM Human Evaluation Interface")
st.markdown("---")

if st.session_state.task_index < len(tasks):
    task = tasks[st.session_state.task_index]
    st.markdown(f"**📌 Question:** {task['question']}")
    st.markdown(f"**📄 Answer:** {task['answer']}")
    if task.get("user_profile"):
        st.markdown(f"**👤 User Profile:** {task['user_profile']}")

    st.markdown("---")
    specificity = st.slider("🔍 Specificity:\nHow specific and detailed is the answer, based on the question and context?", 1, 5, 3)
    relevance = st.slider("🎯 Relevance:\nHow relevant is the answer to the question?", 1, 5, 3)
    robustness = st.slider("🛡️ Robustness:\nIf the question were paraphrased, would the answer still hold?", 1, 5, 3)
    profile_awareness = st.slider("🧠 Profile Awareness:\nDoes the answer appropriately consider the user profile?", 1, 5, 3)

    if st.button("✅ Submit Rating"):
        row = [task['question'], task['answer'], task.get("user_profile", ""), specificity, relevance, robustness, profile_awareness]
        sheet.append_row(row)
        st.session_state.task_index += 1
        st.experimental_rerun()
else:
    st.success("🎉 You have completed all tasks!")
