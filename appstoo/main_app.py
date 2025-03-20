import streamlit as st

# Page Config
st.set_page_config(
    page_title="Climate Intelligence Platform",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Styling
st.markdown("""
    <style>
        /* Global Styling */
        .stApp {
            background: linear-gradient(120deg, #0a192f 0%, #112240 100%);
            color: #e6f1ff;
            font-family: 'Montserrat', sans-serif;
        }
        h1, h2, h3 {
            color: #64ffda;
            text-align: center;
            font-weight: 700;
        }
        p {
            color: #ccd6f6;
            font-size: 18px;
            text-align: center;
            line-height: 1.6;
        }
        .feature-box {
            background: rgba(21, 61, 132, 0.4);
            border-radius: 15px;
            padding: 25px;
            margin: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.4);
            transition: all 0.3s ease;
            border: 1px solid rgba(100, 255, 218, 0.2);
        }
        .feature-box:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.5);
            border-color: rgba(100, 255, 218, 0.4);
        }
        .btn-primary {
            background-color: #64ffda;
            color: #0a192f;
            padding: 15px;
            border-radius: 12px;
            font-weight: 600;
            border: none;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .btn-primary:hover {
            background-color: #00eeff;
            box-shadow: 0 8px 15px rgba(0,0,0,0.2);
            transform: translateY(-3px);
        }
        @media print {
            body {
                background-color: #1e1e2f !important;
                color: white !important;
            }
            .stApp {
                background-color: #1e1e2f !important;
            }
            table, th, td {
                color: white !important;
            }
        }
    </style>
""", unsafe_allow_html=True)

# 🔥 Hero Section
st.markdown("""
    <h1>🌍 Climate Intelligence Platform</h1>
    <p>Empowering data-driven decisions to tackle climate change, predict disasters, and optimize transport routes.</p>
    <div style="text-align: center; margin-top: 20px;">
        <button class="btn-primary" onclick="window.location.href='/dashboard'">🚀 Get Started</button>
    </div>
""", unsafe_allow_html=True)

# ✅ Feature Section
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
        <div class="feature-box">
            <h2>🌍 Global Disaster Tracker</h2>
            <p>Real-time monitoring of global disasters using GDACS data. Filter by type, severity, and region.</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="feature-box">
            <h2>🌧️ Precipitation Change Tracker</h2>
            <p>Track monthly precipitation changes and patterns based on GeoJSON-defined regions.</p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class="feature-box">
            <h2>🌡️ Temperature Change Tracker</h2>
            <p>Analyze regional temperature changes between two years and apply warming factors.</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="feature-box">
            <h2>🚢 Green Routing System</h2>
            <p>Optimize transport routes based on time, cost, and CO2 emissions. Make your supply chain greener.</p>
        </div>
    """, unsafe_allow_html=True)

# 🚀 Get Started Section
st.markdown("""
    <div style="text-align: center; margin-top: 40px;">
        <h2>Ready to get started?</h2>
        <p>Experience the power of climate intelligence today.</p>
        <button class="btn-primary" onclick="window.location.href='/dashboard'">🚀 Start Exploring</button>
    </div>
""", unsafe_allow_html=True)

# Footer
st.markdown("""
    <footer>
        Built with ❤️ using Streamlit | © 2025 Climate Intelligence Platform
    </footer>
""", unsafe_allow_html=True)
