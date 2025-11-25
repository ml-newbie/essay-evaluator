# evaluator.py

import os
from typing import TypedDict
from pydantic import BaseModel, Field

# -------------------------------------------------------------------------
# LOAD API KEY (Works both locally and on Streamlit Cloud)
# -------------------------------------------------------------------------
def load_api_key():
    """
    Use Streamlit secrets on Cloud.
    Use .env locally.
    """
    # 1. Streamlit Cloud
    try:
        import streamlit as st
        if "OPENAI_API_KEY" in st.secrets:
            os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
            return
    except:
        pass

    # 2. Local .env
    from dotenv import load_dotenv
    load_dotenv()

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("No OPENAI_API_KEY found in .env or Streamlit Secrets.")

load_api_key()

# -------------------------------------------------------------------------
# Imports AFTER loading API key
# -------------------------------------------------------------------------
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI

# -------------------------------------------------------------------------
# Structured Output Schema
# -------------------------------------------------------------------------
class EssaySchema(BaseModel):
    feedback: str = Field(description="Detailed feedback on the essay.")
    score: float = Field(description="Score between 0 and 10.", ge=0.0, le=10.0)

model = ChatOpenAI(model="gpt-4o", temperature=0.7)

# -------------------------------------------------------------------------
# State Definition
# -------------------------------------------------------------------------
class EssayState(TypedDict):
    essay_topic: str
    essay_text: str

    clarity_feedback: str
    analysis_feedback: str
    language_feedback: str
    final_feedback: str

    clarity_score: float
    analysis_score: float
    language_score: float
    final_score: float


# -------------------------------------------------------------------------
# Node: Clarity Feedback
# -------------------------------------------------------------------------
def generate_clarity_feedback(state: EssayState):
    essay_text = state["essay_text"]

    prompt = f"""
Provide clarity-of-thought feedback for the essay below.
Your response MUST include:
- A detailed but concise critique (max 300 words)
- A numerical clarity score between 0–10

Essay:
{essay_text}
"""

    llm = model.with_structured_output(EssaySchema)
    result = llm.invoke(prompt)

    return {
        "clarity_feedback": result.feedback,
        "clarity_score": result.score
    }


# -------------------------------------------------------------------------
# Node: Depth of Analysis Feedback
# -------------------------------------------------------------------------
def generate_analysis_feedback(state: EssayState):
    essay_text = state["essay_text"]

    prompt = f"""
Provide depth-of-analysis feedback for the essay below.
Your response MUST include:
- A detailed but concise critique (max 300 words)
- A numerical analysis score between 0–10

Essay:
{essay_text}
"""

    llm = model.with_structured_output(EssaySchema)
    result = llm.invoke(prompt)

    return {
        "analysis_feedback": result.feedback,
        "analysis_score": result.score
    }


# -------------------------------------------------------------------------
# Node: Language Feedback
# -------------------------------------------------------------------------
def generate_language_feedback(state: EssayState):
    essay_text = state["essay_text"]

    prompt = f"""
Provide language & style feedback for the essay below.
Your response MUST include:
- A detailed but concise critique (max 300 words)
- A numerical language score between 0–10

Essay:
{essay_text}
"""

    llm = model.with_structured_output(EssaySchema)
    result = llm.invoke(prompt)

    return {
        "language_feedback": result.feedback,
        "language_score": result.score
    }


# -------------------------------------------------------------------------
# Node: Final Feedback (runs once)
# -------------------------------------------------------------------------
def generate_final_feedback(state: EssayState):
    prompt = f"""
Synthesize the final feedback for this essay using the following inputs:

Clarity Feedback:
{state['clarity_feedback']}

Depth of Analysis Feedback:
{state['analysis_feedback']}

Language Feedback:
{state['language_feedback']}

Clarity Score: {state['clarity_score']}
Analysis Score: {state['analysis_score']}
Language Score: {state['language_score']}

Your tasks:
1. Provide a single final narrative feedback (≤ 300 words).
2. Compute the final score as the AVERAGE of the three scores.
"""

    final_score = (
        state["clarity_score"]
        + state["analysis_score"]
        + state["language_score"]
    ) / 3

    llm = model.with_structured_output(EssaySchema)
    result = llm.invoke(prompt)

    return {
        "final_feedback": result.feedback,
        "final_score": final_score
    }


# -------------------------------------------------------------------------
# Build LangGraph Workflow
# -------------------------------------------------------------------------
graph = StateGraph(EssayState)

graph.add_node("clarity", generate_clarity_feedback)
graph.add_node("analysis", generate_analysis_feedback)
graph.add_node("language", generate_language_feedback)
graph.add_node("final", generate_final_feedback)

# Run three feedback nodes in parallel
graph.add_edge(START, "clarity")
graph.add_edge(START, "analysis")
graph.add_edge(START, "language")

# Final node only after all three are completed
graph.add_edge("clarity", "final")
graph.add_edge("analysis", "final")
graph.add_edge("language", "final")

graph.add_edge("final", END)

workflow = graph.compile()


# -------------------------------------------------------------------------
# Optional: Test the workflow when running this file directly
# -------------------------------------------------------------------------
if __name__ == "__main__":
    print("\nRunning evaluator test...\n")

    sample_essay = """
Artificial Intelligence has become deeply embedded in modern education.
While it offers benefits such as personalized learning and automated grading,
it also introduces several downsides. Students may become overly reliant on AI
tools, reducing critical thinking. Additionally, AI-generated content makes it
harder for educators to assess true student ability. Privacy concerns also arise
due to the amount of data collected to train educational systems. Overall,
AI can be helpful, but only when balanced with human-centered instruction.
"""

    initial_state = {
        "essay_topic": "The downsides of AI in modern education",
        "essay_text": sample_essay.strip(),
        "clarity_feedback": "",
        "analysis_feedback": "",
        "language_feedback": "",
        "final_feedback": "",
        "clarity_score": 0.0,
        "analysis_score": 0.0,
        "language_score": 0.0,
        "final_score": 0.0,
    }

    print("Invoking workflow...\n")
    result = workflow.invoke(initial_state)

    print("=== SCORES ===")
    print("Clarity Score:", result["clarity_score"])
    print("Analysis Score:", result["analysis_score"])
    print("Language Score:", result["language_score"])
    print("FINAL Score:", result["final_score"])

    print("\n=== FEEDBACK ===")
    print("\n-- Clarity Feedback --")
    print(result["clarity_feedback"])

    print("\n-- Analysis Feedback --")
    print(result["analysis_feedback"])

    print("\n-- Language Feedback --")
    print(result["language_feedback"])

    print("\n-- FINAL FEEDBACK --")
    print(result["final_feedback"])

    print("\nTest complete.\n")
