import base64
from datetime import date, datetime, time
from pathlib import Path
from string import Template
from zoneinfo import ZoneInfo

import requests
import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(
    page_title="Sani Season",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    footer {visibility: hidden;}
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

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
    "Kos": "Kos, South Aegean, Greece",
    "Crete": "Heraklion,GR",
    "Marbella": "Marbella,ES",
    "Mallorca": "Palma,ES",
}

BANK_HOLIDAYS = [
    (date(2026, 1, 1), "New Year's Day"),
    (date(2026, 1, 6), "Θεοφάνεια"),
    (date(2026, 2, 23), "Καθαρά Δευτέρα"),
    (date(2026, 3, 25), "25η Μαρτίου"),
    (date(2026, 4, 13), "Δευτέρα του Πάσχα"),
    (date(2026, 5, 1), "Πρωτομαγιά"),
    (date(2026, 8, 15), "Κοίμηση της Θεοτόκου"),
    (date(2026, 10, 28), "28η Οκτωβρίου"),
    (date(2026, 12, 25), "Χριστούγεννα"),
    (date(2026, 12, 26), "2η μέρα Χριστουγέννων"),
]

STICKER_RULES = [
    (20, "Sticker1.png"),
    (40, "Sticker2.png"),
    (60, "Sticker3.png"),
    (80, "Sticker4.png"),
    (100, "Sticker5.png"),
]

# -----------------------
# Helpers
# -----------------------
def get_image_base64(path: str) -> str:
    file_path = Path(path)
    if not file_path.exists():
        return ""
    return base64.b64encode(file_path.read_bytes()).decode()


def get_logo_base64(path: str) -> str:
    return get_image_base64(path)


def get_progress_sticker_path(progress_pct: float) -> str:
    for limit, path in STICKER_RULES:
        if progress_pct <= limit:
            return path
    return STICKER_RULES[-1][1]


