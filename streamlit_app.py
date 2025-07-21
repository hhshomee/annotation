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

with open("tasks.json", "r") as f:
    tasks = json.load(f)

if "task_index" not in st.session_state:
    st.session_state.task_index = 0

# Get current task safely
if st.session_state.task_index < len(tasks):
    task = tasks[st.session_state.task_index]

    st.title("LLM Human Evaluation")

    st.markdown(f"### 📌 Question:\n{task['question']}")
    st.markdown(f"### 📄 Answer:\n{task['answer']}")
    st.markdown(f"### 👤 User Profile:\n{task['user_profile']}")

    # Likert ratings
    specificity = st.slider("Specificity: How specific and detailed is the answer?", 1, 5, 3)
    relevance = st.slider("Relevance: How relevant is the answer to the question?", 1, 5, 3)
    robustness = st.slider("Robustness: Would the answer still hold if the question was paraphrased?", 1, 5, 3)
    profile = st.slider("Profile Awareness: Does the answer reflect the user profile?", 1, 5, 3)

    if st.button("✅ Submit Rating"):
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
        if st.session_state.task_index + 1 < len(tasks):
            st.session_state.task_index += 1
            st.experimental_rerun()
        else:
            st.markdown("🎉 All tasks completed!")
else:
    st.markdown("🎉 All tasks completed!")
