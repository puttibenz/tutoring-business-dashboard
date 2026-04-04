import streamlit as st
import pandas as pd
import plotly.express as px


class TutorProfileTab:
    """Tab 4 — Tutor Deep-Dive Profile (แฟ้มประวัติติวเตอร์)"""

    def __init__(self, courses_df: pd.DataFrame, tutor_map_df: pd.DataFrame):
        # Pre-merge once at startup; Tab 4 always shows the full profile
        # regardless of sidebar filters so the tutor's complete history is visible.
        self.merged = pd.merge(
            tutor_map_df,
            courses_df,
            on=["institute_name", "course_name"],
            how="inner",
        )

    def render(self, filtered: pd.DataFrame, filtered_tutor_map: pd.DataFrame) -> None:
        st.markdown("""
        <div class="page-hero">
          <p class="eyebrow">Tutor Deep-Dive Profile</p>
          <h1>🧑‍🏫 อ่านประวัติติวเตอร์รายบุคคล</h1>
          <p class="subtitle">เจาะลึกข้อมูลติวเตอร์รายบุคคล — สอนที่ไหนบ้าง ราคาเท่าไหร่ คอร์สไหนคุ้มที่สุด</p>
        </div>
        """, unsafe_allow_html=True)
        st.divider()

        all_tutors = sorted(self.merged["individual_tutor"].dropna().unique())
        if not all_tutors:
            st.warning("ไม่พบข้อมูลติวเตอร์ในชุดข้อมูลปัจจุบัน")
            return

        selected_tutor = st.selectbox(
            "🔍 เลือกติวเตอร์",
            options=all_tutors,
            key="tab4_selectbox",
        )

        tutor_df = self.merged[self.merged["individual_tutor"] == selected_tutor].copy()

        if tutor_df.empty:
            st.info("ไม่พบข้อมูลสำหรับติวเตอร์คนนี้")
            return

        # ── KPI Row ──────────────────────────────────────────────────────────
        total_courses = len(tutor_df)
        institutes = ", ".join(sorted(tutor_df["institute_name"].unique()))
        avg_pph = tutor_df["price_per_hour"].mean()
        main_subject_series = tutor_df["subject"].mode()
        main_subject = main_subject_series.iloc[0] if not main_subject_series.empty else "—"

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("📚 จำนวนคอร์สทั้งหมด", total_courses)
        k2.metric("🏫 สถาบันที่สอน", institutes)
        k3.metric("💰 ราคาเฉลี่ย (฿/ชม.)", f"฿{avg_pph:,.1f}")
        k4.metric("📖 วิชาหลัก", main_subject)

        st.divider()

        # ── Donut Chart + Best Deal Table ────────────────────────────────────
        col_chart, col_table = st.columns([2, 1])

        with col_chart:
            st.markdown("""
            <div class="section-header">
              <div class="icon">🍩</div>
              <div>
                <h2>สัดส่วนประเภทคอร์ส</h2>
                <p>Course type distribution</p>
              </div>
            </div>
            """, unsafe_allow_html=True)
            type_counts = (
                tutor_df.groupby("course_type")
                .size()
                .reset_index(name="count")
                .sort_values("count", ascending=False)
            )
            fig_donut = px.pie(
                type_counts,
                names="course_type",
                values="count",
                hole=0.5,
                labels={"course_type": "ประเภทคอร์ส", "count": "จำนวน"},
            )
            fig_donut.update_traces(textposition="outside", textinfo="percent+label")
            fig_donut.update_layout(height=380, showlegend=True)
            st.plotly_chart(fig_donut, use_container_width=True)

        with col_table:
            st.markdown("""
            <div class="section-header">
              <div class="icon" style="background:linear-gradient(135deg,#F59E0B,#D97706);">&#127991;</div>
              <div>
                <h2>คอร์สราคาถูกสุด 3 อันดับ</h2>
                <p>Best value courses by this tutor</p>
              </div>
            </div>
            """, unsafe_allow_html=True)
            best_deals = (
                tutor_df[tutor_df["price"] > 0]
                .sort_values("price")
                .head(3)[["course_name", "institute_name", "subject",
                           "total_hours", "price", "price_per_hour"]]
                .rename(columns={
                    "course_name": "คอร์ส",
                    "institute_name": "สถาบัน",
                    "subject": "วิชา",
                    "total_hours": "ชม.",
                    "price": "ราคา (฿)",
                    "price_per_hour": "฿/ชม.",
                })
                .reset_index(drop=True)
            )
            if best_deals.empty:
                st.info("ไม่พบคอร์สที่มีราคา")
            else:
                best_deals["ราคา (฿)"] = best_deals["ราคา (฿)"].apply(
                    lambda x: f"฿{x:,.0f}"
                )
                best_deals["฿/ชม."] = best_deals["฿/ชม."].apply(
                    lambda x: f"฿{x:,.1f}"
                )
                st.dataframe(best_deals, use_container_width=True, hide_index=True)

        st.divider()

        # ── Full Course List ──────────────────────────────────────────────────
        st.markdown(f"""
        <div class="section-header" style="margin-top:1rem;">
          <div class="icon">📋</div>
          <div>
            <h2>คอร์สทั้งหมดของ {selected_tutor}
              <span class="count-badge">{total_courses} คอร์ส</span></h2>
            <p>เรียงตาม ฿/ชม. — ถูกให้แพงกว่า</p>
          </div>
        </div>
        """, unsafe_allow_html=True)
        full_cols = [
            "institute_name", "course_name", "subject",
            "course_type", "total_hours", "price", "price_per_hour",
        ]
        st.dataframe(
            tutor_df[full_cols].sort_values("price_per_hour"),
            use_container_width=True,
            height=380,
        )
