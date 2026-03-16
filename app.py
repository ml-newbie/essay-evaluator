import streamlit as st
from essay_evaluator import workflow
from get_keys import get_secret

APP_PASSWORD = get_secret("APP_PASSWORD")

def check_password():

    import streamlit as st

    st.markdown("""
    <style>

    /* Hide sidebar */
    [data-testid="stSidebar"] {display: none;}

    /* Page background */
    .stApp {
        background: linear-gradient(135deg, #eef2ff, #f8fafc);
    }

    /* Login card */
    .login-card {
        padding: 45px;
        border-radius: 16px;
        background: white;
        box-shadow: 0 12px 35px rgba(0,0,0,0.08);
        text-align: center;
    }

    .login-title {
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 10px;
    }

    .login-subtitle {
        color: #6b7280;
        font-size: 16px;
        margin-bottom: 25px;
    }

    </style>
    """, unsafe_allow_html=True)

    def password_entered():
        if st.session_state["password"] == APP_PASSWORD:
            st.session_state["password_correct"] = True
        else:
            st.session_state["password_correct"] = False

    # vertical spacing
    st.write("")
    st.write("")
    st.write("")
    st.write("")

    left, center, right = st.columns([3,2,3])

    with center:

        st.markdown("""
        <div class="login-card">
            <div class="login-title">🔒 AI Essay Evaluator</div>
            <div class="login-subtitle">
                Evaluate essays using AI-powered analysis
            </div>
        </div>
        """, unsafe_allow_html=True)

        password = st.text_input(
            "Password",
            type="password",
            label_visibility="collapsed",
            placeholder="Enter password",
            key="password"
        )

        login = st.button("Unlock Access", use_container_width=True)

        if login:
            password_entered()

        if "password_correct" in st.session_state:
            if not st.session_state["password_correct"]:
                st.error("Incorrect password")

    if "password_correct" not in st.session_state:
        return False
    elif not st.session_state["password_correct"]:
        return False
    else:
        return True

st.set_page_config(page_title="Essay Evaluator", layout="wide")
if not check_password():
    st.stop()


st.title("📘 AI Essay Evaluator (LangGraph + OpenAI)")
st.markdown(
    '<p style="font-size:10px; color:gray; text-align:center;">© 2026 Developed by John M. using LangGraph.</p>',
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

