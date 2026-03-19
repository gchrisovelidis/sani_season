import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime, date, time
from zoneinfo import ZoneInfo
from pathlib import Path
import base64
import requests

st.markdown("""
<style>
footer {visibility: hidden;}
header {visibility: hidden;}
#MainMenu {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# -----------------------
# Config
# -----------------------
TARGET_DATE = date(2026, 11, 7)
SEASON_START = date(2026, 3, 26)
START_SHOW_TIME = time(9, 0)
END_SHOW_TIME = time(17, 30)
TIMEZONE = "Europe/Athens"
LOGO_PATH = "logo.png"

# 👉 ADD YOUR API KEY HERE
API_KEY = "3d688fbda879b3f76bc98c248dfcd652"

CITY = "Nea Erythraia,GR"

st.set_page_config(
    page_title="Sani Season",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -----------------------
# Helpers
# -----------------------
def get_logo_base64(path: str) -> str:
    file_path = Path(path)
    if not file_path.exists():
        return ""
    return base64.b64encode(file_path.read_bytes()).decode()

# -----------------------
# Weather
# -----------------------
def get_weather():
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
        response = requests.get(url).json()

        temp = round(response["main"]["temp"])
        weather = response["weather"][0]["main"]

        return f"{temp}°C | {weather}"
    except:
        return "—"

weather_text = get_weather()

# -----------------------
# Time calculations
# -----------------------
now = datetime.now(ZoneInfo(TIMEZONE))
today = now.date()
current_time = now.time().replace(microsecond=0)

days_remaining = (TARGET_DATE - today).days
show_countdown = START_SHOW_TIME <= current_time <= END_SHOW_TIME

countdown_html = ""
if show_countdown:
    target_dt = datetime.combine(today, END_SHOW_TIME, tzinfo=ZoneInfo(TIMEZONE))
    remaining = target_dt - now
    total_seconds = max(int(remaining.total_seconds()), 0)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    countdown_text = f"{hours}h {minutes:02d}m"

    countdown_html = f"""
        <div class="label">Time until 17:30</div>
        <div class="countdown">{countdown_text}</div>
    """

# -----------------------
# Season Progress
# -----------------------
total_days = (TARGET_DATE - SEASON_START).days
elapsed_days = (today - SEASON_START).days
progress = max(0, min(100, int((elapsed_days / total_days) * 100)))

progress_bar = f"""
<div class="progress-label">Season Progress</div>
<div class="progress-bar">
    <div class="progress-fill" style="width:{progress}%"></div>
</div>
<div class="progress-text">{progress}%</div>
"""

# -----------------------
# Logo
# -----------------------
logo_html = ""
logo_b64 = get_logo_base64(LOGO_PATH)
if logo_b64:
    logo_html = f"""
        <div class="logo">
            <img src="data:image/png;base64,{logo_b64}" alt="Logo">
        </div>
    """

# -----------------------
# HTML
# -----------------------
html = f"""
<!DOCTYPE html>
<html>
<head>
<meta http-equiv="refresh" content="60">
<meta charset="utf-8">
<style>

html, body {{
    margin: 0;
    padding: 0;
    height: 100%;
    overflow: hidden;
    background: white;
    font-family: Arial;
}}

.page {{
    display: flex;
    height: 100vh;
}}

.left {{
    width: 30%;
    padding: 40px;
}}

.center {{
    width: 70%;
    display: flex;
    align-items: center;
    justify-content: center;
}}

.content {{
    text-align: center;
}}

.logo img {{
    width: 220px;
    margin-bottom: 20px;
}}

.weather {{
    font-size: 28px;
    font-weight: 600;
    margin-bottom: 40px;
}}

.progress-label {{
    font-size: 16px;
    color: #666;
    margin-bottom: 10px;
}}

.progress-bar {{
    width: 100%;
    height: 14px;
    background: #eee;
    border-radius: 10px;
    overflow: hidden;
    margin-bottom: 8px;
}}

.progress-fill {{
    height: 100%;
    background: #2f3345;
}}

.progress-text {{
    font-size: 16px;
    font-weight: 600;
}}

.label {{
    font-size: 18px;
    color: #5f6675;
    margin-bottom: 10px;
}}

.clock {{
    font-size: 100px;
    font-weight: 700;
    margin-bottom: 25px;
}}

.countdown {{
    font-size: 70px;
    font-weight: 700;
    margin-bottom: 25px;
}}

.days {{
    font-size: 70px;
    font-weight: 700;
}}

</style>
</head>

<body>
<div class="page">

    <div class="left">
        <div class="weather">🌤 {weather_text}</div>
        {progress_bar}
    </div>

    <div class="center">
        <div class="content">
            {logo_html}
            <div class="label">Current time</div>
            <div class="clock">{now.strftime("%H:%M")}</div>
            {countdown_html}
            <div class="label">Days until 7 November 2026</div>
            <div class="days">{days_remaining} days</div>
        </div>
    </div>

</div>
</body>
</html>
"""

components.html(html, height=500, scrolling=False)