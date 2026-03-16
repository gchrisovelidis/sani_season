import streamlit as st
from datetime import datetime, date, time
from zoneinfo import ZoneInfo
from pathlib import Path

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
)

# Auto-refresh every second
st.markdown(
    """
    <meta http-equiv="refresh" content="1">
    """,
    unsafe_allow_html=True,
)

# -----------------------
# Styling
# -----------------------
st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1.2rem;
            padding-bottom: 1.2rem;
            padding-left: 2rem;
            padding-right: 2rem;
            max-width: 1000px;
        }

        .logo-wrap {
            margin-bottom: 2.5rem;
        }

        .label {
            font-size: 1rem;
            color: #6b7280;
            margin-bottom: 0.2rem;
            font-weight: 500;
        }

        .clock {
            font-size: 5rem;
            font-weight: 700;
            line-height: 1.05;
            margin-bottom: 2rem;
        }

        .countdown {
            font-size: 4rem;
            font-weight: 700;
            line-height: 1.05;
            margin-bottom: 2rem;
        }

        .days {
            font-size: 4rem;
            font-weight: 700;
            line-height: 1.05;
        }

        @media (max-width: 768px) {
            .clock {
                font-size: 3.2rem;
            }

            .countdown, .days {
                font-size: 2.5rem;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------
# Time calculations
# -----------------------
now = datetime.now(ZoneInfo(TIMEZONE))
today = now.date()
current_time = now.time().replace(microsecond=0)

days_remaining = (TARGET_DATE - today).days

show_countdown = START_SHOW_TIME <= current_time <= END_SHOW_TIME

if show_countdown:
    target_dt = datetime.combine(today, END_SHOW_TIME, tzinfo=ZoneInfo(TIMEZONE))
    remaining = target_dt - now

    total_seconds = max(int(remaining.total_seconds()), 0)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60

    countdown_text = f"{hours}h {minutes:02d}m"

# -----------------------
# UI
# -----------------------
logo_file = Path(LOGO_PATH)
if logo_file.exists():
    st.markdown('<div class="logo-wrap">', unsafe_allow_html=True)
    st.image(str(logo_file), width=220)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="label">Current time</div>', unsafe_allow_html=True)
st.markdown(f'<div class="clock">{now.strftime("%H:%M:%S")}</div>', unsafe_allow_html=True)

if show_countdown:
    st.markdown('<div class="label">Time until 17:30</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="countdown">{countdown_text}</div>', unsafe_allow_html=True)

st.markdown('<div class="label">Days until 30 October 2026</div>', unsafe_allow_html=True)
st.markdown(f'<div class="days">{days_remaining} days</div>', unsafe_allow_html=True)