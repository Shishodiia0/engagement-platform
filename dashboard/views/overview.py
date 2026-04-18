import streamlit as st
import requests
import pandas as pd
import plotly.express as px


def show(headers, API_URL):
    st.title("📊 Overview")
    st.markdown("---")

    days = st.selectbox("📅 Date Range", [7, 30, 60, 90], index=1, format_func=lambda x: f"Last {x} days")

    try:
        dau = requests.get(f"{API_URL}/analytics/dau?days={days}", headers=headers, timeout=10).json()
        events = requests.get(f"{API_URL}/analytics/event-breakdown?days={days}", headers=headers, timeout=10).json()
        growth = requests.get(f"{API_URL}/analytics/user-growth?days={days}", headers=headers, timeout=10).json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend.")
        return
    except Exception as e:
        st.error(f"❌ Error fetching data: {e}")
        return

    total_users = sum(row.get("NEW_USERS", 0) for row in growth) if growth else 0
    today_dau = dau[-1]["ACTIVE_USERS"] if dau else 0
    total_events = sum(row.get("TOTAL", 0) for row in events) if events else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("👥 Total Users", total_users)
    col2.metric("🟢 Active Users Today", today_dau)
    col3.metric("⚡ Total Events", total_events)

    st.markdown("---")
    st.subheader("📅 Daily Active Users")
    if dau:
        df = pd.DataFrame(dau)
        df.columns = [c.lower() for c in df.columns]
        fig = px.line(df, x="date", y="active_users", markers=True, title=f"DAU - Last {days} Days")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available yet.")

    st.markdown("---")
    st.subheader("⚡ Live Event Feed")
    st.caption("Last 20 events")
    try:
        feed = requests.get(f"{API_URL}/events/recent", headers=headers, timeout=10).json()
        if feed:
            df_feed = pd.DataFrame(feed)
            df_feed.columns = [c.lower() for c in df_feed.columns]
            st.dataframe(df_feed, use_container_width=True)
        else:
            st.info("No recent events.")
    except Exception:
        st.info("No recent events.")

    st.button("🔄 Refresh Feed")
