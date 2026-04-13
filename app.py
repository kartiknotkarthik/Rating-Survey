import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Import our logic modules
from scraper import fetch_groww_reviews
from analyzer import GrowwAnalyzer
from mailer import send_pulse_email

load_dotenv()

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="GROWW Pulse | Growth Analysis Tool",
    page_icon="💹",
    layout="wide"
)

# --- PREMIUM AESTHETICS (CSS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');

    :root {
        --groww-green: #00d09c;
        --dark-bg: #0f172a;
        --card-bg: #ffffff;
    }

    * {
        font-family: 'Outfit', sans-serif;
    }

    .stApp {
        background-color: #f1f5f9;
    }

    /* Main Header */
    .header-container {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 3rem 2rem;
        border-radius: 0 0 2rem 2rem;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        text-align: center;
    }

    .header-title {
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        background: linear-gradient(to right, #00d09c, #00b386);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Cards */
    .glass-card {
        background: white;
        padding: 2rem;
        border-radius: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border: 1px solid #e2e8f0;
        margin-bottom: 1.5rem;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #00d09c 0%, #00b386 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 1rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        width: 100%;
        height: 3.5rem;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0, 208, 156, 0.4);
        color: white;
    }

    /* Status Badges */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        background: #ecfdf5;
        color: #059669;
    }

    /* Section Headings */
    .section-title {
        color: #1e293b;
        font-weight: 700;
        font-size: 1.5rem;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Metrics */
    .metric-container {
        text-align: center;
        padding: 1.5rem;
        border-right: 1px solid #f1f5f9;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 800;
        color: #0f172a;
    }
    .metric-label {
        color: #64748b;
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""
<div class="header-container">
    <div class="header-title">GROWW PULSE</div>
    <div style="font-size: 1.2rem; opacity: 0.8;">Weekly Insight Generator & Pulse Orchestrator</div>
</div>
""", unsafe_allow_html=True)

# --- LAYOUT ---
col_sidebar, col_main = st.columns([1, 2.5], gap="large")

with col_sidebar:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">⚙️ Configuration</div>', unsafe_allow_html=True)
    
    weeks = st.select_slider(
        "Lookback Period",
        options=[4, 8, 12],
        value=8,
        help="How many weeks of reviews to analyze"
    )
    
    st.markdown("---")
    
    # API Check
    groq_ready = os.getenv("GROQ_API_KEY") is not None
    email_ready = all([os.getenv("SENDER_EMAIL"), os.getenv("RECEIVER_EMAIL")])
    
    st.markdown(f"**API Status**")
    st.markdown(f"Groq: {'✅ Ready' if groq_ready else '❌ Missing'}")
    st.markdown(f"Email: {'✅ Configured' if email_ready else '⚠️ Not Setup'}")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("✨ Generate Weekly Pulse"):
        if not groq_ready:
            st.error("Please set your GROQ_API_KEY in the .env file.")
        else:
            with st.spinner("🔍 Fetching Play Store reviews..."):
                df = fetch_groww_reviews(weeks=weeks)
                st.session_state['df'] = df
                
            with st.spinner("🤖 Analyzing themes & sentiments..."):
                analyzer = GrowwAnalyzer()
                report = analyzer.analyze_weekly_pulse(df)
                st.session_state['report'] = report
                st.session_state['timestamp'] = datetime.now()
                st.success("Analysis Complete!")

    if 'report' in st.session_state:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📧 Send Draft Email"):
            with st.spinner("Sending draft..."):
                if send_pulse_email(st.session_state['report']):
                    st.toast("Email sent successfully!", icon="✅")
                    st.balloons()
                else:
                    st.error("Failed to send email. Check logs.")
                    
    st.markdown('</div>', unsafe_allow_html=True)

with col_main:
    if 'report' in st.session_state:
        # Metrics Row
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        m_col1, m_col2, m_col3 = st.columns(3)
        df = st.session_state['df']
        m_col1.markdown(f'<div class="metric-container"><div class="metric-value">{len(df)}</div><div class="metric-label">Reviews Analyzed</div></div>', unsafe_allow_html=True)
        m_col2.markdown(f'<div class="metric-container"><div class="metric-value">{round(df["score"].mean(), 1)}⭐</div><div class="metric-label">Avg. Rating</div></div>', unsafe_allow_html=True)
        m_col3.markdown(f'<div class="metric-container" style="border:none"><div class="metric-value">{weeks}w</div><div class="metric-label">Timespan</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Report Area
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="section-title">📊 Pulse Report <span class="badge">Generated {st.session_state["timestamp"].strftime("%H:%M")}</span></div>', unsafe_allow_html=True)
        st.markdown(st.session_state['report'])
        st.markdown('</div>', unsafe_allow_html=True)
        
    else:
        # Welcome State
        st.markdown("""
        <div style="background: white; padding: 5rem; border-radius: 1.5rem; text-align: center; border: 2px dashed #cbd5e1; color: #64748b;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">📈</div>
            <h2 style="color: #1e293b; font-weight: 700;">Ready for Insights?</h2>
            <p>Select your lookback period and click <b>Generate Weekly Pulse</b> to begin.</p>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown(
    f'<div style="text-align: center; padding: 2rem; color: #94a3b8; font-size: 0.8rem;">'
    f'© {datetime.now().year} GROWW Growth Team | Data sourced via google-play-scraper'
    f'</div>', 
    unsafe_allow_html=True
)