def get_weather_icon_svg(weather: str) -> str:
    weather = (weather or "").strip()

    icons = {
        "Clear": """
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <circle cx="12" cy="12" r="4.2" fill="#F5B301"></circle>
              <g stroke="#F5B301" stroke-width="1.8" stroke-linecap="round">
                <line x1="12" y1="2.5" x2="12" y2="5.2"></line>
                <line x1="12" y1="18.8" x2="12" y2="21.5"></line>
                <line x1="2.5" y1="12" x2="5.2" y2="12"></line>
                <line x1="18.8" y1="12" x2="21.5" y2="12"></line>
                <line x1="5.2" y1="5.2" x2="7.1" y2="7.1"></line>
                <line x1="16.9" y1="16.9" x2="18.8" y2="18.8"></line>
                <line x1="16.9" y1="7.1" x2="18.8" y2="5.2"></line>
                <line x1="5.2" y1="18.8" x2="7.1" y2="16.9"></line>
              </g>
            </svg>
        """,
        "Clouds": """
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <ellipse cx="10" cy="13.2" rx="5.2" ry="3.4" fill="#C8D0DF"></ellipse>
              <ellipse cx="14.8" cy="12.8" rx="4.5" ry="3.1" fill="#B5C0D3"></ellipse>
              <ellipse cx="7.2" cy="14.1" rx="3.2" ry="2.5" fill="#D6DDE9"></ellipse>
            </svg>
        """,
        "Rain": """
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <ellipse cx="10" cy="10.8" rx="5.2" ry="3.4" fill="#C8D0DF"></ellipse>
              <ellipse cx="14.8" cy="10.4" rx="4.5" ry="3.1" fill="#B5C0D3"></ellipse>
              <g stroke="#4A90E2" stroke-width="1.8" stroke-linecap="round">
                <line x1="8" y1="15.2" x2="6.8" y2="18.2"></line>
                <line x1="12" y1="15.2" x2="10.8" y2="18.2"></line>
                <line x1="16" y1="15.2" x2="14.8" y2="18.2"></line>
              </g>
            </svg>
        """,
        "Drizzle": """
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <ellipse cx="10" cy="10.8" rx="5.2" ry="3.4" fill="#C8D0DF"></ellipse>
              <ellipse cx="14.8" cy="10.4" rx="4.5" ry="3.1" fill="#B5C0D3"></ellipse>
              <g stroke="#67A7EF" stroke-width="1.5" stroke-linecap="round">
                <line x1="9" y1="15.5" x2="8.2" y2="17.4"></line>
                <line x1="13" y1="15.5" x2="12.2" y2="17.4"></line>
                <line x1="17" y1="15.5" x2="16.2" y2="17.4"></line>
              </g>
            </svg>
        """,
        "Thunderstorm": """
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <ellipse cx="10" cy="10.8" rx="5.2" ry="3.4" fill="#C8D0DF"></ellipse>
              <ellipse cx="14.8" cy="10.4" rx="4.5" ry="3.1" fill="#B5C0D3"></ellipse>
              <polygon points="12,14.4 9.5,18.6 12.4,18.6 10.8,21.4 15.2,16.6 12.4,16.6 14,14.4" fill="#F5B301"></polygon>
            </svg>
        """,
        "Snow": """
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <ellipse cx="10" cy="10.8" rx="5.2" ry="3.4" fill="#C8D0DF"></ellipse>
              <ellipse cx="14.8" cy="10.4" rx="4.5" ry="3.1" fill="#B5C0D3"></ellipse>
              <g stroke="#7FB7FF" stroke-width="1.4" stroke-linecap="round">
                <line x1="8" y1="15.4" x2="8" y2="18.2"></line>
                <line x1="6.6" y1="16.8" x2="9.4" y2="16.8"></line>
                <line x1="12.5" y1="15.4" x2="12.5" y2="18.2"></line>
                <line x1="11.1" y1="16.8" x2="13.9" y2="16.8"></line>
                <line x1="16.5" y1="15.4" x2="16.5" y2="18.2"></line>
                <line x1="15.1" y1="16.8" x2="17.9" y2="16.8"></line>
              </g>
            </svg>
        """,
        "Mist": """
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <g stroke="#B8C2D1" stroke-width="1.8" stroke-linecap="round">
                <line x1="5" y1="8" x2="19" y2="8"></line>
                <line x1="3.5" y1="12" x2="17.5" y2="12"></line>
                <line x1="6.5" y1="16" x2="20.5" y2="16"></line>
              </g>
            </svg>
        """,
        "Fog": """
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <g stroke="#B8C2D1" stroke-width="1.8" stroke-linecap="round">
                <line x1="5" y1="8" x2="19" y2="8"></line>
                <line x1="3.5" y1="12" x2="17.5" y2="12"></line>
                <line x1="6.5" y1="16" x2="20.5" y2="16"></line>
              </g>
            </svg>
        """,
        "Haze": """
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <g stroke="#B8C2D1" stroke-width="1.8" stroke-linecap="round">
                <line x1="5" y1="8" x2="19" y2="8"></line>
                <line x1="3.5" y1="12" x2="17.5" y2="12"></line>
                <line x1="6.5" y1="16" x2="20.5" y2="16"></line>
              </g>
            </svg>
        """,
        "Unavailable": """
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <circle cx="12" cy="12" r="4" fill="#D3D8E2"></circle>
            </svg>
        """,
    }

    return icons.get(
        weather,
        """
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <circle cx="9" cy="9" r="3.6" fill="#F5B301"></circle>
          <ellipse cx="12" cy="13.2" rx="5.2" ry="3.4" fill="#C8D0DF"></ellipse>
          <ellipse cx="16.2" cy="12.9" rx="4.1" ry="2.8" fill="#B5C0D3"></ellipse>
        </svg>
        """,
    )


def get_weather_temp_class(temp_value) -> str:
    if temp_value is None:
        return "temp-unavailable"
    if temp_value <= 10:
        return "temp-cold"
    if temp_value <= 19:
        return "temp-mild"
    if temp_value <= 27:
        return "temp-warm"
    return "temp-hot"


