"""Streamlit application for the interactive educational / workshop experience.

Run with:

    uv run streamlit run src/revenue_prediction/ui/app.py

All data is synthetic. Nothing here contacts Azure or Fabric.
"""

from __future__ import annotations

import streamlit as st

from revenue_prediction.education import (
    get_knowledge_checks,
    get_lessons,
    grade_answer,
)
from revenue_prediction.ui.experience import (
    build_comparison_view,
    build_dataset_overview,
    facility_month_series,
    load_experience,
    run_training_experience,
)

st.set_page_config(page_title="Revenue Prediction Accelerator", layout="wide")


@st.cache_resource(show_spinner=False)
def _load(environment: str):
    return load_experience(environment)


def _sidebar() -> str:
    st.sidebar.title("Revenue Prediction Accelerator")
    st.sidebar.caption("Healthcare facility net-revenue prediction - synthetic data only.")
    env = st.sidebar.selectbox("Config environment", ["dev", "test", "prod"], index=0)
    st.sidebar.warning(
        "All data and outputs are synthetic and illustrative. Review with "
        "qualified finance, data, security, privacy, compliance, and "
        "operational stakeholders before any production use."
    )
    return env


def _overview(state) -> None:
    st.header("1. Dataset overview")
    overview = build_dataset_overview(state)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rows", overview["rows"])
    c2.metric("Facilities", len(overview["facilities"]))
    c3.metric("Months", len(overview["months"]))
    c4.metric("Avg month-end net revenue", f"${overview['target_mean']:,.0f}")

    facility = st.selectbox("Inspect a facility", overview["facilities"])
    series = facility_month_series(state, facility)
    st.line_chart(series.set_index("accounting_month"))
    st.dataframe(state.data.head(50), width="stretch")


def _training(state) -> None:
    st.header("2. Train & compare (code-first, offline)")
    if st.button("Run local training pipeline"):
        with st.spinner("Training candidates on a time-aware split..."):
            output = run_training_experience(state)
        table = build_comparison_view(output)
        st.success(f"Champion: {output.selection.champion}")
        st.dataframe(table, width="stretch")
        st.bar_chart(table.set_index("model")["mae"])


def _education() -> None:
    st.header("3. Learn")
    for lesson in get_lessons():
        with st.expander(f"{lesson.title} - {lesson.summary}"):
            st.write(lesson.body)
            if lesson.references:
                st.caption("References: " + ", ".join(lesson.references))


def _knowledge_checks() -> None:
    st.header("4. Knowledge checks")
    score = 0
    total = 0
    for check in get_knowledge_checks():
        total += 1
        choice = st.radio(check.question, check.options, index=None, key=check.key)
        if choice is not None:
            chosen_index = check.options.index(choice)
            if grade_answer(check, chosen_index):
                st.success("Correct. " + check.explanation)
                score += 1
            else:
                st.error("Not quite. " + check.explanation)
    st.info(f"Score: {score} / {total}")


def main() -> None:
    env = _sidebar()
    state = _load(env)
    tabs = st.tabs(["Overview", "Train & Compare", "Learn", "Knowledge Checks"])
    with tabs[0]:
        _overview(state)
    with tabs[1]:
        _training(state)
    with tabs[2]:
        _education()
    with tabs[3]:
        _knowledge_checks()


if __name__ == "__main__":
    main()
