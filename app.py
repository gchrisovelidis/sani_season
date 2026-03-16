import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime, date, time
from zoneinfo import ZoneInfo
from pathlib import Path
import base64

# -----------------------
# Config
# -----------------------
TARGET_DATE = date(2026, 10, 30)
START_SHOW_TIME = time(9, 0)
END_SHOW_TIME = time(17, 30)
TIMEZONE = "Europe/Athens"
LOGO_PATH = "logo.png"

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

logo_html = ""
logo_b64 = get_logo_base64(LOGO_PATH)
if logo_b64:
    logo_html = f"""
        <div class="logo">
            <img src="data:image/png;base64,{logo_b64}" alt="Logo">
        </div>
    """

html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        html, body {{
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            background: white;
            font-family: Arial, Helvetica, sans-serif;
        }}

        .page {{
            width: 100%;
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: white;
        }}

        .content {{
            width: 100%;
            max-width: 900px;
            text-align: center;
            padding: 20px;
            box-sizing: border-box;
        }}

        .logo {{
            margin-bottom: 24px;
        }}

        .logo img {{
            width: 230px;
            max-width: 60vw;
            height: auto;
            pointer-events: none;
            user-select: none;
            -webkit-user-drag: none;
        }}

        .label {{
            font-size: 18px;
            color: #5f6675;
            margin-bottom: 10px;
            font-weight: 500;
        }}

        .clock {{
            font-size: 102px;
            font-weight: 700;
            line-height: 1;
            color: #2f3345;
            margin-bottom: 28px;
        }}

        .countdown {{
            font-size: 72px;
            font-weight: 700;
            line-height: 1;
            color: #2f3345;
            margin-bottom: 28px;
        }}

        .days {{
            font-size: 72px;
            font-weight: 700;
            line-height: 1;
            color: #2f3345;
            margin-bottom: 0;
        }}

        @media (max-width: 768px) {{
            .logo img {{
                width: 180px;
            }}

            .clock {{
                font-size: 72px;
            }}

            .countdown, .days {{
                font-size: 48px;
            }}

            .label {{
                font-size: 16px;
            }}
        }}
    </style>
</head>
<body>
    <div class="page">
        <div class="content">
            {logo_html}
            <div class="label">Current time</div>
            <div class="clock">{now.strftime("%H:%M")}</div>
            {countdown_html}
            <div class="label">Days until 30 October 2026</div>
            <div class="days">{days_remaining} days</div>
        </div>
    </div>
</body>
</html>
"""

components.html(html, height=500, scrolling=False)