def get_weather_condition_class(weather: str) -> str:
    weather = (weather or "").strip().lower()

    mapping = {
        "clear": "cond-clear",
        "clouds": "cond-clouds",
        "rain": "cond-rain",
        "drizzle": "cond-drizzle",
        "thunderstorm": "cond-thunderstorm",
        "snow": "cond-snow",
        "mist": "cond-mist",
        "fog": "cond-mist",
        "haze": "cond-mist",
        "unavailable": "cond-unavailable",
    }
    return mapping.get(weather, "cond-default")


@st.cache_data(ttl=600, show_spinner=False)
def fetch_weather(query: str, api_key: str) -> dict:
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": query,
        "appid": api_key,
        "units": "metric",
    }
    response = requests.get(url, params=params, timeout=10)
    return {
        "status_code": response.status_code,
        "json": response.json(),
    }


def get_weather_for_city(query: str) -> dict:
    try:
        result = fetch_weather(query, API_KEY)
        status_code = result["status_code"]
        data = result["json"]

        if status_code != 200:
            return {
                "temp": "—",
                "temp_value": None,
                "temp_class": get_weather_temp_class(None),
                "weather": "Unavailable",
                "condition_class": get_weather_condition_class("Unavailable"),
                "icon": get_weather_icon_svg("Unavailable"),
            }

        temp = round(data["main"]["temp"])
        weather = data["weather"][0]["main"]
        icon = get_weather_icon_svg(weather)

        return {
            "temp": f"{temp}°C",
            "temp_value": temp,
            "temp_class": get_weather_temp_class(temp),
            "weather": weather,
            "condition_class": get_weather_condition_class(weather),
            "icon": icon,
        }

    except Exception:
        return {
            "temp": "—",
            "temp_value": None,
            "temp_class": get_weather_temp_class(None),
            "weather": "Unavailable",
            "condition_class": get_weather_condition_class("Unavailable"),
            "icon": get_weather_icon_svg("Unavailable"),
        }


def render_weather_rows(locations: dict, office: bool = False) -> str:
    rows = []
    for label, query in locations.items():
        info = get_weather_for_city(query)
        row_class = "office-row" if office else "weather-row"
        rows.append(
            f"""
            <div class="{row_class}">
                <div class="weather-left">
                    <div class="weather-city">{label}</div>
                    <div class="weather-condition {info["condition_class"]}">
                        <span class="weather-icon">{info["icon"]}</span>
                        <span>{info["weather"]}</span>
                    </div>
                </div>
                <div class="weather-temp {info["temp_class"]}">{info["temp"]}</div>
            </div>
            """
        )
    return "".join(rows)


def get_next_holiday(today_: date):
    future_holidays = [(d, name) for d, name in BANK_HOLIDAYS if d >= today_]
    if not future_holidays:
        return None, None, None
    next_date, next_name = min(future_holidays, key=lambda x: x[0])
    days_left = (next_date - today_).days
    return next_name, next_date, days_left


def get_holiday_alert_class(days_left) -> str:
    if days_left is None:
        return ""
    if days_left < 3:
        return "alert-danger"
    if days_left <= 7:
        return "alert-warning"
    return "alert-normal"


def get_weekend_indicator(today_: date):
    weekday = today_.weekday()

    if weekday >= 5:
        return {
            "title": "Weekend Indicator",
            "name": "Weekend",
            "days_text": "Today",
            "is_weekend": True,
            "alert_class": "alert-weekend",
        }

    days_to_saturday = 5 - weekday

    if days_to_saturday == 1:
        text = "Tomorrow"
        alert_class = "alert-warning"
    else:
        text = f"{days_to_saturday} days"
        alert_class = "alert-normal"

    return {
        "title": "Weekend Indicator",
        "name": "Next weekend",
        "days_text": text,
        "is_weekend": False,
        "alert_class": alert_class,
    }


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

sticker_path = get_progress_sticker_path(progress)
sticker_b64 = get_image_base64(sticker_path)

