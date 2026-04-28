import streamlit as st
import pandas as pd
import mysql.connector
import matplotlib.pyplot as plt
from collections import Counter

st.set_page_config(
    page_title="Real-Time Website Spam Filter Dashboard",
    layout="wide"
)

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",   # apna mysql password daal
    "database": "web_spam"
}


def load_data():
    conn = mysql.connector.connect(**DB_CONFIG)
    query = "SELECT * FROM submissions ORDER BY id DESC"
    df = pd.read_sql(query, conn)
    conn.close()
    return df


def get_email_domain(email):
    if pd.isna(email) or "@" not in str(email):
        return "unknown"
    return str(email).split("@")[-1].lower().strip()


def is_mobile_valid(mobile):
    mobile = str(mobile).strip()
    return mobile.isdigit() and len(mobile) == 10


st.markdown("""
<style>
.main {
    background: linear-gradient(135deg, #0b1120, #111827);
    color: white;
}
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}
h1, h2, h3 {
    color: white !important;
}
.metric-card {
    background: linear-gradient(135deg, rgba(59,130,246,0.35), rgba(37,99,235,0.18));
    border: 1px solid rgba(255,255,255,0.08);
    padding: 20px;
    border-radius: 18px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.25);
    margin-bottom: 10px;
}
.metric-card h3 {
    margin: 0;
    font-size: 18px;
    color: #cbd5e1 !important;
}
.metric-card h1 {
    margin: 8px 0 0 0;
    font-size: 34px;
    color: white !important;
}
.section-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 18px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.2);
    margin-bottom: 20px;
}
.small-note {
    color: #cbd5e1;
    font-size: 13px;
}
</style>
""", unsafe_allow_html=True)

st.title("Real-Time Website Spam Filter Dashboard")
st.caption("Manual Form + Selenium Reader + MySQL + Streamlit Dashboard")

try:
    df = load_data()
except Exception as e:
    st.error(f"Database error: {e}")
    st.stop()

if df.empty:
    st.warning("No data found in database.")
    st.stop()

# ---------------------------
# Data Prep
# ---------------------------
df["score"] = pd.to_numeric(df["score"], errors="coerce").fillna(0)

if "collected_at" in df.columns:
    df["collected_at_dt"] = pd.to_datetime(df["collected_at"], errors="coerce")
else:
    df["collected_at_dt"] = pd.NaT

df["email_domain"] = df["email"].apply(get_email_domain)
df["mobile_status"] = df["mobile"].apply(lambda x: "Valid" if is_mobile_valid(x) else "Invalid")

# ---------------------------
# KPIs
# ---------------------------
total_submissions = len(df)
total_spam = (df["verdict"] == "spam").sum()
total_suspect = (df["verdict"] == "suspect").sum()
total_ham = (df["verdict"] == "ham").sum()
avg_score_total = round(df["score"].mean(), 2)

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.markdown(f"""
    <div class="metric-card">
        <h3>Total Submissions</h3>
        <h1>{total_submissions}</h1>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-card">
        <h3>Total Spam</h3>
        <h1>{total_spam}</h1>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="metric-card">
        <h3>Total Suspect</h3>
        <h1>{total_suspect}</h1>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="metric-card">
        <h3>Total Ham</h3>
        <h1>{total_ham}</h1>
    </div>
    """, unsafe_allow_html=True)

