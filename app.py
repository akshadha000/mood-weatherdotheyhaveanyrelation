import os
import pickle
import requests
import pandas as pd
import streamlit as st
import plotly.express as px
from dotenv import load_dotenv
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium

# ==============================
# CONFIG
# ==============================
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")
if not API_KEY:
    try:
        API_KEY = st.secrets["OPENWEATHER_API_KEY"]
    except Exception:
        API_KEY = None

st.set_page_config(
    page_title="MoodCast — Weather & Mood Intelligence",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================
# THEME / CUSTOM CSS
# ==============================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    font-size: 16px;
}
h1, h2, h3 {
    font-family: 'Space Grotesk', sans-serif;
}

.stApp {
    background: linear-gradient(-45deg, #0f0c29, #43125e, #1a1a2e, #302b63, #0f0c29);
    background-size: 500% 500%;
    animation: gradientShift 14s ease infinite;
}
@keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* Ambient glow blobs */
.stApp::before, .stApp::after {
    content: "";
    position: fixed;
    width: 500px;
    height: 500px;
    border-radius: 50%;
    filter: blur(80px);
    z-index: 0;
    pointer-events: none;
}
.stApp::before {
    background: radial-gradient(circle, rgba(167,139,250,0.35), transparent 70%);
    top: -10%;
    left: -10%;
    animation: floatBlob 12s ease-in-out infinite;
}
.stApp::after {
    background: radial-gradient(circle, rgba(52,211,153,0.3), transparent 70%);
    bottom: -10%;
    right: -10%;
    animation: floatBlob 16s ease-in-out infinite reverse;
}
@keyframes floatBlob {
    0%, 100% { transform: translate(0, 0) scale(1); }
    50% { transform: translate(40px, -30px) scale(1.15); }
}

section[data-testid="stSidebar"] {
    background: rgba(10, 10, 25, 0.9);
    border-right: 1px solid rgba(255,255,255,0.08);
    backdrop-filter: blur(12px);
}
section[data-testid="stSidebar"] * {
    font-size: 1.02rem !important;
}
section[data-testid="stSidebar"] label {
    font-size: 1.05rem !important;
    font-weight: 600;
}

h1, h2, h3, h4, p, label, span, div {
    color: #f5f5fa;
}

/* Hero */
.hero-banner {
    position: relative;
    background: linear-gradient(120deg, rgba(139,92,246,0.18), rgba(59,130,246,0.12));
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 24px;
    padding: 40px 44px;
    margin-bottom: 30px;
    overflow: hidden;
}
.hero-banner::before {
    content: "";
    position: absolute;
    top: -50%;
    right: -10%;
    width: 320px;
    height: 320px;
    background: radial-gradient(circle, rgba(139,92,246,0.35), transparent 70%);
    border-radius: 50%;
    filter: blur(20px);
}
.hero-title {
    font-size: 3rem;
    font-weight: 700;
    margin: 10px 0 0 0;
    background: linear-gradient(90deg, #A78BFA, #60A5FA, #34D399, #A78BFA);
    background-size: 300% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    display: inline-block;
    animation: shine 6s linear infinite;
    filter: drop-shadow(0 0 20px rgba(167,139,250,0.4));
}
@keyframes shine {
    to { background-position: 300% center; }
}
.hero-sub {
    font-size: 1.05rem;
    opacity: 0.85;
    font-weight: 400;
    max-width: 640px;
    margin-top: 10px;
    line-height: 1.5;
}
.pill {
    display: inline-block;
    background: rgba(167,139,250,0.18);
    border: 1px solid rgba(167,139,250,0.6);
    color: #D8B4FE;
    padding: 5px 16px;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 700;
    margin-right: 10px;
    margin-bottom: 12px;
    letter-spacing: 0.3px;
    box-shadow: 0 0 12px rgba(167,139,250,0.2);
}

/* Metric cards */
.metric-card {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.12);
    backdrop-filter: blur(14px);
    padding: 30px 20px;
    border-radius: 20px;
    text-align: center;
    margin-bottom: 16px;
    transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
}
.metric-card:hover {
    transform: translateY(-8px) scale(1.02);
    border-color: #A78BFA;
    box-shadow: 0 16px 40px rgba(139,92,246,0.35);
}
.metric-card h2 {
    margin: 0;
    font-size: 2.2rem;
    font-weight: 700;
}
.metric-card p {
    margin: 8px 0 0 0;
    opacity: 0.7;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    font-weight: 700;
}

/* Mood highlight card */
.mood-hero {
    background: linear-gradient(135deg, rgba(167,139,250,0.3), rgba(96,165,250,0.2));
    border: 2px solid rgba(167,139,250,0.55);
    border-radius: 24px;
    padding: 30px;
    text-align: center;
    animation: fadeInUp 0.6s ease, pulseGlow 3s ease-in-out infinite;
}
.mood-hero h2 {
    font-size: 2.2rem;
    margin: 6px 0;
    letter-spacing: 1px;
    filter: drop-shadow(0 0 14px rgba(167,139,250,0.5));
}
.mood-hero p {
    font-size: 0.95rem;
    opacity: 0.85;
}
@keyframes pulseGlow {
    0%, 100% { box-shadow: 0 0 30px rgba(167,139,250,0.15); }
    50% { box-shadow: 0 0 50px rgba(167,139,250,0.4); }
}
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(16px); }
    to { opacity: 1; transform: translateY(0); }
}

