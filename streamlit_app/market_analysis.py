import streamlit as st
import pandas as pd
import plotly.express as px


class MarketAnalysisTab:
    """Tab 2 — Market & Competitor Analysis (มุมมองนักวิเคราะห์)"""

    def __init__(self, courses_df: pd.DataFrame, tutor_map_df: pd.DataFrame):
        self.courses = courses_df
        self.tutor_map = tutor_map_df

    def render(self, filtered: pd.DataFrame, filtered_tutor_map: pd.DataFrame) -> None:
        st.markdown("""
        <div class="page-hero">
          <p class="eyebrow">Market &amp; Competitor Analysis</p>
          <h1>💼 วิเคราะห์ตลาดและคู่แข่ง</h1>
          <p class="subtitle">ภาพรวมราคา บทวิเคราะห์กลยุทธ์แข่งขัน และติดตาม Star Tutor Risk</p>
        </div>
        """, unsafe_allow_html=True)

        # ── KPI Metrics ──────────────────────────────────────────────────────
        avg_market_price = filtered["price"].mean()
        avg_market_pph = filtered["price_per_hour"].mean()

        most_competitive_subject = filtered.groupby("subject").size().idxmax()
        most_competitive_count = filtered.groupby("subject").size().max()

        most_expensive_subject = (
            filtered.groupby("subject")["price_per_hour"].mean().idxmax()
        )
        most_expensive_pph = (
            filtered.groupby("subject")["price_per_hour"].mean().max()
        )

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("ราคาเฉลี่ยตลาด", f"฿{avg_market_price:,.0f}")
        k2.metric("฿/ชม. เฉลี่ยตลาด", f"฿{avg_market_pph:,.1f}")
        k3.metric("วิชาแข่งขันสูงสุด", most_competitive_subject,
                  f"{most_competitive_count} คอร์ส")
        k4.metric("วิชาแพงสุด (฿/ชม.)", most_expensive_subject,
                  f"฿{most_expensive_pph:,.1f}/ชม.")

        st.divider()

        # ── Price & Hours by Institute ────────────────────────────────────────
        st.markdown("""
        <div class="section-header">
          <div class="icon">📊</div>
          <div>
            <h2>เปรียบเทียบราคาและจำนวนชั่วโมงแต่ละสถาบัน</h2>
            <p>Average vs. Median เปรียบรายสถาบัน</p>
          </div>
        </div>
        """, unsafe_allow_html=True)

        inst_stats = (
            filtered.groupby("institute_name")
            .agg(
                avg_price=("price", "mean"),
                median_price=("price", "median"),
                avg_hours=("total_hours", "mean"),
                median_hours=("total_hours", "median"),
                avg_pph=("price_per_hour", "mean"),
                total_courses=("course_name", "count"),
            )
            .reset_index()
        )

        c1, c2 = st.columns(2)

        with c1:
            fig_price = px.bar(
                inst_stats, x="institute_name", y=["avg_price", "median_price"],
                barmode="group", text_auto=",.0f",
                labels={
                    "institute_name": "สถาบัน",
                    "value": "ราคา (฿)",
                    "variable": "ตัวชี้วัด",
                },
                color_discrete_map={
                    "avg_price": "#636EFA",
                    "median_price": "#EF553B",
                },
            )
            fig_price.for_each_trace(lambda t: t.update(
                name="ราคาเฉลี่ย" if t.name == "avg_price" else "ราคามัธยฐาน"
            ))
            fig_price.update_layout(height=420, title="ราคา (เฉลี่ย vs มัธยฐาน)")
            st.plotly_chart(fig_price, use_container_width=True)

        with c2:
            fig_hours = px.bar(
                inst_stats, x="institute_name", y=["avg_hours", "median_hours"],
                barmode="group", text_auto=".1f",
                labels={
                    "institute_name": "สถาบัน",
                    "value": "ชั่วโมง",
                    "variable": "ตัวชี้วัด",
                },
                color_discrete_map={
                    "avg_hours": "#00CC96",
                    "median_hours": "#FFA15A",
                },
            )
            fig_hours.for_each_trace(lambda t: t.update(
                name="ชม.เฉลี่ย" if t.name == "avg_hours" else "ชม.มัธยฐาน"
            ))
            fig_hours.update_layout(height=420, title="จำนวนชั่วโมง (เฉลี่ย vs มัธยฐาน)")
            st.plotly_chart(fig_hours, use_container_width=True)

        # ── Box Plots ─────────────────────────────────────────────────────────
        st.markdown("""
        <div class="section-header" style="margin-top:1rem;">
          <div class="icon">📦</div>
          <div>
            <h2>การกระจายราคาของแต่ละสถาบัน</h2>
            <p>Price distribution per institute (outliers marked)</p>
          </div>
        </div>
        """, unsafe_allow_html=True)
        fig_box_price = px.box(
            filtered, x="institute_name", y="price", color="institute_name",
            points="outliers",
            labels={"institute_name": "สถาบัน", "price": "ราคา (฿)"},
        )
        fig_box_price.update_layout(height=420, showlegend=False)
        st.plotly_chart(fig_box_price, use_container_width=True)

        st.markdown("""
        <div class="section-header" style="margin-top:1rem;">
          <div class="icon">⏱️</div>
          <div>
            <h2>การกระจายจำนวนชั่วโมงของแต่ละสถาบัน</h2>
            <p>Hours distribution per institute</p>
          </div>
        </div>
        """, unsafe_allow_html=True)
        fig_box_hours = px.box(
            filtered, x="institute_name", y="total_hours", color="institute_name",
            points="outliers",
            labels={"institute_name": "สถาบัน", "total_hours": "ชั่วโมงเรียน"},
        )
        fig_box_hours.update_layout(height=420, showlegend=False)
        st.plotly_chart(fig_box_hours, use_container_width=True)

        st.divider()

        # ── Course Type by Institute ──────────────────────────────────────────
        st.markdown("""
        <div class="section-header">
          <div class="icon">🎯</div>
          <div>
            <h2>ประเภทคอร์สของแต่ละสถาบัน</h2>
            <p>Course type breakdown by institute</p>
          </div>
        </div>
        """, unsafe_allow_html=True)

        ct_by_inst = (
            filtered.groupby(["institute_name", "course_type"])
            .size()
            .reset_index(name="count")
        )
        ct_by_inst["pct"] = ct_by_inst.groupby("institute_name")["count"].transform(
            lambda x: x / x.sum() * 100
        )

        fig_bar = px.bar(
            ct_by_inst, x="institute_name", y="count", color="course_type",
            barmode="group", text_auto=True,
            hover_data={"pct": ":.1f"},
            labels={
                "institute_name": "สถาบัน",
                "count": "จำนวนคอร์ส",
                "course_type": "ประเภทคอร์ส",
                "pct": "% ของสถาบัน",
            },
        )
        fig_bar.update_layout(height=450)
        st.plotly_chart(fig_bar, use_container_width=True)

        # ── Scatter: Bulk Pricing Strategy ───────────────────────────────────
        st.markdown("""
        <div class="section-header" style="margin-top:1rem;">
          <div class="icon">🔬</div>
          <div>
            <h2>Scatter Plot — กลยุทธ์ตั้งราคา (Bulk Pricing)</h2>
            <p>ความสัมพันธ์ระหว่างจำนวนชั่วโมง ราคา และสถาบัน</p>
          </div>
        </div>
        """, unsafe_allow_html=True)

        scatter_subjects = st.multiselect(
            "กรองวิชาที่ต้องการดู",
            options=sorted(filtered["subject"].dropna().unique()),
            default=[],
            key="tab2_scatter_subjects",
        )

        scatter_data = filtered.copy()
        if scatter_subjects:
            scatter_data = scatter_data[scatter_data["subject"].isin(scatter_subjects)]

        fig_scatter = px.scatter(
            scatter_data,
            x="total_hours", y="price",
            color="institute_name",
            size="price_per_hour",
            hover_name="course_name",
            hover_data={
                "price_per_hour": ":.1f",
                "subject": True,
                "total_hours": True,
                "price": ":,.0f",
            },
            labels={
                "total_hours": "ชั่วโมงเรียนรวม",
                "price": "ราคา (฿)",
                "institute_name": "สถาบัน",
                "price_per_hour": "฿/ชม.",
            },
        )
        fig_scatter.update_layout(height=500)
        st.plotly_chart(fig_scatter, use_container_width=True)

        st.divider()

        # ── Key Man Risk Monitor ──────────────────────────────────────────────
        st.markdown("""
        <div class="section-header">
          <div class="icon" style="background:linear-gradient(135deg,#F59E0B,#D97706);">&#9888;</div>
          <div>
            <h2>Key Man Risk Monitor — Star Tutor</h2>
            <p>ติวเตอร์ที่ถือคอร์สมากที่สุด — ความเสี่ยงหากติวเตอร์ปรับเปลี่ยน</p>
          </div>
        </div>
        """, unsafe_allow_html=True)

        tutor_course_count = (
            filtered_tutor_map.groupby(["institute_name", "individual_tutor"])
            .size()
            .reset_index(name="course_count")
            .sort_values("course_count", ascending=False)
        )

        fig_risk = px.bar(
            tutor_course_count.head(15),
            x="individual_tutor", y="course_count",
            color="institute_name", text_auto=True,
            labels={
                "individual_tutor": "ติวเตอร์",
                "course_count": "จำนวนคอร์สในมือ",
                "institute_name": "สถาบัน",
            },
        )
        fig_risk.update_layout(height=450, xaxis_tickangle=-35)
        st.plotly_chart(fig_risk, use_container_width=True)

        st.dataframe(tutor_course_count, use_container_width=True, height=350)