with c5:
    st.markdown(f"""
    <div class="metric-card">
        <h3>Average Score</h3>
        <h1>{avg_score_total}</h1>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------
# Filters
# ---------------------------
st.markdown("### Filters")

f1, f2, f3 = st.columns(3)

with f1:
    verdict_filter = st.multiselect(
        "Filter by Verdict",
        options=sorted(df["verdict"].dropna().unique().tolist()),
        default=sorted(df["verdict"].dropna().unique().tolist())
    )

with f2:
    state_options = sorted(df["state"].dropna().astype(str).unique().tolist())
    selected_states = st.multiselect(
        "Filter by State",
        options=state_options,
        default=state_options
    )

with f3:
    search_name = st.text_input("Search by Name / Email")

filtered_df = df.copy()

if verdict_filter:
    filtered_df = filtered_df[filtered_df["verdict"].isin(verdict_filter)]

if selected_states:
    filtered_df = filtered_df[filtered_df["state"].astype(str).isin(selected_states)]

if search_name.strip():
    q = search_name.strip().lower()
    filtered_df = filtered_df[
        filtered_df["first_name"].astype(str).str.lower().str.contains(q, na=False) |
        filtered_df["last_name"].astype(str).str.lower().str.contains(q, na=False) |
        filtered_df["email"].astype(str).str.lower().str.contains(q, na=False)
    ]

if filtered_df.empty:
    st.warning("No data matched the selected filters.")
    st.stop()

st.markdown("---")

# ---------------------------
# Recent Table
# ---------------------------
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.subheader("Recent Submissions")
st.dataframe(
    filtered_df[[
        "id", "first_name", "last_name", "email", "mobile", "dob", "gender",
        "subject", "hobbies", "address", "state", "city", "score", "verdict",
        "rules_triggered", "collected_at"
    ]],
    width="stretch",
    hide_index=True
)
st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------
# Charts Row 1
# ---------------------------
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Verdict Distribution")
    verdict_counts = filtered_df["verdict"].value_counts()

    fig1, ax1 = plt.subplots(figsize=(6, 4))
    ax1.bar(verdict_counts.index, verdict_counts.values)
    ax1.set_xlabel("Verdict")
    ax1.set_ylabel("Count")
    ax1.set_title("Spam / Suspect / Ham Count")
    st.pyplot(fig1)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Average Score by Verdict")
    avg_score = filtered_df.groupby("verdict")["score"].mean()

    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.bar(avg_score.index, avg_score.values)
    ax2.set_xlabel("Verdict")
    ax2.set_ylabel("Average Score")
    ax2.set_title("Average Spam Score by Verdict")
    st.pyplot(fig2)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------
# Charts Row 2
# ---------------------------
col3, col4 = st.columns(2)

with col3:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Top Triggered Spam Rules")

    all_rules = []
    for rules in filtered_df["rules_triggered"].dropna():
        split_rules = [r.strip() for r in str(rules).split(",") if r.strip()]
        all_rules.extend(split_rules)

    if all_rules:
        rules_series = pd.Series(all_rules).value_counts().head(10)

        fig3, ax3 = plt.subplots(figsize=(8, 5))
        ax3.barh(rules_series.index, rules_series.values)
        ax3.set_xlabel("Count")
        ax3.set_ylabel("Rule")
        ax3.set_title("Top Triggered Spam Rules")
        plt.tight_layout()
        st.pyplot(fig3)
    else:
        st.info("No rules triggered data available.")
    st.markdown("</div>", unsafe_allow_html=True)

with col4:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("State-wise Submission Count")
    state_counts = filtered_df["state"].value_counts().head(10)

    fig4, ax4 = plt.subplots(figsize=(8, 5))
    ax4.bar(state_counts.index, state_counts.values)
    ax4.set_xlabel("State")
    ax4.set_ylabel("Count")
    ax4.set_title("Submissions by State")
    plt.xticks(rotation=30)
    st.pyplot(fig4)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------
# Charts Row 3
# ---------------------------
col5, col6 = st.columns(2)

with col5:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("City-wise Submission Count")
    city_counts = filtered_df["city"].value_counts().head(10)

    fig5, ax5 = plt.subplots(figsize=(8, 5))
    ax5.bar(city_counts.index, city_counts.values)
    ax5.set_xlabel("City")
    ax5.set_ylabel("Count")
    ax5.set_title("Submissions by City")
    plt.xticks(rotation=30)
    st.pyplot(fig5)
    st.markdown("</div>", unsafe_allow_html=True)

with col6:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Score Distribution")

    fig6, ax6 = plt.subplots(figsize=(8, 5))
    ax6.hist(filtered_df["score"].dropna(), bins=10)
    ax6.set_xlabel("Score")
    ax6.set_ylabel("Frequency")
    ax6.set_title("Spam Score Distribution")
    st.pyplot(fig6)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------
# Charts Row 4
# ---------------------------
col7, col8 = st.columns(2)

with col7:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Verdict Pie Chart")
    verdict_counts_pie = filtered_df["verdict"].value_counts()

    fig7, ax7 = plt.subplots(figsize=(6, 6))
    ax7.pie(verdict_counts_pie.values, labels=verdict_counts_pie.index, autopct="%1.1f%%")
    ax7.set_title("Verdict Share")
    st.pyplot(fig7)
    st.markdown("</div>", unsafe_allow_html=True)

with col8:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Mobile Validity Split")
    mobile_counts = filtered_df["mobile_status"].value_counts()

    fig8, ax8 = plt.subplots(figsize=(6, 4))
    ax8.bar(mobile_counts.index, mobile_counts.values)
    ax8.set_xlabel("Mobile Status")
    ax8.set_ylabel("Count")
    ax8.set_title("Valid vs Invalid Mobile")
    st.pyplot(fig8)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------
# Charts Row 5
# ---------------------------
col9, col10 = st.columns(2)

with col9:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Top Email Domains")
    domain_counts = filtered_df["email_domain"].value_counts().head(10)

    fig9, ax9 = plt.subplots(figsize=(8, 5))
    ax9.barh(domain_counts.index, domain_counts.values)
    ax9.set_xlabel("Count")
    ax9.set_ylabel("Domain")
    ax9.set_title("Top Email Domains")
    plt.tight_layout()
    st.pyplot(fig9)
    st.markdown("</div>", unsafe_allow_html=True)

with col10:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Submissions Over Time")

    temp_df = filtered_df.dropna(subset=["collected_at_dt"]).copy()

    if not temp_df.empty:
        temp_df["date_only"] = temp_df["collected_at_dt"].dt.date
        date_counts = temp_df.groupby("date_only").size()

        fig10, ax10 = plt.subplots(figsize=(8, 5))
        ax10.plot(date_counts.index, date_counts.values, marker="o")
        ax10.set_xlabel("Date")
        ax10.set_ylabel("Submissions")
        ax10.set_title("Submission Trend Over Time")
        plt.xticks(rotation=30)
        st.pyplot(fig10)
    else:
        st.info("No valid collected_at date data available.")
    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------
# Charts Row 6 (NEW - Behavior Analysis)
# ---------------------------
col11, col12 = st.columns(2)

with col11:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Fast vs Normal Submission")

    fast_counts = filtered_df["rules_triggered"].str.contains("Fast submission", na=False).value_counts()

    fig11, ax11 = plt.subplots(figsize=(6, 4))
    ax11.bar(fast_counts.index.astype(str), fast_counts.values)
    ax11.set_xlabel("Fast Submission")
    ax11.set_ylabel("Count")
    ax11.set_title("Fast vs Normal Users")
    st.pyplot(fig11)

    st.markdown("</div>", unsafe_allow_html=True)

with col12:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Honeypot Triggered (Bot Detection)")

    honeypot_counts = filtered_df["rules_triggered"].str.contains("Honeypot", na=False).value_counts()

    fig12, ax12 = plt.subplots(figsize=(6, 4))
    ax12.bar(honeypot_counts.index.astype(str), honeypot_counts.values)
    ax12.set_xlabel("Honeypot Trigger")
    ax12.set_ylabel("Count")
    ax12.set_title("Bot Detection using Honeypot")
    st.pyplot(fig12)

    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------
# Summary Box
# ---------------------------
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.subheader("Quick Summary")

most_common_verdict = filtered_df["verdict"].mode()[0] if not filtered_df["verdict"].mode().empty else "N/A"
top_state = filtered_df["state"].mode()[0] if not filtered_df["state"].mode().empty else "N/A"
top_city = filtered_df["city"].mode()[0] if not filtered_df["city"].mode().empty else "N/A"

st.markdown(f"""
<div class="small-note">
• Most common verdict: <b>{most_common_verdict}</b><br>
• Top state by submissions: <b>{top_state}</b><br>
• Top city by submissions: <b>{top_city}</b><br>
• Average score across filtered data: <b>{round(filtered_df['score'].mean(), 2)}</b>
</div>
""", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)