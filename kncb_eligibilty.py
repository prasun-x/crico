# streamlit_app.py — KNCB Player Eligibility Checker Web App (No Recreational Division)
import streamlit as st
from datetime import datetime

def get_most_recent_division(division_data):
    for division, count in division_data:
        if count > 0:
            return division
    return "None"

def check_75_percent_rule(player_name, current, previous, use_previous):
    if use_previous:
        combined = [(div, current[div] + previous[div]) for div in current]
    else:
        combined = [(div, current[div]) for div in current]

    total_matches = sum(m for _, m in combined)
    if total_matches == 0:
        return "No matches played.", False, "None", 0

    most_recent_division = get_most_recent_division(combined)
    seen_recent = False
    lower_matches = 0
    for division, count in combined:
        if division == most_recent_division:
            seen_recent = True
            continue
        if seen_recent:
            lower_matches += count

    lower_percentage = (lower_matches / total_matches) * 100
    is_regular_lower = lower_percentage >= 75

    return lower_matches, is_regular_lower, most_recent_division, lower_percentage

def check_article_24(last_higher_date, next_lower_date, is_regular_lower):
    try:
        last = datetime.strptime(last_higher_date, "%Y-%m-%d")
        next = datetime.strptime(next_lower_date, "%Y-%m-%d")
    except ValueError:
        return "❌ Invalid date format. Use YYYY-MM-DD."

    delta = (next - last).days
    if is_regular_lower:
        return "✅ Article 24 not triggered — regular lower-team player."
    elif delta >= 8:
        return f"✅ Article 24 OK — {delta} days passed."
    else:
        return f"❌ Article 24 applies — only {delta} days. Dispensation needed."

def check_division_movement(source, target):
    order = {
        "Topklasse": 1,
        "Hoofdklasse": 2,
        "Eerste Klasse": 3,
        "Tweede Klasse": 4,
        "Derde Klasse": 5,
        "Vierde Klasse": 6
    }
    if source not in order or target not in order:
        return "❌ Invalid division names."
    if order[source] < order[target]:
        return "⬇️ Moving to lower division — Article 24 applies."
    elif order[source] > order[target]:
        return "⬆️ Moving up — freely allowed."
    else:
        return "➡️ Lateral movement — allowed."

# Streamlit UI
st.set_page_config(page_title="KNCB Player Eligibility Checker", layout="centered")
st.title("🏏 KNCB Player Eligibility Checker")

with st.form("player_form"):
    name = st.text_input("Player name")
    use_previous = st.checkbox("Include Previous Season Matches", value=True)

    st.markdown("### This Season")
    col1, col2 = st.columns(2)
    with col1:
        top_c = st.number_input("Topklasse (current)", 0)
        eerste_c = st.number_input("Eerste Klasse (current)", 0)
        derde_c = st.number_input("Derde Klasse (current)", 0)
    with col2:
        hoofd_c = st.number_input("Hoofdklasse (current)", 0)
        tweede_c = st.number_input("Tweede Klasse (current)", 0)
        vierde_c = st.number_input("Vierde Klasse (current)", 0)

    previous = {}
    if use_previous:
        st.markdown("### Previous Season")
        col3, col4 = st.columns(2)
        with col3:
            top_p = st.number_input("Topklasse (previous)", 0)
            eerste_p = st.number_input("Eerste Klasse (previous)", 0)
            derde_p = st.number_input("Derde Klasse (previous)", 0)
        with col4:
            hoofd_p = st.number_input("Hoofdklasse (previous)", 0)
            tweede_p = st.number_input("Tweede Klasse (previous)", 0)
            vierde_p = st.number_input("Vierde Klasse (previous)", 0)
    else:
        top_p = eerste_p = derde_p = hoofd_p = tweede_p = vierde_p = 0

    last_higher = st.date_input("Last higher match date")
    next_lower = st.date_input("Intended lower match date")

    source = st.selectbox("From division", ["Topklasse", "Hoofdklasse", "Eerste Klasse", "Tweede Klasse", "Derde Klasse", "Vierde Klasse"])
    target = st.selectbox("To division", ["Topklasse", "Hoofdklasse", "Eerste Klasse", "Tweede Klasse", "Derde Klasse", "Vierde Klasse"])

    submitted = st.form_submit_button("Check Eligibility")

if submitted:
    current = {
        "Topklasse": top_c,
        "Hoofdklasse": hoofd_c,
        "Eerste Klasse": eerste_c,
        "Tweede Klasse": tweede_c,
        "Derde Klasse": derde_c,
        "Vierde Klasse": vierde_c,
    }
    previous = {
        "Topklasse": top_p,
        "Hoofdklasse": hoofd_p,
        "Eerste Klasse": eerste_p,
        "Tweede Klasse": tweede_p,
        "Derde Klasse": derde_p,
        "Vierde Klasse": vierde_p,
    }
    lower_matches, is_lower, recent_div, percent = check_75_percent_rule(name, current, previous, use_previous)
    st.subheader("Eligibility Result")
    st.write(f"**Most Recent Higher Division Played:** {recent_div}")
    st.write(f"**Total Lower Division Matches:** {lower_matches}")
    st.write(f"**Lower Division %:** {percent:.2f}%")
    st.write(f"**Regular Lower-Team Player (Article 22):** {'✅ Yes' if is_lower else '❌ No'}")

    result = check_article_24(str(last_higher), str(next_lower), is_lower)
    st.subheader("Article 24 Check")
    st.write(result)

    move = check_division_movement(source, target)
    st.subheader("Division Movement Advice")
    st.write(move)
