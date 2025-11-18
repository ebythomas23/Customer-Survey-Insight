import asyncio
import streamlit as st
import pandas as pd
from pathlib import Path
from PIL import Image


# Load secrets when running on Streamlit Cloud
chat_key = st.secrets.get("OPENAI_API_KEY")
embed_key = st.secrets.get("OPENAI_EMBEDDING_API_KEY")

if chat_key:
    os.environ["OPENAI_API_KEY"] = chat_key

if embed_key:
    os.environ["OPENAI_EMBEDDING_API_KEY"] = embed_key

from teams.survey_insight import get_survey_insight_team

st.set_page_config(page_title="Survey Insight Agent", layout="wide")

st.title("Customer Survey Insight Pipeline")
st.markdown("Upload survey data and generate insights with AI-powered analysis")

# File upload
uploaded_file = st.file_uploader("Upload Survey CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success(f"Uploaded {len(df)} survey responses")
    
    with st.expander("Preview Data"):
        st.dataframe(df.head(10))
    
    # Save as input.csv
    Path("data").mkdir(exist_ok=True)
    df.to_csv("data/input.csv", index=False)
    
    if st.button("Run Analysis Pipeline", type="primary"):
        st.markdown("---")
        st.subheader("Pipeline Progress")
        
        message_container = st.container()
        
        async def run_pipeline():
            team = await get_survey_insight_team()
            messages = []
            
            async for message in team.run_stream(task="Run the full 4-step pipeline on data/input.csv"):
                msg_text = str(message)
                messages.append(msg_text)
                with message_container:
                    st.markdown(msg_text)
            
            return messages
        
        # Run the pipeline
        with st.spinner("Running AI pipeline..."):
            asyncio.run(run_pipeline())
        
        st.success("Pipeline Complete!")
        
        # Display plots
        st.markdown("---")
        st.subheader("Generated Insights")
        
        plot_files = [
            ("Top Pain Points", "data/plot_top_pain_points.png"),
            ("Pain Points by Product", "data/heatmap_pain_points_by_product.png"),
            ("Theme Severity", "data/theme_severity_stacked.png"),
            ("Trends Over Time", "data/theme_trends_over_time.png"),
        ]
        
        cols = st.columns(2)
        for idx, (title, path) in enumerate(plot_files):
            if Path(path).exists():
                with cols[idx % 2]:
                    st.markdown(f"**{title}**")
                    img = Image.open(path)
                    st.image(img, use_container_width=True)
        
        # Display output CSV
        if Path("data/output.csv").exists():
            st.markdown("---")
            st.subheader("Enriched Output Data Preview")
            output_df = pd.read_csv("data/output.csv")
            st.dataframe(output_df.head(50))
            
            st.download_button(
                label="Download Output CSV",
                data=output_df.to_csv(index=False),
                file_name="output.csv",
                mime="text/csv",
            )
else:
    st.info("Upload a CSV file to begin")
