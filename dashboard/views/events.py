import streamlit as st
import requests
import pandas as pd
import plotly.express as px


def show(headers):
    st.title("⚡ Event Breakdown")
    st.markdown("---")

    days = st.selectbox("📅 Date Range", [7, 30, 60, 90], index=1, format_func=lambda x: f"Last {x} days")

    try:
        data = requests.get(f"http://localhost:8000/analytics/event-breakdown?days={days}", headers=headers, timeout=10).json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend.")
        return
    except Exception as e:
        st.error(f"❌ Error fetching data: {e}")
        return

    if data:
        df = pd.DataFrame(data)
        df.columns = [c.lower() for c in df.columns]

        col1, col2 = st.columns(2)
        with col1:
            fig_bar = px.bar(df, x="event_type", y="total", title=f"Events by Type (Last {days} Days)", color="event_type")
            st.plotly_chart(fig_bar, use_container_width=True)
        with col2:
            fig_pie = px.pie(df, names="event_type", values="total", title="Event Distribution")
            st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("---")
        st.subheader("Raw Data")
        st.dataframe(df, use_container_width=True)
        st.download_button("⬇️ Export as CSV", df.to_csv(index=False), "event_breakdown.csv", "text/csv")
    else:
        st.info("No event data available yet.")
