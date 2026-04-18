import streamlit as st
import requests


def show(headers, API_URL):
    st.title("🔄 ETL Pipeline Status")
    st.markdown("---")

    try:
        data = requests.get(f"{API_URL}/analytics/etl-status", headers=headers, timeout=5).json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend.")
        return

    if "status" in data and data["status"] == "No ETL runs yet":
        st.warning("No ETL runs recorded yet.")
    else:
        status = data.get("status", "unknown")
        col1, col2, col3 = st.columns(3)
        col1.metric("📦 Rows Synced", data.get("rows_extracted", 0))
        col2.metric("🕐 Last Synced At", str(data.get("last_synced_at", "N/A"))[:19])
        col3.metric("🕐 ETL Ran At", str(data.get("ran_at", "N/A"))[:19])
        st.markdown("---")
        if "success" in status:
            st.success(f"✅ Last ETL Status: {status}")
        else:
            st.error(f"❌ Last ETL Status: {status}")

    st.markdown("---")
    st.subheader("⚡ Manual ETL Trigger")
    st.caption("Sync data from PostgreSQL to Snowflake right now.")
    if st.button("🔁 Sync Now"):
        with st.spinner("Running ETL pipeline..."):
            try:
                res = requests.post(f"{API_URL}/etl/trigger", headers=headers, timeout=120)
                if res.status_code == 200:
                    st.success(f"✅ ETL completed! Rows synced: {res.json().get('rows_synced', 0)}")
                else:
                    st.error("❌ ETL trigger failed.")
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to backend.")
            except requests.exceptions.Timeout:
                st.warning("⏳ ETL is taking longer than expected.")