sticker_html = ""
if sticker_b64:
    sticker_html = f"""
    <div class="progress-sticker-wrap">
        <img src="data:image/png;base64,{sticker_b64}" alt="Progress Sticker" class="progress-sticker">
    </div>
    """

progress_bar = f"""
<div class="center-progress">
    <div class="label">Season Progress</div>
    <div class="progress-bar center-progress-bar">
        <div class="progress-fill" style="width:{progress}%"></div>
    </div>
    <div class="progress-text">{progress}%</div>
    {sticker_html}
</div>
"""

# -----------------------
# Bank Holiday
# -----------------------
holiday_name, holiday_date, holiday_days = get_next_holiday(today)
holiday_alert_class = get_holiday_alert_class(holiday_days)

holiday_html = ""
if holiday_name is not None:
    day_label = "day" if holiday_days == 1 else "days"
    holiday_html = f"""
    <div class="section holiday-section">
        <div class="section-title">Next Bank Holiday</div>
        <div class="holiday-name {holiday_alert_class}">{holiday_name}</div>
        <div class="holiday-days {holiday_alert_class}">{holiday_days} {day_label}</div>
    </div>
    """

# -----------------------
# Weekend
# -----------------------
weekend = get_weekend_indicator(today)

weekend_html = f"""
<div class="section weekend-section">
    <div class="section-title">{weekend["title"]}</div>
    <div class="weekend-name {weekend["alert_class"]}">{weekend["name"]}</div>
    <div class="weekend-days {weekend["alert_class"]}">{weekend["days_text"]}</div>
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
html_template = Template(
    """
