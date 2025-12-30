# -*- coding: utf-8 -*-
"""
手机可用版本（推荐）：Streamlit Web 表单
部署后手机浏览器打开链接即可使用（也可“添加到主屏幕”当作App）。
"""
import pandas as pd
import streamlit as st

from salary_logic import projects, calculate

st.set_page_config(page_title="武汉开明销售部季度绩效工资计算", layout="centered")

st.title("武汉开明销售部季度绩效工资计算")
st.caption("填表 → 一键计算 → 输出明细与汇总")

project = st.selectbox("项目名称", list(projects.keys()))

# ---------------- 权重定义 ----------------
weights = {
    "业绩": 0.3,
    "毛利率": 0.35,
    "结算率": 0.1,
    "开票率": 0.025,
    "回款率": 0.075,
    "审计偏差": 0.05,
    "客情成本": 0.1,
}

# 转 DataFrame
df_weights = (
    pd.Series(weights, name="权重")
      .rename_axis("指标")
      .reset_index()
)
df_weights["权重(%)"] = (df_weights["权重"] * 100).round(2).astype(str) + "%"

# ---------------- 页面内容 ----------------
st.subheader("📊 项目指标权重表")
st.dataframe(
    df_weights[["指标", "权重", "权重(%)"]],
    use_container_width=True,
    hide_index=True
)
st.info("提示：权重总和为 1.0，毛利率可为负，代表亏损项目的情况。")

col1, col2 = st.columns(2)
with col1:
    year_target = st.number_input("年度目标产值", min_value=0.0, value=5000000.0, step=10000.0, format="%.2f")
    quarter_actual = st.number_input("实际季度业绩", min_value=0.0, value=250000.0, step=10000.0, format="%.2f")
    margin = st.number_input("毛利率（如 -0.05）", min_value=-3.0, max_value=1.0, value=0.25, step=0.01, format="%.4f")
with col2:
    settlement_days = st.number_input("结算时间（工作日）", min_value=0, value=10, step=1)
    invoice_days = st.number_input("开票时间（工作日）", min_value=0, value=10, step=1)
    payback_days = st.number_input("回款时间（工作日）", min_value=0, value=30, step=1)

col3, col4 = st.columns(2)
with col3:
    audit_bias = st.number_input("审计偏差率（如 0.01）", min_value=0.0, value=0.01, step=0.001, format="%.4f")
with col4:
    customer_rate = st.number_input("客情费率（如 0.01）", min_value=0.0, value=0.01, step=0.001, format="%.4f")

tax_keep_rate = st.number_input("税后保留比例（默认 0.97）", min_value=0.0, max_value=1.0, value=0.97, step=0.001, format="%.3f")

if st.button("开始计算", type="primary"):
    try:
        res = calculate(
            project=project,
            year_target=year_target,
            quarter_actual=quarter_actual,
            margin=margin,
            settlement_days=int(settlement_days),
            invoice_days=int(invoice_days),
            payback_days=int(payback_days),
            audit_bias=audit_bias,
            customer_rate=customer_rate,
            tax_keep_rate=tax_keep_rate,
        )
    except Exception as e:
        st.error(str(e))
    else:
        st.success("计算完成")

        st.subheader("汇总")
        st.metric("业绩完成率", f"{res.performance_rate*100:.2f}%")
        c1, c2, c3 = st.columns(3)
        c1.metric("总绩效得分", f"{res.total_score:.2f}")
        c2.metric("季度绩效工资", f"{res.perf_money:.2f}")
        c3.metric("季度总工资（税前）", f"{res.total_salary:.2f}")
        st.metric("季度税后总工资", f"{res.after_tax_salary:.2f}")

        st.subheader("评分明细")
        df = pd.DataFrame(res.breakdown)
        st.dataframe(df, use_container_width=True)
