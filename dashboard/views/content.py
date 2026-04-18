import streamlit as st
import requests
import pandas as pd
import plotly.express as px


def show(headers, API_URL):
    st.title("🔥 Content Popularity")
    st.markdown("---")

    days = st.selectbox("📅 Date Range", [7, 30, 60, 90], index=1, format_func=lambda x: f"Last {x} days")

    try:
        data = requests.get(f"{API_URL}/analytics/top-content?days={days}", headers=headers, timeout=10).json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend.")
        return
    except Exception as e:
        st.error(f"❌ Error fetching data: {e}")
        return

    if data:
        df = pd.DataFrame(data)
        df.columns = [c.lower() for c in df.columns]

        fig = px.bar(
            df, x="interactions", y="title",
            orientation="h", title=f"Top 10 Most Interacted Content (Last {days} Days)",
            color="interactions", color_continuous_scale="Blues"
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        st.subheader("Top Content Table")
        st.dataframe(df[["title", "interactions", "content_id"]], use_container_width=True)
        st.download_button("⬇️ Export as CSV", df.to_csv(index=False), "top_content.csv", "text/csv")
    else:
        st.info("No content data available yet.")
