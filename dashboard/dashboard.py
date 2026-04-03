import streamlit as st
import pandas as pd
import os
import altair as alt
from sqlalchemy import create_engine

st.set_page_config(page_title="Job Market Insights", layout="wide")

st.title("🚀 Job Market Data Pipeline Insights")
st.markdown("Analyzing job roles, salaries, and technical skills.")

# Database Connection
DB_URL = os.getenv("DB_URL", "postgresql://airflow:airflow@localhost:5432/airflow")


@st.cache_data(ttl=600)
def load_data():
    try:
        engine = create_engine(DB_URL)
        # Load Jobs
        query_jobs = "SELECT * FROM jobs"
        df_jobs = pd.read_sql(query_jobs, engine)

        # Load Skills count
        query_skills = """
            SELECT s.skill_name, COUNT(js.job_id) as job_count
            FROM skills s
            JOIN job_skills js ON s.skill_id = js.skill_id
            GROUP BY s.skill_name
            ORDER BY job_count DESC
            LIMIT 15;
        """
        df_skills = pd.read_sql(query_skills, engine)

        return df_jobs, df_skills
    except Exception as e:
        st.error(f"Error connecting to database: {e}")
        return pd.DataFrame(), pd.DataFrame()


df_jobs, df_skills = load_data()

if not df_jobs.empty:
    # Top Metrics
    st.metric("Total Jobs Found", len(df_jobs))
    
    # Layout
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔥 Top Technical Skills")
        if not df_skills.empty and "job_count" in df_skills.columns:
            chart_skills = (
                alt.Chart(df_skills)
                .mark_bar()
                .encode(
                    x=alt.X("job_count:Q", title="Number of Jobs"),
                    y=alt.Y("skill_name:N", sort="-x", title="Skill"),
                    color="job_count:Q",
                )
            )
            st.altair_chart(chart_skills, use_container_width=True)
            
            # Insights Section
            st.divider()
            st.subheader("📝 Key Insights")
            top_skill = df_skills.iloc[0]["skill_name"]
            st.info(
                f"**{top_skill}** is the most in-demand skill right now, appearing in {(df_skills.iloc[0]['job_count'] / len(df_jobs) * 100):.1f}% of analyzed jobs."
            )
        else:
            st.info("No explicit technical skills found in the current job descriptions.")

    with col2:
        st.subheader("💰 Average Salary by Location")
        if "avg_salary" in df_jobs.columns and not df_jobs.empty:
            salary_by_loc = df_jobs.groupby("location")["avg_salary"].mean().reset_index()
            if not salary_by_loc.empty:
                chart_salary = (
                    alt.Chart(salary_by_loc)
                    .mark_bar()
                    .encode(
                        x=alt.X("location:N", title="Location"),
                        y=alt.Y("avg_salary:Q", title="Avg Salary ($)"),
                        color="avg_salary:Q",
                    )
                )
                st.altair_chart(chart_salary, use_container_width=True)

else:
    st.warning("⚠️ No data found in the database. Please trigger the Airflow DAG to start the processing pipeline.")
    st.info("Log in to Airflow at [http://localhost:8080](http://localhost:8080) (admin/admin) and unpause the `daily_job_pipeline` DAG.")

# Data Table
with st.expander("Show Raw Data"):
    st.dataframe(df_jobs)
