import sys
import os

import streamlit as st
import pandas as pd

# Allow importing the streamlit_app package from the workspace root
sys.path.insert(0, os.path.dirname(__file__))

from streamlit_app import CourseFinderTab, MarketAnalysisTab, BundleCalculatorTab, TutorProfileTab

st.set_page_config(page_title="Tutoring Business Dashboard", layout="wide")

# ── Load Data ────────────────────────────────────────────────────────────────
@st.cache_data
def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    courses = pd.read_csv("data/processed/cleaned_courses.csv")
    tutor_map = pd.read_csv("data/processed/tutor_course_mapping.csv")
    return courses, tutor_map


courses, tutor_map = load_data()

# ── Sidebar Filters ──────────────────────────────────────────────────────────
with st.sidebar:
    st.header("🔍 Smart Filters")

    sel_subjects = st.multiselect(
        "วิชา (Subject)",
        options=sorted(courses["subject"].dropna().unique()),
        default=[],
    )
    sel_institutes = st.multiselect(
        "สถาบัน (Institute)",
        options=sorted(courses["institute_name"].dropna().unique()),
        default=[],
    )
    sel_course_types = st.multiselect(
        "ประเภทคอร์ส (Course Type)",
        options=sorted(courses["course_type"].dropna().unique()),
        default=[],
    )

    price_min = float(courses["price"].min())
    price_max = float(courses["price"].max())
    price_range = st.slider(
        "งบประมาณ (Price ฿)",
        min_value=price_min,
        max_value=price_max,
        value=(price_min, price_max),
        step=100.0,
    )

# ── Apply Filters ────────────────────────────────────────────────────────────
filtered = courses.copy()
if sel_subjects:
    filtered = filtered[filtered["subject"].isin(sel_subjects)]
if sel_institutes:
    filtered = filtered[filtered["institute_name"].isin(sel_institutes)]
if sel_course_types:
    filtered = filtered[filtered["course_type"].isin(sel_course_types)]
filtered = filtered[
    (filtered["price"] >= price_range[0]) & (filtered["price"] <= price_range[1])
]

filtered_tutor_map = tutor_map.merge(
    filtered[["institute_name", "course_name"]].drop_duplicates(),
    on=["institute_name", "course_name"],
    how="inner",
)

# ── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🎓 มุมมองผู้เรียน (Course Finder & Budget Optimizer)",
    "💼 มุมมองนักวิเคราะห์ (Market & Competitor Analysis)",
    "🧮 Smart Bundle Calculator",
    "🧑‍🏫 Tutor Deep-Dive Profile",
])

course_finder_tab = CourseFinderTab(courses, tutor_map)
market_analysis_tab = MarketAnalysisTab(courses, tutor_map)
bundle_calculator_tab = BundleCalculatorTab(courses, tutor_map)
tutor_profile_tab = TutorProfileTab(courses, tutor_map)

with tab1:
    course_finder_tab.render(filtered, filtered_tutor_map)

with tab2:
    market_analysis_tab.render(filtered, filtered_tutor_map)

with tab3:
    bundle_calculator_tab.render(filtered, filtered_tutor_map)

with tab4:
    tutor_profile_tab.render(filtered, filtered_tutor_map)