<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="refresh" content="60">
    <meta charset="utf-8">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        html, body {
            margin: 0;
            padding: 0;
            height: 100%;
            overflow: hidden;
            background: white;
            font-family: 'Inter', Arial, Helvetica, sans-serif;
            color: #2f3345;
        }

        .page {
            display: flex;
            width: 100%;
            height: 100vh;
            background: white;
        }

        .left {
            width: 34%;
            padding: 24px 28px 20px 32px;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
        }

        .center {
            width: 66%;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 10px 20px;
            box-sizing: border-box;
        }

        .content {
            text-align: center;
            width: 100%;
            max-width: 760px;
        }

        .logo {
            margin-bottom: 18px;
        }

        .logo img {
            width: 220px;
            max-width: 60vw;
            height: auto;
            pointer-events: none;
            user-select: none;
            -webkit-user-drag: none;
        }

        .section {
            margin-bottom: 16px;
        }

        .section-title {
            font-size: 13px;
            font-weight: 700;
            color: #7a8190;
            text-transform: uppercase;
            letter-spacing: 0.7px;
            margin-bottom: 12px;
        }

        .section-divider {
            height: 1px;
            background: #e6e9ef;
            margin: 12px 0 14px 0;
        }

        .office-row,
        .weather-row {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 16px;
            margin-bottom: 8px;
        }

        .weather-left {
            text-align: left;
        }

        .weather-city {
            font-size: 17px;
            font-weight: 600;
            line-height: 1.2;
            color: #2f3345;
        }

        .weather-condition {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 13px;
            margin-top: 3px;
            font-weight: 500;
        }

        .weather-icon {
            display: inline-flex;
            width: 16px;
            height: 16px;
            flex: 0 0 16px;
        }

        .weather-icon svg {
            width: 16px;
            height: 16px;
            display: block;
        }

        .weather-temp {
            font-size: 20px;
            font-weight: 700;
            line-height: 1.1;
            white-space: nowrap;
        }

        .temp-cold {
            color: #2563EB;
            font-weight: 800;
        }

        .temp-mild {
            color: #475569;
        }

        .temp-warm {
            color: #F59E0B;
        }

        .temp-hot {
            color: #DC2626;
            font-weight: 800;
        }

        .temp-unavailable {
            color: #9CA3AF;
        }

        .cond-clear {
            color: #F59E0B;
        }

        .cond-clouds {
            color: #7B8798;
        }

        .cond-rain {
            color: #2563EB;
        }

        .cond-drizzle {
            color: #60A5FA;
        }

        .cond-thunderstorm {
            color: #6D28D9;
        }

        .cond-snow {
            color: #93C5FD;
        }

        .cond-mist {
            color: #9CA3AF;
        }

        .cond-unavailable,
        .cond-default {
            color: #9CA3AF;
        }

        .holiday-section,
        .weekend-section {
            margin-top: 4px;
        }

        .holiday-name,
        .weekend-name {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 6px;
        }

        .holiday-days,
        .weekend-days {
            font-size: 20px;
            font-weight: 700;
        }

        .alert-normal {
            color: #2F3345;
        }

        .alert-warning {
            color: #D97706;
        }

        .alert-danger {
            color: #C2410C;
        }

        .alert-weekend {
            color: #2E8B57;
        }

        .progress-bar {
            width: 100%;
            height: 14px;
            background: #E8EDF5;
            border-radius: 999px;
            overflow: hidden;
            margin-bottom: 8px;
            box-shadow: inset 0 1px 2px rgba(32, 55, 95, 0.06);
        }

        .center-progress-bar {
            margin-top: 2px;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #1F5FAE 0%, #4A90E2 100%);
            border-radius: 999px;
        }

        .progress-text {
            font-size: 16px;
            font-weight: 700;
            color: #2f3345;
        }

        .progress-sticker-wrap {
            text-align: center;
            margin-top: 14px;
        }

        .progress-sticker {
            width: 120px;
            height: 120px;
            object-fit: contain;
            display: inline-block;
            pointer-events: none;
            user-select: none;
            -webkit-user-drag: none;
        }

        @media (max-width: 1100px) {
            .left {
                width: 36%;
                padding: 22px;
            }

            .center {
                width: 64%;
            }

            .clock,
            .countdown,
            .days {
                font-size: 56px;
            }

            .progress-sticker {
                width: 105px;
                height: 105px;
            }
        }

        @media (max-width: 768px) {
            .page {
                flex-direction: column;
            }

            .left, .center {
                width: 100%;
            }

            .left {
                padding: 20px;
            }

            .center {
                padding: 10px 20px 20px 20px;
            }

            .logo img {
                width: 180px;
            }

            .clock,
            .countdown,
            .days {
                font-size: 42px;
            }

            .progress-sticker {
                width: 95px;
                height: 95px;
            }
        }

        .label {
            font-size: 18px;
            color: #5F6675;
            margin-bottom: 10px;
            font-weight: 500;
        }

        .clock,
        .countdown,
        .days {
            font-size: 70px;
            font-weight: 700;
            line-height: 1;
            color: #2F3345;
        }

        .clock,
        .countdown {
            margin-bottom: 25px;
        }

        .days {
            margin-bottom: 24px;
        }

        .progress-text {
            font-size: 16px;
            font-weight: 700;
            color: #2F3345;
        }
    </style>
</head>
<body>
    <div class="page">
        <div class="left">
            <div class="section">
                <div class="section-title">Weather in our offices</div>
                $office_weather_html
            </div>

            <div class="section-divider"></div>

            <div class="section">
                <div class="section-title">Weather in our properties</div>
                $property_weather_html
            </div>

            <div class="section-divider"></div>

            $holiday_html

            <div class="section-divider"></div>

            $weekend_html
        </div>

        <div class="center">
            <div class="content">
                $logo_html
                <div class="label">Current time</div>
                <div class="clock">$current_time_text</div>
                $countdown_html
                <div class="label">Days until 7 November 2026</div>
                <div class="days">$days_remaining_text</div>
                $progress_bar
            </div>
        </div>
    </div>
</body>
</html>
"""
)

html = html_template.substitute(
    office_weather_html=office_weather_html,
    property_weather_html=property_weather_html,
    holiday_html=holiday_html,
    weekend_html=weekend_html,
    logo_html=logo_html,
    current_time_text=now.strftime("%H:%M"),
    countdown_html=countdown_html,
    days_remaining_text=f"{days_remaining} days",
    progress_bar=progress_bar,
)

components.html(html, height=760, scrolling=False)