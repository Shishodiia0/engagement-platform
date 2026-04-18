import streamlit as st
import requests
import pandas as pd
import plotly.express as px


def show(headers, API_URL):
    st.title("📈 Engagement Trends")
    st.markdown("---")

    days = st.selectbox("📅 Date Range", [7, 30, 60, 90], index=1, format_func=lambda x: f"Last {x} days")

    try:
        dau = requests.get(f"{API_URL}/analytics/dau?days={days}", headers=headers, timeout=10).json()
        growth = requests.get(f"{API_URL}/analytics/user-growth?days={days}", headers=headers, timeout=10).json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend.")
        return
    except Exception as e:
        st.error(f"❌ Error fetching data: {e}")
        return

    if dau:
        df_dau = pd.DataFrame(dau)
        df_dau.columns = [c.lower() for c in df_dau.columns]
        fig1 = px.area(df_dau, x="date", y="active_users", title=f"Daily Active Users (Last {days} Days)", color_discrete_sequence=["#636EFA"])
        st.plotly_chart(fig1, use_container_width=True)
        st.download_button("⬇️ Export DAU as CSV", df_dau.to_csv(index=False), "dau.csv", "text/csv")
    else:
        st.info("No DAU data available.")

    st.markdown("---")

    if growth:
        df_growth = pd.DataFrame(growth)
        df_growth.columns = [c.lower() for c in df_growth.columns]
        fig2 = px.bar(df_growth, x="date", y="new_users", title=f"New User Registrations (Last {days} Days)", color_discrete_sequence=["#00CC96"])
        st.plotly_chart(fig2, use_container_width=True)
        st.download_button("⬇️ Export User Growth as CSV", df_growth.to_csv(index=False), "user_growth.csv", "text/csv")
    else:
        st.info("No user growth data available.")
