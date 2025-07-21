import streamlit as st
import json
import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# Load tasks
with open("tasks.json") as f:
    tasks = json.load(f)

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("google-credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("LLM_Human_Eval_Results").sheet1

# Track progress
if "task_index" not in st.session_state:
    st.session_state.task_index = 0

task = tasks[st.session_state.task_index]
st.title("LLM Human Evaluation (Pairwise)")

# Display inputs
st.markdown(f"**Query:** {task['query']}")
st.markdown(f"**Ground Truth Answer:** {task['ground_truth']}")

st.markdown("### 🅰 Response 1")
st.markdown(task["response1"])
if task.get("critique1"):
    st.markdown(f"**Critique 1:** {task['critique1']}")

st.markdown("### 🅱 Response 2")
st.markdown(task["response2"])
if task.get("critique2"):
    st.markdown(f"**Critique 2:** {task['critique2']}")

# Rating questions
correctness = st.radio("🧠 Correctness: Is Response 1 better than Response 2?", 
                       options=["Significantly Better", "Slightly Better", "Tie", "Slightly Worse", "Significantly Worse"], horizontal=True)

completeness = st.radio("📚 Completeness: Is Response 1 better than Response 2?", 
                        options=["Significantly Better", "Slightly Better", "Tie", "Slightly Worse", "Significantly Worse"], horizontal=True)

overall = st.radio("🏆 Overall Quality: Is Response 1 better than Response 2?", 
                   options=["Significantly Better", "Slightly Better", "Tie", "Slightly Worse", "Significantly Worse"], horizontal=True)

# Submit button
if st.button("✅ Submit Evaluation"):
    sheet.append_row([
        datetime.now().isoformat(),
        task['id'],
        correctness,
        completeness,
        overall
    ])
    st.success("Submission recorded ✅")
    st.session_state.task_index += 1
    st.experimental_rerun()
