import streamlit as st
import pandas as pd
import plotly.express as px


class CourseFinderTab:
    """Tab 1 — Course Finder & Budget Optimizer (มุมมองผู้เรียน)"""

    def __init__(self, courses_df: pd.DataFrame, tutor_map_df: pd.DataFrame):
        self.courses = courses_df
        self.tutor_map = tutor_map_df

    def render(self, filtered: pd.DataFrame, filtered_tutor_map: pd.DataFrame) -> None:
        st.header("🎓 ค้นหาคอร์สที่คุ้มค่าที่สุด")

        # ── Results Table ────────────────────────────────────────────────────
        st.subheader(f"📋 ผลลัพธ์ ({len(filtered)} คอร์ส)")
        st.caption("คลิกหัวคอลัมน์เพื่อเรียงลำดับ — เช่น price_per_hour หรือ total_hours")

        display_cols = [
            "institute_name", "course_name", "tutor", "subject",
            "course_type", "total_hours", "price", "price_per_hour",
        ]
        st.dataframe(
            filtered[display_cols].sort_values("price_per_hour"),
            use_container_width=True,
            height=450,
        )

        # ── Tutor Comparison ─────────────────────────────────────────────────
        st.subheader("👩‍🏫 เปรียบเทียบติวเตอร์")

        tutor_detail = self.tutor_map.merge(
            self.courses[[
                "institute_name", "course_name", "subject", "course_type",
                "total_hours", "price", "price_per_hour",
            ]],
            on=["institute_name", "course_name"],
            how="left",
        )

        all_tutors = sorted(tutor_detail["individual_tutor"].dropna().unique())
        sel_tutors = st.multiselect(
            "เลือกติวเตอร์เพื่อเปรียบเทียบ (2-3 คน)",
            options=all_tutors,
            default=[],
            key="tab1_sel_tutors",
        )

        if sel_tutors:
            comp = tutor_detail[tutor_detail["individual_tutor"].isin(sel_tutors)]

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**ราคาเฉลี่ย (฿/ชม.) ของแต่ละติวเตอร์**")
                avg_price = (
                    comp.groupby("individual_tutor")["price_per_hour"]
                    .mean()
                    .reset_index()
                    .rename(columns={"price_per_hour": "avg_price_per_hour"})
                )
                fig_avg = px.bar(
                    avg_price, x="individual_tutor", y="avg_price_per_hour",
                    color="individual_tutor", text_auto=".1f",
                    labels={
                        "individual_tutor": "ติวเตอร์",
                        "avg_price_per_hour": "฿/ชม. เฉลี่ย",
                    },
                )
                fig_avg.update_layout(showlegend=False)
                st.plotly_chart(fig_avg, use_container_width=True)

            with col2:
                st.markdown("**ประเภทคอร์สของแต่ละติวเตอร์**")
                type_counts = (
                    comp.groupby(["individual_tutor", "course_type"])
                    .size()
                    .reset_index(name="count")
                )
                fig_type = px.bar(
                    type_counts, x="individual_tutor", y="count",
                    color="course_type", barmode="group", text_auto=True,
                    labels={
                        "individual_tutor": "ติวเตอร์",
                        "count": "จำนวนคอร์ส",
                        "course_type": "ประเภท",
                    },
                )
                st.plotly_chart(fig_type, use_container_width=True)

            st.dataframe(
                comp[[
                    "individual_tutor", "institute_name", "course_name",
                    "subject", "course_type", "price", "price_per_hour",
                ]].sort_values("price_per_hour"),
                use_container_width=True,
            )
        else:
            st.info("เลือกติวเตอร์ 2-3 คนจากรายการด้านบนเพื่อเปรียบเทียบ")
