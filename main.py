import sys
import os

import streamlit as st
import pandas as pd

# Allow importing the streamlit_app package from the workspace root
sys.path.insert(0, os.path.dirname(__file__))

from streamlit_app import CourseFinderTab, MarketAnalysisTab, BundleCalculatorTab, TutorProfileTab

st.set_page_config(
    page_title="Tutoring Business Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Inject Design System CSS ──────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
@import url('https://fonts.googleapis.com/icon?family=Material+Icons+Sharp');

/* Fix sidebar collapse button icon rendering */
[data-testid="stSidebarCollapsedControl"] span,
[data-testid="stSidebarContent"] button span,
button[kind="header"] span,
.st-emotion-cache-1rtdyuf span,
span.material-icons-sharp {
    font-family: 'Material Icons Sharp' !important;
    font-size: 20px !important;
    font-style: normal !important;
    font-weight: normal !important;
    line-height: 1 !important;
    letter-spacing: normal !important;
    text-transform: none !important;
    display: inline-block !important;
    white-space: nowrap !important;
    word-wrap: normal !important;
    -webkit-font-feature-settings: 'liga' !important;
    font-feature-settings: 'liga' !important;
}

/* ── Base Typography & Force Light Mode ─────────────────────────── */
html, body, .stApp, .stApp * {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif !important;
}
.stApp { background-color: #F8FAFC !important; color: #1E293B !important; }

/* Force all main-area text to be dark so it stays visible on white bg */
[data-testid="stAppViewContainer"] label,
[data-testid="stAppViewContainer"] p,
[data-testid="stAppViewContainer"] span:not([data-baseweb]),
[data-testid="stAppViewContainer"] div[class*="stMarkdown"] {
    color: #1E293B !important;
}
/* Widget labels (multiselect, selectbox, radio, slider, etc.) */
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] p,
.stSelectbox label, .stMultiSelect label,
.stSlider label, .stRadio label,
.stTextInput label, .stToggle label {
    color: #334155 !important;
}
/* Metric delta / general fine text */
[data-testid="stMetricDelta"] { color: inherit !important; }

/* ── Top Bar ────────────────────────────────────────────────────── */
[data-testid="stHeader"] {
    background: rgba(248,250,252,0.92) !important;
    backdrop-filter: blur(12px) !important;
    border-bottom: 1px solid #E2E8F0 !important;
}

/* ── Main Block Container (8px grid) ───────────────────────────── */
.main .block-container {
    padding: 2rem 2.5rem 3rem !important;
    max-width: 1440px !important;
}

/* ── Sidebar ────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0F172A 0%, #1E293B 100%) !important;
    border-right: 1px solid #1E293B !important;
}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p {
    color: #CBD5E1 !important;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #F1F5F9 !important; }
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: rgba(255,255,255,0.06) !important;
    border-color: #334155 !important;
    border-radius: 8px !important;
    color: #E2E8F0 !important;
    transition: border-color .15s ease !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] > div:hover {
    border-color: #3B82F6 !important;
}
[data-testid="stSidebar"] [data-baseweb="tag"] {
    background: rgba(59,130,246,.18) !important;
    border-color: rgba(59,130,246,.35) !important;
}
[data-testid="stSidebar"] [data-baseweb="tag"] span { color: #93C5FD !important; }
[data-testid="stSidebar"] hr { border-color: #334155 !important; }

/* ── Tabs (pill style) ──────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: #F1F5F9 !important;
    border-radius: 12px !important;
    padding: 4px !important;
    gap: 2px !important;
    border-bottom: none !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    padding: 10px 18px !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    color: #64748B !important;
    background: transparent !important;
    border: none !important;
    transition: color .15s ease, background .15s ease !important;
    white-space: nowrap !important;
}
.stTabs [data-baseweb="tab"]:hover:not([aria-selected="true"]) {
    background: rgba(255,255,255,.65) !important;
    color: #334155 !important;
}
.stTabs [aria-selected="true"] {
    background: #FFFFFF !important;
    box-shadow: 0 1px 4px rgba(0,0,0,.08), 0 0 0 1px rgba(0,0,0,.04) !important;
    color: #1D4ED8 !important;
    font-weight: 600 !important;
}
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.5rem !important; }

/* ── Metric Cards ───────────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 12px !important;
    padding: 1.25rem 1.5rem !important;
    box-shadow: 0 1px 2px rgba(0,0,0,.04) !important;
    transition: box-shadow .2s ease, transform .2s ease !important;
}
[data-testid="stMetric"]:hover {
    box-shadow: 0 8px 24px rgba(0,0,0,.08) !important;
    transform: translateY(-2px) !important;
}
[data-testid="stMetricLabel"] > div {
    font-size: .7rem !important;
    font-weight: 600 !important;
    letter-spacing: .07em !important;
    text-transform: uppercase !important;
    color: #64748B !important;
}
[data-testid="stMetricValue"] > div {
    font-size: 1.5rem !important;
    font-weight: 700 !important;
    color: #0F172A !important;
    letter-spacing: -.02em !important;
}
[data-testid="stMetricDelta"] > div {
    font-size: .75rem !important;
    font-weight: 500 !important;
}

/* ── DataFrames ─────────────────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border-radius: 12px !important;
    overflow: hidden !important;
    border: 1px solid #E2E8F0 !important;
    box-shadow: 0 1px 2px rgba(0,0,0,.04) !important;
}

/* ── Form Controls ──────────────────────────────────────────────── */
[data-baseweb="select"] > div:first-child {
    border-radius: 8px !important;
    border-color: #CBD5E1 !important;
    transition: border-color .15s ease, box-shadow .15s ease !important;
}
[data-baseweb="select"] > div:first-child:hover { border-color: #94A3B8 !important; }
[data-baseweb="select"] > div:focus-within {
    border-color: #3B82F6 !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,.15) !important;
}
[data-baseweb="input"] > div { border-radius: 8px !important; border-color: #CBD5E1 !important; }

/* ── Slider ─────────────────────────────────────────────────────── */
[data-testid="stSlider"] [role="slider"] {
    background: #2563EB !important;
    border-color: #2563EB !important;
}

/* ── Divider ────────────────────────────────────────────────────── */
[data-testid="stDivider"] hr, hr { border-color: #E2E8F0 !important; margin: 1.5rem 0 !important; }

/* ── Alert Boxes ────────────────────────────────────────────────── */
[data-testid="stAlert"] { border-radius: 10px !important; }

/* ── Caption ────────────────────────────────────────────────────── */
[data-testid="stCaptionContainer"] p, .stCaption { color: #94A3B8 !important; font-size: .8rem !important; }

/* ── Buttons ────────────────────────────────────────────────────── */
.stButton > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all .2s ease !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg,#3B82F6,#1D4ED8) !important;
    border: none !important;
    box-shadow: 0 1px 3px rgba(59,130,246,.25) !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 14px rgba(59,130,246,.4) !important;
}
.stButton > button[kind="secondary"] {
    border-color: #CBD5E1 !important;
    color: #475569 !important;
}
.stButton > button[kind="secondary"]:hover {
    border-color: #94A3B8 !important;
    color: #1E293B !important;
    transform: translateY(-1px) !important;
}

/* ── Markdown headings ──────────────────────────────────────────── */
.stMarkdown h1 {
    font-size: 1.75rem !important; font-weight: 800 !important;
    color: #0F172A !important; letter-spacing: -.03em !important; line-height: 1.25 !important;
}
.stMarkdown h2 {
    font-size: 1.125rem !important; font-weight: 700 !important;
    color: #1E293B !important; letter-spacing: -.02em !important;
}
.stMarkdown h3 {
    font-size: .9375rem !important; font-weight: 600 !important; color: #334155 !important;
}
.stMarkdown strong { color: #1E293B !important; font-weight: 600 !important; }

/* ── Custom Utility Classes (used via st.markdown) ──────────────── */
.page-hero {
    padding-bottom: 1.25rem;
    border-bottom: 1px solid #E2E8F0;
    margin-bottom: 1.5rem;
}
.page-hero .eyebrow {
    font-size: .68rem; font-weight: 700; letter-spacing: .1em;
    text-transform: uppercase; color: #3B82F6; margin-bottom: 6px;
}
.page-hero h1 {
    font-size: 1.625rem !important; font-weight: 800 !important;
    color: #0F172A !important; letter-spacing: -.03em !important;
    line-height: 1.2 !important; margin: 0 !important;
}
.page-hero .subtitle {
    font-size: .875rem; color: #64748B; margin-top: 6px;
}
.section-header {
    display: flex; align-items: center; gap: 10px;
    margin-bottom: 1rem; margin-top: .25rem;
    padding-bottom: .75rem; border-bottom: 2px solid #F1F5F9;
}
.section-header .icon {
    width: 32px; height: 32px;
    background: linear-gradient(135deg,#3B82F6,#1D4ED8);
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem; flex-shrink: 0;
}
.section-header h2 {
    font-size: 1rem !important; font-weight: 700 !important;
    color: #1E293B !important; margin: 0 !important; letter-spacing: -.02em !important;
}
.section-header p {
    font-size: .75rem !important; color: #94A3B8 !important; margin: 1px 0 0 !important;
}
.count-badge {
    display: inline-flex; align-items: center;
    background: #EFF6FF; color: #1D4ED8;
    font-size: .68rem; font-weight: 700; letter-spacing: .04em;
    padding: 2px 8px; border-radius: 999px;
    border: 1px solid #BFDBFE; margin-left: 6px; vertical-align: middle;
}
.app-header {
    display: flex; align-items: flex-start; justify-content: space-between;
    padding-bottom: 1.5rem; border-bottom: 1px solid #E2E8F0; margin-bottom: 1.5rem;
}
.app-header .brand-eyebrow {
    font-size: .65rem; font-weight: 700; letter-spacing: .1em;
    text-transform: uppercase; color: #3B82F6; margin-bottom: 6px;
}
.app-header h1 {
    font-size: 1.875rem !important; font-weight: 800 !important;
    color: #0F172A !important; letter-spacing: -.035em !important;
    line-height: 1.15 !important; margin: 0 !important;
}
.app-header .tagline { font-size: .875rem; color: #64748B; margin-top: 8px; }
.app-header .stat-box { text-align: right; flex-shrink: 0; padding-left: 2rem; }
.app-header .stat-box .stat-label {
    font-size: .62rem; font-weight: 600; letter-spacing: .09em;
    text-transform: uppercase; color: #94A3B8; margin-bottom: 2px;
}
.app-header .stat-box .stat-value {
    font-size: 2.25rem; font-weight: 800;
    color: #0F172A; letter-spacing: -.04em; line-height: 1;
}
.sidebar-nav-label {
    font-size: .62rem; font-weight: 700; letter-spacing: .12em;
    text-transform: uppercase; color: #475569; margin-bottom: 4px;
}
.sidebar-nav-title {
    font-size: 1.0625rem; font-weight: 700; color: #F1F5F9;
    display: flex; align-items: center; gap: 8px; margin-bottom: 1.25rem;
}
</style>
""", unsafe_allow_html=True)

# ── Load Data ────────────────────────────────────────────────────────────────
@st.cache_data
def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    courses = pd.read_csv("data/processed/cleaned_courses.csv")
    tutor_map = pd.read_csv("data/processed/tutor_course_mapping.csv")
    return courses, tutor_map


courses, tutor_map = load_data()

# ── App Hero Header ───────────────────────────────────────────────────────────
st.markdown(f"""
<div class="app-header">
  <div>
    <p class="brand-eyebrow">Tutoring Market Intelligence</p>
    <h1>คอร์สเรียนติวเตอร์ไทย</h1>
    <p class="tagline">วิเคราะห์ตลาดคอร์สติวเตอร์ไทยครบวงจร — ค้นหา เปรียบเทียบ และเลือกได้อย่างชาญฉลาด</p>
  </div>
  <div class="stat-box">
    <p class="stat-label">Total Courses</p>
    <p class="stat-value">{len(courses):,}</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar Filters ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 0 0.25rem 1rem;">
      <p class="sidebar-nav-label">Dashboard</p>
      <div class="sidebar-nav-title">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none"
             stroke="#3B82F6" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
        </svg>
        Smart Filters
      </div>
    </div>
    """, unsafe_allow_html=True)

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

    has_scope_col = "course_scope" in courses.columns
    hide_chapters = False
    if has_scope_col:
        st.divider()
        hide_chapters = st.toggle(
            "🔖 ซ่อนคอร์สแยกบท",
            value=False,
            help="ซ่อนคอร์สเนื้อหาแยกบท (Chapter) แสดงเฉพาะ Full Course",
        )

# ── Apply Filters ────────────────────────────────────────────────────────────
filtered = courses.copy()
if sel_subjects:
    filtered = filtered[filtered["subject"].isin(sel_subjects)]
if sel_institutes:
    filtered = filtered[filtered["institute_name"].isin(sel_institutes)]
if sel_course_types:
    filtered = filtered[filtered["course_type"].isin(sel_course_types)]
if hide_chapters and "course_scope" in filtered.columns:
    filtered = filtered[filtered["course_scope"] == "Full Course (คอร์สเตรียมสอบ/รวมเทอม)"]
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
    "🎓  Course Finder",
    "💼  Market Analysis",
    "🧮  Bundle Calculator",
    "🧑‍🏫  Tutor Profile",
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