.section-label {
    display: inline-block;
    font-size: 0.85rem;
    letter-spacing: 1.4px;
    text-transform: uppercase;
    opacity: 0.7;
    font-weight: 700;
    margin-bottom: 8px;
    color: #D8B4FE;
}

.search-bar {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(167,139,250,0.35);
    border-radius: 22px;
    padding: 22px 26px;
    margin-bottom: 26px;
    backdrop-filter: blur(14px);
}

.debug-box {
    background: rgba(255,255,255,0.04);
    border: 1px dashed rgba(255,255,255,0.2);
    border-radius: 12px;
    padding: 12px 16px;
    font-size: 0.9rem;
    opacity: 0.85;
}

/* Responsive tweaks */
@media (max-width: 768px) {
    .hero-title { font-size: 2.1rem; }
    .hero-banner { padding: 24px 20px; }
    .metric-card h2 { font-size: 1.7rem; }
}

/* Tabs */
button[data-baseweb="tab"] {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1rem;
    font-weight: 600;
}

/* Data analysis text */
[data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li {
    font-size: 0.98rem;
    line-height: 1.6;
}

/* Inputs */
.stTextInput input, .stRadio label {
    font-size: 0.95rem !important;
}
.stButton button, .stFormSubmitButton button {
    font-size: 0.98rem !important;
    font-weight: 700;
    border-radius: 14px !important;
    background: linear-gradient(90deg, #8B5CF6, #3B82F6) !important;
    border: none !important;
    padding: 8px 22px !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.stButton button:hover, .stFormSubmitButton button:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 25px rgba(139,92,246,0.4);
}
</style>
""", unsafe_allow_html=True)

# ==============================
# LOAD MODEL + DATA
# ==============================
@st.cache_resource
def load_model_artifacts():
    model = pickle.load(open("model.pkl", "rb"))
    le_weather = pickle.load(open("weather_encoder.pkl", "rb"))
    le_mood = pickle.load(open("mood_encoder.pkl", "rb"))
    return model, le_weather, le_mood

@st.cache_data
def load_dataset():
    return pd.read_csv("final_mood_weather_data.csv")

model, le_weather, le_mood = load_model_artifacts()
df = load_dataset()

# ==============================
# HERO
# ==============================
st.markdown("""
<div class="hero-banner">
    <span class="pill">Machine Learning</span>
    <span class="pill">Live Weather API</span>
    <span class="pill">Geospatial Analysis</span>
    <div class="hero-title">MoodCast</div>
    <div class="hero-sub">Exploring how weather conditions correlate with predicted human mood — powered by live data, a trained classifier, and interactive analysis.</div>
</div>
""", unsafe_allow_html=True)

# ==============================
# SEARCH BAR (main, centered)
# ==============================
st.markdown('<div class="search-bar">', unsafe_allow_html=True)
with st.form("search_form"):
    c1, c2, c3, c4 = st.columns([2, 2, 1, 1])
    with c1:
        city = st.text_input("City", placeholder="e.g. Patna, Mumbai, London")
    with c2:
        compare_city = st.text_input("Compare with (optional)", placeholder="e.g. Delhi")
    with c3:
        unit = st.selectbox("Units", ["Celsius", "Fahrenheit"])
    with c4:
        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("Search", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

if submitted:
    st.session_state.search_city = city
    st.session_state.search_compare = compare_city
    st.session_state.search_unit = unit

city = st.session_state.get("search_city", "")
compare_city = st.session_state.get("search_compare", "")
unit = st.session_state.get("search_unit", "Celsius")

# ==============================
# SIDEBAR
# ==============================
if "history" not in st.session_state:
    st.session_state.history = []

if st.session_state.history:
    st.sidebar.markdown("### Recent Searches")
    for h in reversed(st.session_state.history[-5:]):
        st.sidebar.caption(f"{h['city'].title()} — {h['mood'].upper()} ({h['temp']}°C)")
    st.sidebar.markdown("---")

st.sidebar.markdown("### About")
st.sidebar.info(
    "This dashboard fetches live weather data, feeds it through a trained "
    "classifier, and estimates a likely mood category. It's a trend-analysis "
    "tool, not a clinical or diagnostic instrument."
)

if not API_KEY:
    st.sidebar.error("No API key found. Add OPENWEATHER_API_KEY to your .env file.")

# ==============================
# HELPER: fetch + predict, with real error surfacing
# ==============================
def get_weather_and_mood(city_name):
    """Returns (result_dict_or_None, error_message_or_None)."""
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_KEY}&units=metric"
    try:
        resp = requests.get(url, timeout=8)
    except requests.exceptions.RequestException as e:
        return None, f"Network error: {e}"

    try:
        data = resp.json()
    except ValueError:
        return None, f"Unexpected response from weather API (status {resp.status_code})."

    # OpenWeatherMap returns cod as string "404" on failure, int 200 on success
    if str(data.get("cod")) != "200":
        api_message = data.get("message", "unknown error")
        return None, f"API error ({data.get('cod')}): {api_message}"

    temp = data["main"]["temp"]
    humidity = data["main"]["humidity"]
    weather = data["weather"][0]["main"]

    weather_for_model = weather if weather in le_weather.classes_ else "Clear"
    weather_encoded = le_weather.transform([weather_for_model])[0]
    prediction = model.predict([[temp, humidity, weather_encoded]])
    predicted_mood = le_mood.inverse_transform(prediction)[0]

    confidence = None
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba([[temp, humidity, weather_encoded]])[0]
        confidence = round(max(proba) * 100, 1)

    result = {"city": city_name, "temp": temp, "humidity": humidity, "weather": weather,
              "mood": predicted_mood, "confidence": confidence}
    return result, None


def to_display_temp(celsius, unit):
    if unit == "Fahrenheit":
        return round(celsius * 9 / 5 + 32, 1), "°F"
    return round(celsius, 1), "°C"


def get_forecast_trend(city_name):
    """5-day forecast (3-hour steps, take midday reading per day) -> mood per day."""
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city_name}&appid={API_KEY}&units=metric"
    try:
        resp = requests.get(url, timeout=8)
        data = resp.json()
    except requests.exceptions.RequestException:
        return None

    if str(data.get("cod")) != "200":
        return None

    rows = []
    for entry in data.get("list", []):
        if "12:00:00" in entry["dt_txt"]:
            temp = entry["main"]["temp"]
            humidity = entry["main"]["humidity"]
            weather = entry["weather"][0]["main"]
            weather_for_model = weather if weather in le_weather.classes_ else "Clear"
            weather_encoded = le_weather.transform([weather_for_model])[0]
            pred = model.predict([[temp, humidity, weather_encoded]])
            mood = le_mood.inverse_transform(pred)[0]
            rows.append({"date": entry["dt_txt"][:10], "temp": temp, "humidity": humidity, "mood": mood})

    return pd.DataFrame(rows) if rows else None


@st.cache_data(ttl=600, show_spinner=False)
def get_weather_and_mood_cached(city_name):
    return get_weather_and_mood(city_name)


@st.cache_data(ttl=600, show_spinner=False)
def get_forecast_trend_cached(city_name):
    return get_forecast_trend(city_name)


@st.cache_data(ttl=3600, show_spinner=False)
def geocode_cached(city_name):
    geolocator = Nominatim(user_agent="moodcast-app")
    try:
        location = geolocator.geocode(city_name, timeout=5)
    except Exception:
        location = None
    if location:
        return location.latitude, location.longitude
    return None


def plotly_layout(fig, height=340):
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#f5f5fa", family="Inter", size=14),
        legend=dict(bgcolor="rgba(0,0,0,0)")
    )
    return fig

# ==============================
# TABS
# ==============================
tab_dashboard, tab_analysis, tab_about = st.tabs(["Live Dashboard", "Data Analysis", "About This Project"])

# ------------------------------
# TAB 1: LIVE DASHBOARD
# ------------------------------
with tab_dashboard:
    if not city:
        st.info("Enter a city in the sidebar to get started.")
    elif not API_KEY:
        st.warning("Add your OpenWeather API key to `.env` as `OPENWEATHER_API_KEY` to enable live lookups.")
    else:
        with st.spinner(f"Fetching live weather for {city}..."):
            result, error = get_weather_and_mood_cached(city)

        if error:
            st.error(f"Couldn't get weather data for '{city}'.")
            st.markdown(f'<div class="debug-box">{error}</div>', unsafe_allow_html=True)
            st.caption(
                "Common causes: a brand-new API key can take up to ~2 hours to activate after signup, "
                "the city name may need a country code (try 'Patna,IN'), or the key itself may be invalid."
            )
        else:
            col_left, col_right = st.columns([1.1, 1])

            with col_left:
                st.markdown(f'<div class="section-label">Weather in {result["city"].title()}</div>', unsafe_allow_html=True)

                if result not in st.session_state.history:
                    st.session_state.history.append(result)

                disp_temp, unit_label = to_display_temp(result["temp"], unit)

                m1, m2, m3 = st.columns(3)
                with m1:
                    st.markdown(f'<div class="metric-card"><h2>{disp_temp}{unit_label}</h2><p>Temperature</p></div>', unsafe_allow_html=True)
                with m2:
                    st.markdown(f'<div class="metric-card"><h2>{result["humidity"]}%</h2><p>Humidity</p></div>', unsafe_allow_html=True)
                with m3:
                    st.markdown(f'<div class="metric-card"><h2>{result["weather"]}</h2><p>Condition</p></div>', unsafe_allow_html=True)

                conf_line = f"<p>Predicted mood category — {result['confidence']}% confidence</p>" if result.get("confidence") else "<p>Predicted mood category</p>"
                st.markdown(f"""
                <div class="mood-hero">
                    <h2>{result['mood'].upper()}</h2>
                    {conf_line}
                </div>
                """, unsafe_allow_html=True)

                st.caption("Prediction is the classifier's most-likely category based on temperature, humidity, and weather condition — treat it as a trend signal, not a precise reading.")

            with col_right:
                st.markdown('<div class="section-label">Location</div>', unsafe_allow_html=True)
                coords = geocode_cached(result["city"])

                if coords:
                    lat, lon = coords
                    fmap = folium.Map(location=[lat, lon], zoom_start=10, tiles="CartoDB dark_matter")
                    folium.Marker([lat, lon], popup=result["city"], tooltip=result["mood"]).add_to(fmap)
                    folium.Circle(radius=3000, location=[lat, lon], color="#A78BFA", fill=True, fill_opacity=0.15).add_to(fmap)
                    st_folium(fmap, width=None, height=380, use_container_width=True)
                else:
                    st.warning("Couldn't resolve map coordinates for this city.")

            # 5-day mood trend
            st.markdown("---")
            st.markdown('<div class="section-label">5-Day Mood Trend</div>', unsafe_allow_html=True)
            forecast_df = get_forecast_trend_cached(city)
            if forecast_df is not None:
                fig_trend = px.line(forecast_df, x="date", y="temp", markers=True,
                                     hover_data=["mood", "humidity"],
                                     color_discrete_sequence=["#A78BFA"])
                fig_trend.update_traces(line_width=3, marker_size=10)
                for _, row in forecast_df.iterrows():
                    fig_trend.add_annotation(x=row["date"], y=row["temp"], text=row["mood"],
                                              showarrow=False, yshift=18, font=dict(size=11, color="#C4B5FD"))
                st.plotly_chart(plotly_layout(fig_trend, 300), use_container_width=True)
            else:
                st.caption("Forecast trend unavailable for this city right now.")

            # Comparison
            if compare_city:
                st.markdown("---")
                st.markdown(f'<div class="section-label">Comparing with {compare_city.title()}</div>', unsafe_allow_html=True)

                with st.spinner(f"Fetching live weather for {compare_city}..."):
                    result2, error2 = get_weather_and_mood(compare_city)

                if error2:
                    st.error(f"Couldn't get weather data for '{compare_city}'.")
                    st.markdown(f'<div class="debug-box">{error2}</div>', unsafe_allow_html=True)
                else:
                    comp_df = pd.DataFrame([result, result2])

                    c1, c2 = st.columns(2)
                    with c1:
                        fig = px.bar(comp_df, x="city", y="temp", color="city",
                                     color_discrete_sequence=["#A78BFA", "#60A5FA"],
                                     text="temp", title="Temperature (°C)")
                        fig.update_traces(textposition="outside")
                        st.plotly_chart(plotly_layout(fig, 300), use_container_width=True)
                    with c2:
                        fig2 = px.bar(comp_df, x="city", y="humidity", color="city",
                                      color_discrete_sequence=["#A78BFA", "#60A5FA"],
                                      text="humidity", title="Humidity (%)")
                        fig2.update_traces(textposition="outside")
                        st.plotly_chart(plotly_layout(fig2, 300), use_container_width=True)

                    st.dataframe(comp_df.set_index("city"), use_container_width=True)

# ------------------------------
# TAB 2: DATA ANALYSIS
# ------------------------------
with tab_analysis:
    st.markdown('<div class="section-label">Dataset Overview</div>', unsafe_allow_html=True)

    d1, d2, d3, d4 = st.columns(4)
    with d1:
        st.markdown(f'<div class="metric-card"><h2>{len(df)}</h2><p>Total Records</p></div>', unsafe_allow_html=True)
    with d2:
        st.markdown(f'<div class="metric-card"><h2>{df["temp"].mean():.1f}°C</h2><p>Avg Temperature</p></div>', unsafe_allow_html=True)
    with d3:
        st.markdown(f'<div class="metric-card"><h2>{df["humidity"].mean():.1f}%</h2><p>Avg Humidity</p></div>', unsafe_allow_html=True)
    with d4:
        n_moods = df["mood"].nunique() if "mood" in df.columns else "—"
        st.markdown(f'<div class="metric-card"><h2>{n_moods}</h2><p>Mood Categories</p></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown('<div class="section-label">Correlation Heatmap</div>', unsafe_allow_html=True)
        corr = df[["temp", "humidity"]].corr()
        fig_corr = px.imshow(corr, text_auto=".2f", color_continuous_scale="Purples", aspect="auto")
        st.plotly_chart(plotly_layout(fig_corr, 320), use_container_width=True)

    with chart_col2:
        if "mood" in df.columns:
            st.markdown('<div class="section-label">Mood Distribution</div>', unsafe_allow_html=True)
            mood_counts = df["mood"].value_counts().reset_index()
            mood_counts.columns = ["mood", "count"]
            fig_donut = px.pie(mood_counts, names="mood", values="count", hole=0.55,
                                color_discrete_sequence=px.colors.sequential.Purples_r)
            st.plotly_chart(plotly_layout(fig_donut, 320), use_container_width=True)

    st.markdown('<div class="section-label">Temperature vs Humidity</div>', unsafe_allow_html=True)
    color_col = "mood" if "mood" in df.columns else None
    fig_scatter = px.scatter(df, x="temp", y="humidity", color=color_col,
                              color_discrete_sequence=px.colors.qualitative.Bold,
                              opacity=0.75)
    st.plotly_chart(plotly_layout(fig_scatter, 380), use_container_width=True)

    st.markdown('<div class="section-label">Key Observations</div>', unsafe_allow_html=True)
    st.markdown("""
    - Temperature shows a **weak relationship** with mood in this dataset
    - Higher humidity slightly correlates with **negative mood trends**
    - Weather condition alone explains only **minor variation** in sentiment
    - City-level differences are minimal, likely due to the synthetic nature of parts of the dataset
    """)

    with st.expander("View raw data sample"):
        st.dataframe(df.head(25), use_container_width=True)

# ------------------------------
# TAB 3: ABOUT THIS PROJECT
# ------------------------------
with tab_about:
    st.markdown('<div class="section-label">Project Deep Dive</div>', unsafe_allow_html=True)
    st.markdown("""
    **What this project does**

    MoodCast investigates a simple question: *does the weather predict how people feel?*
    It combines a live weather API, geolocation, and a trained machine learning
    classifier to estimate a likely mood category for any city, then lets you
    explore the broader dataset the model was trained on.

    **How it works**

    1. **Live weather ingestion** — calls the OpenWeatherMap API for real-time
       temperature, humidity, and weather condition for a given city.
    2. **Feature encoding** — categorical weather conditions are encoded using
       a saved `LabelEncoder`, matching how training data was prepared.
    3. **ML inference** — a pre-trained classifier (`model.pkl`) predicts the
       most likely mood category from temperature, humidity, and weather condition.
    4. **Geospatial context** — the city is geocoded and plotted on an
       interactive dark-themed map using Folium.
    5. **Exploratory analysis** — a dedicated tab surfaces correlation patterns,
       mood distribution, and temperature/humidity relationships across the
       full training dataset using interactive Plotly charts.

    **Honest limitations**

    - The model predicts a **single most likely category**, not a probability
      or confidence score — treat it as a trend signal, not a precise reading.
    - Weather alone is a weak predictor of mood; real emotional state depends
      on many factors this model doesn't capture.
    - Parts of the training data are synthetic, so city-level differences may
      not reflect real-world patterns.

    **Tech stack**

    - `Streamlit` — UI and app framework
    - `scikit-learn` — trained classifier + label encoders
    - `Plotly` — interactive charts
    - `OpenWeatherMap API` — live weather data
    - `geopy` + `Folium` — geocoding and interactive maps
    - `pandas` — data handling

""")