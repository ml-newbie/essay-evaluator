import streamlit as st
from essay_evaluator import workflow

st.set_page_config(page_title="Essay Evaluator", layout="wide")

st.title("📘 AI Essay Evaluator (LangGraph + OpenAI)")
st.markdown(
                "<p style='font-size:12px;'>Created by John Merwin</p>",
                unsafe_allow_html=True
            )
st.write("Write your essay or upload a file, then click **Evaluate Essay**.")

# Input section
topic = st.text_input("✏️ Essay Topic", placeholder="Enter the essay topic...")

uploaded_file = st.file_uploader("📄 Upload Essay (.txt)", type=["txt"])

essay_text = st.text_area(
    "📝 Write Your Essay",
    height=300,
    placeholder="Type your essay here..."
)

# Replace text with uploaded file
if uploaded_file:
    essay_text = uploaded_file.read().decode("utf-8")

# Evaluate button
if st.button("🚀 Evaluate Essay", type="primary"):

    if not essay_text.strip():
        st.error("Please provide an essay before evaluating.")
        st.stop()

    if not topic.strip():
        st.error("Please enter the essay topic.")
        st.stop()

    with st.spinner("Evaluating essay..."):

        # Construct initial state
        initial_state = {
            "essay_topic": topic,
            "essay_text": essay_text,
            "clarity_feedback": "",
            "analysis_feedback": "",
            "language_feedback": "",
            "final_feedback": "",
            "clarity_score": 0.0,
            "analysis_score": 0.0,
            "language_score": 0.0,
            "final_score": 0.0
        }

        result = workflow.invoke(initial_state)

    st.success("Evaluation complete!")

    # Display results
    st.header("📊 Scores")

    cols = st.columns(4)
    cols[0].metric("Clarity", round(result["clarity_score"], 2))
    cols[1].metric("Analysis", round(result["analysis_score"], 2))
    cols[2].metric("Language", round(result["language_score"], 2))
    cols[3].metric("⭐ Final Score", round(result["final_score"], 2))

    st.divider()

    st.subheader("🧠 Clarity of Thought Feedback")
    st.write(result["clarity_feedback"])

    st.subheader("🔍 Depth of Analysis Feedback")
    st.write(result["analysis_feedback"])

    st.subheader("🎨 Language & Style Feedback")
    st.write(result["language_feedback"])

    st.subheader("🏁 Final Feedback")
    st.write(result["final_feedback"])
