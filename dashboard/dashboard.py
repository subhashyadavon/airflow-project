import streamlit as st
import pandas as pd
import os
import altair as alt
from sqlalchemy import create_engine

st.set_page_config(
    page_title="Job Market Insights Pro",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for premium look
st.markdown(
    """
<style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #1e2130;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #30363d;
    }
    .stInfo {
        background-color: #161b22;
        border: 1px solid #30363d;
    }
</style>
""",
    unsafe_allow_html=True,
)

st.title("Tech Market Intelligence Dashboard")
st.markdown("Real-time analysis of job roles, skill demand, and salary benchmarks.")

# Database Connection
DB_URL = os.getenv("DB_URL", "postgresql://airflow:airflow@localhost:5432/airflow")


def load_all_data():
    try:
        engine = create_engine(DB_URL)
        # Load Jobs
        df_jobs = pd.read_sql("SELECT * FROM jobs", engine)

        # Load all Job-Skill mappings with salaries
        query = """
            SELECT j.job_id, j.role, j.avg_salary, s.skill_name
            FROM jobs j
            JOIN job_skills js ON j.job_id = js.job_id
            JOIN skills s ON js.skill_id = s.skill_id
        """
        df_merged = pd.read_sql(query, engine)

        return df_jobs, df_merged
    except Exception as e:
        st.error(f"Error connecting to database: {e}")
        return pd.DataFrame(), pd.DataFrame()


df_jobs, df_merged = load_all_data()

if not df_jobs.empty:
    # Sidebar
    st.sidebar.header("🔍 Filters")
    all_roles = sorted(df_jobs["role"].unique().tolist())
    selected_roles = st.sidebar.multiselect(
        "Select Job Roles", options=all_roles, default=all_roles
    )

    # Filter Data
    filtered_jobs = df_jobs[df_jobs["role"].isin(selected_roles)]
    filtered_merged = (
        df_merged[df_merged["role"].isin(selected_roles)]
        if not df_merged.empty
        else pd.DataFrame()
    )

    # Top Metrics
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Total Jobs", len(filtered_jobs))
    with m2:
        avg_sal = filtered_jobs["avg_salary"].mean()
        st.metric(
            "Average Salary", f"${avg_sal:,.0f}" if not pd.isna(avg_sal) else "N/A"
        )
    with m3:
        unique_skills = (
            filtered_merged["skill_name"].nunique() if not filtered_merged.empty else 0
        )
        st.metric("Tech Skills Tracked", unique_skills)

    st.divider()

    # Layout - Row 1
    col_a, col_b = st.columns([1, 2])

    with col_a:
        st.subheader("📊 Role Distribution")
        role_counts = filtered_jobs.groupby("role").size().reset_index(name="count")
        chart_roles = (
            alt.Chart(role_counts)
            .mark_arc(innerRadius=50)
            .encode(
                theta=alt.Theta(field="count", type="quantitative"),
                color=alt.Color(
                    field="role", type="nominal", scale=alt.Scale(scheme="category20b")
                ),
                tooltip=["role", "count"],
            )
        ).properties(height=300)
        st.altair_chart(chart_roles, use_container_width=True)

    with col_b:
        st.subheader("💰 Average Salary by Role")
        role_salary = filtered_jobs.groupby("role")["avg_salary"].mean().reset_index()
        chart_sal_role = (
            alt.Chart(role_salary)
            .mark_bar(cornerRadiusEnd=5)
            .encode(
                x=alt.X("avg_salary:Q", title="Avg Salary ($)"),
                y=alt.Y("role:N", sort="-x", title="Role"),
                color=alt.Color(
                    "avg_salary:Q", scale=alt.Scale(scheme="magma"), legend=None
                ),
                tooltip=["role", "avg_salary"],
            )
        ).properties(height=300)
        st.altair_chart(chart_sal_role, use_container_width=True)

    st.divider()

    # Layout - Row 2
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔥 Most In-Demand Skills")
        if not filtered_merged.empty:
            skill_demand = (
                filtered_merged.groupby("skill_name").size().reset_index(name="count")
            )
            skill_demand["percentage"] = (
                skill_demand["count"] / len(filtered_jobs) * 100
            ).round(1)
            skill_demand = skill_demand.sort_values("count", ascending=False).head(15)

            chart_demand = (
                alt.Chart(skill_demand)
                .mark_bar(cornerRadiusEnd=5)
                .encode(
                    x=alt.X("percentage:Q", title="Demand (%)"),
                    y=alt.Y("skill_name:N", sort="-x", title="Skill"),
                    color=alt.Color(
                        "percentage:Q", scale=alt.Scale(scheme="viridis"), legend=None
                    ),
                    tooltip=["skill_name", "count", "percentage"],
                )
            ).properties(height=400)
            st.altair_chart(chart_demand, use_container_width=True)
        else:
            st.info(
                "No specific technical skills detected in the current job descriptions for these roles."
            )

    with col2:
        st.subheader("💰 Highest Paying Skills")
        if not filtered_merged.empty:
            skill_salary = (
                filtered_merged.groupby("skill_name")["avg_salary"]
                .agg(["mean", "count"])
                .reset_index()
            )
            skill_salary = skill_salary[skill_salary["count"] > 0]
            skill_salary = skill_salary.sort_values("mean", ascending=False).head(15)

            chart_salary = (
                alt.Chart(skill_salary)
                .mark_bar(cornerRadiusEnd=5)
                .encode(
                    x=alt.X("mean:Q", title="Avg Salary ($)"),
                    y=alt.Y("skill_name:N", sort="-x", title="Skill"),
                    color=alt.Color(
                        "mean:Q", scale=alt.Scale(scheme="magma"), legend=None
                    ),
                    tooltip=["skill_name", "mean", "count"],
                )
            ).properties(height=400)
            st.altair_chart(chart_salary, use_container_width=True)
        else:
            st.info("Add more job data to see skill-to-salary correlations.")

    st.divider()

    # Detailed Insights
    if not filtered_merged.empty:
        skill_demand = (
            filtered_merged.groupby("skill_name").size().reset_index(name="count")
        )
        skill_demand["percentage"] = (
            skill_demand["count"] / len(filtered_jobs) * 100
        ).round(1)
        skill_demand = skill_demand.sort_values("count", ascending=False)
        top_skill = skill_demand.iloc[0]["skill_name"]
        st.info(
            f"💡 **Market Insight:** For the selected roles, **{top_skill}** is the most critical skill, appearing in {skill_demand.iloc[0]['percentage']}% of job listings."
        )

else:
    st.warning("⚠️ No job data found in the database.")
    st.info(
        "1. Go to Airflow [http://localhost:8080](http://localhost:8080)\n2. Unpause and Trigger `daily_job_pipeline`."
    )

# Data Table
with st.expander("📂 Explore Raw Job Postings"):
    st.dataframe(
        filtered_jobs if not df_jobs.empty else df_jobs, use_container_width=True
    )
