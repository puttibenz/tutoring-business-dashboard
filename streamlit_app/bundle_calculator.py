import streamlit as st
import pandas as pd


SUBJECT_KEYWORDS: dict[str, list[str]] = {
    "คณิตศาสตร์": ["คณิต"],
    "ฟิสิกส์":    ["ฟิสิกส์"],
    "เคมี":       ["เคมี"],
    "ชีววิทยา":  ["ชีวะ", "ชีว"],
    "ภาษาไทย":   ["ภาษาไทย", "ไทย-สังคม"],
    "สังคมศึกษา": ["สังคม", "ไทย-สังคม"],
    "ภาษาอังกฤษ": ["อังกฤษ", "English"],
    "ความถนัด (TGAT/TPAT/สอบเฉพาะทาง)": ["TGAT", "TPAT", "ความถนัด"],
}

COMBO_SUBJECT_MAP: dict[str, list[str]] = {
    "ภาษาไทย-สังคมศึกษา":                    ["ภาษาไทย", "สังคมศึกษา"],
    "วิทยาศาสตร์รวม (ฟิสิกส์/เคมี/ชีวะ)":   ["ฟิสิกส์", "เคมี", "ชีววิทยา"],
    "แพ็กเกจวิทย์-คณิต (รวมวิชา)":          ["ฟิสิกส์", "เคมี", "ชีววิทยา", "คณิตศาสตร์"],
    "แพ็กเกจเตรียมสอบแพทย์ (กสพท/TPAT1)": [
        "ฟิสิกส์", "เคมี", "ชีววิทยา", "คณิตศาสตร์",
        "ภาษาไทย", "สังคมศึกษา", "ภาษาอังกฤษ",
        "ความถนัด (TGAT/TPAT/สอบเฉพาะทาง)",
    ],
    "แพ็กเกจเตรียมสอบวิศวะ (TPAT3)": [
        "ฟิสิกส์", "คณิตศาสตร์", "ภาษาอังกฤษ",
        "ความถนัด (TGAT/TPAT/สอบเฉพาะทาง)",
    ],
    "ความถนัด (TGAT/TPAT/สอบเฉพาะทาง)": ["ความถนัด (TGAT/TPAT/สอบเฉพาะทาง)"],
}

CORE_SUBJECTS: list[str] = [
    "คณิตศาสตร์", "ฟิสิกส์", "เคมี", "ชีววิทยา",
    "ภาษาไทย", "สังคมศึกษา", "ภาษาอังกฤษ",
    "ความถนัด (TGAT/TPAT/สอบเฉพาะทาง)",
]


