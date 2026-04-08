import streamlit as st
from agent import run_agent

st.title("Content Optimization Agent")

# Inputs
topic = st.text_input("Enter Topic")
draft = st.text_area("Enter Draft")
keywords = st.text_input("Keywords (comma separated)")

# Button
if st.button("Optimize"):

    kw_list = [k.strip() for k in keywords.split(",") if k.strip()]

    result = run_agent(
        topic=topic,
        draft=draft,
        keywords=kw_list,
        verbose=False
    )

    st.subheader("Optimized Draft")
    st.text_area("Output", result["best_draft"], height=150)

    st.subheader("Score")
    st.write(result["best_reward"])

    st.subheader("Steps Taken")
    st.write(result["steps_taken"])

    st.subheader("Step-by-step Optimization")

    for step in result["log"]:
        st.write(
            f"Step {step['step']} → {step['action']} | "
            f"Reward: {step['reward']} (Δ {step['delta']:+.4f})"
        )