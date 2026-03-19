import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime, date, time
from zoneinfo import ZoneInfo
from pathlib import Path
import base64
import requests

st.set_page_config(
    page_title="Sani Season",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
footer {visibility: hidden;}
header {visibility: hidden;}
#MainMenu {visibility: hidden;}
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}
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

API_KEY = st.secrets["API_KEY"]

OFFICE_LOCATIONS = {
    "Thessaloniki": "Thessaloniki,GR",
}

PROPERTY_LOCATIONS = {
    "Halkidiki": "Polygyros,GR",
    "Corfu": "Kerkyra,GR",
    "Kos": "Kos,GR",
    "Crete": "Heraklion,GR",
    "Marbella": "Marbella,ES",
    "Mallorca": "Palma,ES",
}

# -----------------------
# Helpers
# -----------------------
def get_logo_base64(path: str) -> str:
    file_path = Path(path)
    if not file_path.exists():
        return ""
    return base64.b64encode(file_path.read_bytes()).decode()

def get_weather_icon(weather: str) -> str:
    mapping = {
        "Clear": "☀️",
        "Clouds": "☁️",
        "Rain": "🌧",
        "Drizzle": "🌦",
        "Thunderstorm": "⛈",
        "Snow": "❄️",
        "Mist": "🌫",
        "Fog": "🌫",
        "Haze": "🌫",
        "Smoke": "🌫",
        "Dust": "🌫",
        "Sand": "🌫",
        "Ash": "🌫",
        "Squall": "🌬",
        "Tornado": "🌪",
    }
    return mapping.get(weather, "🌤")

def get_weather_for_city(query: str) -> dict:
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": query,
            "appid": API_KEY,
            "units": "metric",
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if response.status_code != 200:
            return {"temp": "—", "weather": "Unavailable", "icon": "•"}

        temp = round(data["main"]["temp"])
        weather = data["weather"][0]["main"]
        icon = get_weather_icon(weather)

        return {"temp": f"{temp}°C", "weather": weather, "icon": icon}

    except Exception:
        return {"temp": "—", "weather": "Unavailable", "icon": "•"}

def render_weather_rows(locations: dict, office: bool = False) -> str:
    rows = []
    for label, query in locations.items():
        info = get_weather_for_city(query)
        row_class = "office-row" if office else "weather-row"
        rows.append(f"""
            <div class="{row_class}">
                <div class="weather-left">
                    <div class="weather-city">{label}</div>
                    <div class="weather-condition">{info["icon"]} {info["weather"]}</div>
                </div>
                <div class="weather-temp">{info["temp"]}</div>
            </div>
        """)
    return "".join(rows)

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
progress = max(0, min(100, int((elapsed_days / total_days) * 100))) if total_days > 0 else 0

progress_bar = f"""
<div class="center-progress">
    <div class="label">Season Progress</div>
    <div class="progress-bar center-progress-bar">
        <div class="progress-fill" style="width:{progress}%"></div>
    </div>
    <div class="progress-text">{progress}%</div>
</div>
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
# Weather HTML
# -----------------------
office_weather_html = render_weather_rows(OFFICE_LOCATIONS, office=True)
property_weather_html = render_weather_rows(PROPERTY_LOCATIONS, office=False)

# -----------------------
# HTML
# -----------------------
html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="refresh" content="60">
    <meta charset="utf-8">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        html, body {{
            margin: 0;
            padding: 0;
            height: 100%;
            overflow: hidden;
            background: white;
            font-family: 'Inter', Arial, Helvetica, sans-serif;
            color: #2f3345;
        }}

        .page {{
            display: flex;
            width: 100%;
            height: 100vh;
            background: white;
        }}

        .left {{
            width: 34%;
            padding: 24px 28px 20px 32px;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
        }}

        .center {{
            width: 66%;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 10px 20px;
            box-sizing: border-box;
        }}

        .content {{
            text-align: center;
            width: 100%;
            max-width: 760px;
        }}

        .logo {{
            margin-bottom: 18px;
        }}

        .logo img {{
            width: 220px;
            max-width: 60vw;
            height: auto;
            pointer-events: none;
            user-select: none;
            -webkit-user-drag: none;
        }}

        .section {{
            margin-bottom: 18px;
        }}

        .section-title {{
            font-size: 13px;
            font-weight: 700;
            color: #7a8190;
            text-transform: uppercase;
            letter-spacing: 0.7px;
            margin-bottom: 12px;
        }}

        .office-row,
        .weather-row {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 16px;
            margin-bottom: 6px;
        }}

        .weather-left {{
            text-align: left;
        }}

        .weather-city {{
            font-size: 17px;
            font-weight: 600;
            line-height: 1.2;
            color: #2f3345;
        }}

        .weather-condition {{
            font-size: 13px;
            color: #7a8190;
            margin-top: 3px;
        }}

        .weather-temp {{
            font-size: 20px;
            font-weight: 700;
            line-height: 1.1;
            white-space: nowrap;
            color: #2f3345;
        }}

        .label {{
            font-size: 18px;
            color: #5f6675;
            margin-bottom: 10px;
            font-weight: 500;
        }}

        .clock {{
            font-size: 100px;
            font-weight: 700;
            line-height: 1;
            margin-bottom: 25px;
            color: #2f3345;
        }}

        .countdown {{
            font-size: 70px;
            font-weight: 700;
            line-height: 1;
            margin-bottom: 25px;
            color: #2f3345;
        }}

        .days {{
            font-size: 70px;
            font-weight: 700;
            line-height: 1;
            color: #2f3345;
            margin-bottom: 24px;
        }}

        .center-progress {{
            width: 100%;
            max-width: 520px;
            margin: 0 auto;
        }}

        .progress-bar {{
            width: 100%;
            height: 14px;
            background: #eceef2;
            border-radius: 999px;
            overflow: hidden;
            margin-bottom: 8px;
        }}

        .center-progress-bar {{
            margin-top: 2px;
        }}

        .progress-fill {{
            height: 100%;
            background: #2f3345;
            border-radius: 999px;
        }}

        .progress-text {{
            font-size: 16px;
            font-weight: 700;
            color: #2f3345;
        }}

        @media (max-width: 1100px) {{
            .left {{
                width: 36%;
                padding: 22px;
            }}

            .center {{
                width: 64%;
            }}

            .clock {{
                font-size: 82px;
            }}

            .countdown, .days {{
                font-size: 56px;
            }}
        }}

        @media (max-width: 768px) {{
            .page {{
                flex-direction: column;
            }}

            .left, .center {{
                width: 100%;
            }}

            .left {{
                padding: 20px;
            }}

            .center {{
                padding: 10px 20px 20px 20px;
            }}

            .logo img {{
                width: 180px;
            }}

            .clock {{
                font-size: 64px;
            }}

            .countdown, .days {{
                font-size: 42px;
            }}
        }}
    </style>
</head>
<body>
    <div class="page">
        <div class="left">
            <div class="section">
                <div class="section-title">Weather in our offices</div>
                {office_weather_html}
            </div>

            <div class="section">
                <div class="section-title">Weather in our properties</div>
                {property_weather_html}
            </div>
        </div>

        <div class="center">
            <div class="content">
                {logo_html}
                <div class="label">Current time</div>
                <div class="clock">{now.strftime("%H:%M")}</div>
                {countdown_html}
                <div class="label">Days until 7 November 2026</div>
                <div class="days">{days_remaining} days</div>
                {progress_bar}
            </div>
        </div>
    </div>
</body>
</html>
"""

components.html(html, height=700, scrolling=False)