class BundleCalculatorTab:
    """Tab 3 — Smart Bundle Calculator (🧮)"""

    def __init__(self, courses_df: pd.DataFrame, tutor_map_df: pd.DataFrame):
        self.courses = courses_df
        self.tutor_map = tutor_map_df

    # ── Private helpers ───────────────────────────────────────────────────────

    def _get_bundle_subjects(self, row: pd.Series) -> set[str]:
        """Return set of core subjects covered by a bundle row."""
        if row["subject"] in COMBO_SUBJECT_MAP:
            return set(COMBO_SUBJECT_MAP[row["subject"]])
        covered: set[str] = set()
        if row["subject"] in CORE_SUBJECTS:
            covered.add(row["subject"])
        name = str(row["course_name"])
        for subj, keywords in SUBJECT_KEYWORDS.items():
            if any(kw in name for kw in keywords):
                covered.add(subj)
        return covered

    def _find_cheapest_singles(
        self, selected: list[str], pool: pd.DataFrame
    ) -> tuple[pd.DataFrame, float]:
        """For each selected subject, find cheapest single-subject course."""
        if "course_scope" in pool.columns:
            pool = pool[pool["course_scope"] == "Full Course (คอร์สเตรียมสอบ/รวมเทอม)"]
        rows = []
        total = 0.0
        for subj in selected:
            candidates = pool[
                (pool["subject"] == subj)
                & (pool["course_type"].isin(["ติวเนื้อหา/เสริมเกรด", "ปูพื้นฐาน"]))
                & (pool["price"] > 0)
            ]
            if candidates.empty:
                rows.append({
                    "วิชา": subj,
                    "คอร์ส": "ไม่พบคอร์สแยก",
                    "สถาบัน": "-",
                    "ราคา (฿)": None,
                    "url": "",
                })
            else:
                best = candidates.loc[candidates["price"].idxmin()]
                rows.append({
                    "วิชา": subj,
                    "คอร์ส": best["course_name"],
                    "สถาบัน": best["institute_name"],
                    "ราคา (฿)": best["price"],
                    "url": best["url"],
                })
                total += best["price"]
        return pd.DataFrame(rows), total

    def _find_best_bundles(
        self,
        selected: list[str],
        pool: pd.DataFrame,
        require_full_coverage: bool,
    ) -> pd.DataFrame:
        """Score and rank bundle packages by subject coverage."""
        if "course_scope" in pool.columns:
            pool = pool[pool["course_scope"] == "Full Course (คอร์สเตรียมสอบ/รวมเทอม)"]
        selected_set = set(selected)
        bundles = pool[(pool["course_type"] == "คอร์สแพ็กเกจ") & (pool["price"] > 0)].copy()
        if bundles.empty:
            return pd.DataFrame()

        records = []
        for _, row in bundles.iterrows():
            covered = self._get_bundle_subjects(row)
            overlap = covered & selected_set
            if require_full_coverage and overlap != selected_set:
                continue
            if not overlap:
                continue
            score = len(overlap) / len(selected_set)
            records.append({
                "คอร์ส": row["course_name"],
                "สถาบัน": row["institute_name"],
                "ครอบคลุมวิชา": ", ".join(sorted(overlap)),
                "coverage_score": round(score, 2),
                "ชั่วโมง": row["total_hours"],
                "ราคา (฿)": row["price"],
                "url": row["url"],
            })

        if not records:
            return pd.DataFrame()
        result = pd.DataFrame(records)
        result = result.sort_values(
            ["coverage_score", "ราคา (฿)"], ascending=[False, True]
        )
        return result.head(5).reset_index(drop=True)

    # ── Public API ────────────────────────────────────────────────────────────

    @property
    def core_subjects(self) -> list[str]:
        return CORE_SUBJECTS

    def render(self, filtered: pd.DataFrame, filtered_tutor_map: pd.DataFrame) -> None:
        st.header("🧮 Smart Bundle Calculator")
        st.caption(
            "เลือกวิชาที่อยากเรียน → ระบบเปรียบเทียบให้ว่า "
            "**ซื้อแยกวิชา** กับ **ซื้อแพ็กเกจรวม** แบบไหนคุ้มกว่า"
        )
        st.caption(f"วิเคราะห์จาก **{len(filtered)}** คอร์ส (ตาม Smart Filters ด้านซ้าย)")
        st.divider()

        # ── User Inputs ───────────────────────────────────────────────────────
        col_a, col_b = st.columns([3, 1])

        with col_a:
            selected_subjects: list[str] = st.multiselect(
                "📚 เลือกวิชาที่อยากเรียน (เลือกได้มากกว่า 1 วิชา)",
                options=CORE_SUBJECTS,
                default=[],
                key="tab3_bundle_subjects",
            )
        with col_b:
            coverage_mode = st.radio(
                "🎯 แพ็กเกจที่แสดง",
                options=["ครบทุกวิชาที่เลือก", "บางวิชาก็ได้"],
                index=1,
                key="tab3_coverage_mode",
            )

        if len(selected_subjects) < 2:
            st.info("กรุณาเลือกอย่างน้อย **2 วิชา** เพื่อเปรียบเทียบ")
            return

        require_full = coverage_mode == "ครบทุกวิชาที่เลือก"

        # ── Compute ───────────────────────────────────────────────────────────
        singles_df, singles_total = self._find_cheapest_singles(selected_subjects, filtered)
        bundles_df = self._find_best_bundles(selected_subjects, filtered, require_full)

        best_bundle_price = (
            float(bundles_df.iloc[0]["ราคา (฿)"]) if not bundles_df.empty else None
        )
        saving = (
            (singles_total - best_bundle_price)
            if best_bundle_price is not None
            else None
        )

        # ── KPI Row ───────────────────────────────────────────────────────────
        m1, m2, m3 = st.columns(3)
        m1.metric(
            "🧾 ราคาซื้อแยกรวม",
            f"฿{singles_total:,.0f}" if singles_total > 0 else "N/A",
        )
        m2.metric(
            "📦 ราคาแพ็กเกจดีสุด",
            f"฿{best_bundle_price:,.0f}" if best_bundle_price is not None else "ไม่พบแพ็กเกจ",
        )
        if saving is not None:
            m3.metric(
                "💰 ประหยัดได้",
                f"฿{abs(saving):,.0f}",
                delta=f"{'ถูกกว่า' if saving > 0 else 'แพงกว่า'} {abs(saving):,.0f} ฿",
                delta_color="normal" if saving > 0 else "inverse",
            )
        else:
            m3.metric("💰 ประหยัดได้", "—")

        st.divider()

        # ── Side-by-Side Comparison ───────────────────────────────────────────
        left, right = st.columns(2)

        with left:
            st.subheader("🧾 ซื้อแยกวิชา (ราคาถูกสุดต่อวิชา)")
            display_singles = singles_df.copy()
            display_singles["ราคา (฿)"] = display_singles["ราคา (฿)"].apply(
                lambda x: f"฿{x:,.0f}" if pd.notna(x) else "ไม่มีคอร์สแยก"
            )
            st.dataframe(
                display_singles[["วิชา", "คอร์ส", "สถาบัน", "ราคา (฿)"]],
                use_container_width=True,
                hide_index=True,
            )
            st.markdown(f"**ยอดรวม: ฿{singles_total:,.0f}**")

            missing = singles_df[
                singles_df["ราคา (฿)"] == "ไม่มีคอร์สแยก"
            ]["วิชา"].tolist()
            if missing:
                st.warning(
                    f"⚠️ ไม่พบคอร์สแยกสำหรับ: {', '.join(missing)} "
                    "(อาจเป็นเพราะ sidebar filter กรองออกไป)"
                )

        with right:
            st.subheader("📦 แพ็กเกจที่แนะนำ")
            if bundles_df.empty:
                verb = "ครอบคลุมทุกวิชา" if require_full else "ครอบคลุมบางวิชา"
                st.warning(
                    f"ไม่พบแพ็กเกจที่{verb}ที่คุณเลือก\n\n"
                    "ลองเปลี่ยนเป็น **บางวิชาก็ได้** หรือปรับ Smart Filters ด้านซ้าย"
                )
            else:
                display_bundles = bundles_df.copy()
                display_bundles["coverage_score"] = display_bundles["coverage_score"].apply(
                    lambda x: f"{x * 100:.0f}%"
                )
                display_bundles["ราคา (฿)"] = display_bundles["ราคา (฿)"].apply(
                    lambda x: f"฿{x:,.0f}"
                )
                st.dataframe(
                    display_bundles[[
                        "คอร์ส", "สถาบัน", "ครอบคลุมวิชา",
                        "coverage_score", "ชั่วโมง", "ราคา (฿)",
                    ]].rename(columns={"coverage_score": "ครอบคลุม %"}),
                    use_container_width=True,
                    hide_index=True,
                )
                if saving is not None and saving > 0:
                    st.success(
                        f"✅ แพ็กเกจนี้ถูกกว่าซื้อแยก **฿{saving:,.0f}** "
                        f"({saving / singles_total * 100:.1f}%)"
                    )
                elif saving is not None and saving <= 0:
                    st.info(
                        f"แพ็กเกจนี้แพงกว่าซื้อแยก ฿{abs(saving):,.0f} "
                        "— แต่อาจให้ชั่วโมงเรียนมากกว่าหรือครอบคลุมวิชาได้ดีกว่า"
                    )
