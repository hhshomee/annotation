import streamlit as st
import json

# Load the data
with open("data.json") as f:
    tasks = json.load(f)

st.title("LLM Human Evaluation")

# Create session state for tracking annotations
if "annotations" not in st.session_state:
    st.session_state.annotations = {}

for item in tasks:
    st.markdown("---")
    st.markdown(f"**Prompt:** {item['prompt']}")
    st.markdown(f"**Response:** {item['response']}")

    rel = st.slider(f"Relevance (Task {item['id']})", 1, 5, key=f"rel_{item['id']}")
    fact = st.slider(f"Factuality (Task {item['id']})", 1, 5, key=f"fact_{item['id']}")
    comment = st.text_area(f"Comments (Task {item['id']})", key=f"com_{item['id']}")

    st.session_state.annotations[item['id']] = {
        "relevance": rel,
        "factuality": fact,
        "comment": comment
    }

st.markdown("---")
if st.button("Export Annotations"):
    st.download_button(
        label="📥 Download JSON",
        data=json.dumps(st.session_state.annotations, indent=2),
        file_name="annotations.json",
        mime="application/json"
    )
