import streamlit as st

# ------------- Session Setup -------------
if "meals" not in st.session_state:
    st.session_state.meals = {
        "Breakfast": {"Calories": 350, "Carbs": 60, "Protein": 10, "Fat": 5, "Time": "07:00 AM", "Details": "Oatmeal, Banana"},
        "Lunch": {"Calories": 500, "Carbs": 40, "Protein": 40, "Fat": 15, "Time": "12:30 PM", "Details": "Chicken, Rice"},
        "Dinner": {"Calories": 600, "Carbs": 45, "Protein": 45, "Fat": 25, "Time": "07:00 PM", "Details": "Salmon, Veggies"},
    }
if "selected_snack" not in st.session_state:
    st.session_state.selected_snack = ""
if "show_popup" not in st.session_state:
    st.session_state.show_popup = False

# ------------- Constants -------------
snack_options = {
    "Protein Shake": {"Calories": 550, "Carbs": 155, "Protein": 54, "Fat": 35},
    "Apple": {"Calories": 95, "Carbs": 25, "Protein": 0, "Fat": 0},
    "Peanut Butter": {"Calories": 190, "Carbs": 7, "Protein": 8, "Fat": 16},
}
macro_goals = {"Calories": 2000, "Carbs": 300, "Protein": 150, "Fat": 80}

# ------------- Helper Functions -------------
def compute_totals(meals):
    total = {"Calories": 0, "Carbs": 0, "Protein": 0, "Fat": 0}
    for meal in meals.values():
        for k in total:
            total[k] += meal.get(k, 0)
    return total

def add_snack():
    snack_name = st.session_state.selected_snack
    if not snack_name:
        return
    st.session_state.meals["Snack"] = {
        **snack_options[snack_name],
        "Time": "3:00 PM",
        "Details": snack_name
    }
    totals = compute_totals(st.session_state.meals)
    if abs(totals["Protein"] - macro_goals["Protein"]) == 1:
        st.session_state.show_popup = True

def close_popup():
    st.session_state.show_popup = False
    st.session_state.selected_snack = ""

# ------------- Styles -------------
st.markdown("""
<style>
.stApp > header, .stApp [data-testid="stToolbar"] {
    display: none !important;
}

html, body, .main, [class^="css"], .stApp {
    background-color: #0a0f1f !important;
    color: #f8fafc !important;
    padding: 0 !important;
    margin: 0 !important;
    padding-bottom: 60px !important;
}

.kpis-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1rem;
    margin-bottom: 1rem;
}

.kpi-box {
    background: #1e293b;
    border-radius: 12px;
    padding: 1rem;
    box-shadow: 0 2px 5px rgba(0,0,0,0.3);
}
.kpi-box:hover {
    box-shadow: 0 4px 10px rgba(0,0,0,0.4);
}

.meals-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1rem;
    margin-bottom: 1rem;
}

.meal-card {
    background: #1e293b;
    border-left: 4px solid #10b981;
    padding: 1rem;
    border-radius: 10px;
}

.progress {
    height: 8px;
    background: #334155;
    border-radius: 10px;
    overflow: hidden;
}
.progress > div {
    height: 100%;
    background: linear-gradient(90deg, #10b981, #22c55e);
}

.popup-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.7);
    z-index: 999;
    display: flex;
    justify-content: center;
    align-items: center;
}

.popup-box {
    background: #1e293b;
    padding: 2rem;
    border-radius: 15px;
    color: #10b981;
    box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    text-align: center;
    position: relative;
    z-index: 1001;
}

.popup-box button {
    margin-top: 1rem;
    background: #10b981;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    cursor: pointer;
}

.bottom-nav {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    background: #1e293b;
    display: flex;
    justify-content: space-around;
    padding: 0.5rem 0;
    z-index: 1000;
    box-shadow: 0 -2px 5px rgba(0,0,0,0.3);
}

.nav-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    color: #f8fafc;
    text-decoration: none;
    font-size: 0.9rem;
}

.nav-item.active {
    color: #10b981;
}

.nav-item svg {
    width: 24px;
    height: 24px;
    margin-bottom: 0.2rem;
}
</style>
<script>
document.addEventListener('click', function(e) {
    const popupBox = document.querySelector('.popup-box');
    if (popupBox && !popupBox.contains(e.target)) {
        const streamlitEvent = new Event("streamlit:close_popup");
        document.dispatchEvent(streamlitEvent);
    }
});
</script>
""", unsafe_allow_html=True)

# ------------- UI -------------
st.title("Gerich Hinzufügen")
st.subheader("Mittwoch, 2. Juli")

# KPIs
# KPIs
st.markdown("### 🧮 Nährwerte")

totals = compute_totals(st.session_state.meals)
kpi_items = [
    ("Kalorien", "Calories", "kcal"),
    ("Protein", "Protein", "g"),
    ("Kohlenhydrate", "Carbs", "g"),
    ("Fett", "Fat", "g")
]

# Render KPIs in rows of 2 columns each
for i in range(0, len(kpi_items), 2):
    cols = st.columns(2)
    for col, (label, key, unit) in zip(cols, kpi_items[i:i+2]):
        value = totals[key]
        goal = macro_goals[key]
        percent = min(100, int(value / goal * 100)) if goal else 0
        col.markdown(f"""
        <div class="kpi-box" style="min-width: 150px;">
            <strong>{label}</strong><br>
            {value} / {goal} {unit}
            <div class="progress"><div style="width:{percent}%"></div></div>
        </div>
        """, unsafe_allow_html=True)


# Meals
st.markdown("### 🍽️ Mahlzeiten")
st.markdown('<div class="meals-grid">', unsafe_allow_html=True)
for name, data in st.session_state.meals.items():
    st.markdown(f"""
    <div class="meal-card">
        <strong>{name}</strong> – {data["Time"]}<br>
        <em>{data["Details"]}</em><br>
        {data["Calories"]} kcal | {data["Carbs"]}g C | {data["Protein"]}g P | {data["Fat"]}g F
    </div>
    """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Snack Selector
st.markdown("### ➕ Gericht hinzufügen")
st.selectbox("", [""] + list(snack_options.keys()), key="selected_snack", on_change=add_snack)

# Popup
if st.session_state.show_popup:
    st.markdown(f"""
    <div class="popup-overlay">
        <div class="popup-box">
            🎯 Du bist 1g vom Protein-Ziel entfernt, starke Leistung!
            <button onclick="this.closest('.popup-overlay').style.display='none';">Schließen</button>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # JavaScript for popup close
    js_event = """
    <script>
    document.addEventListener("streamlit:close_popup", function() {
        fetch("/", {method: "POST", body: JSON.stringify({type: "close_popup"})});
    });
    </script>
    """
    st.markdown(js_event, unsafe_allow_html=True)

    # Handle close event
    if st.experimental_get_query_params().get("event") == ["close_popup"]:
        close_popup()
        st.rerun()

# Bottom Navigation
st.markdown("""
<div class="bottom-nav">
    <div class="nav-item active">
        <svg viewBox="0 0 24 24" fill="currentColor"><path d="M4 4h16v2H4zm0 4h16v12H4zm6 4h4v4h-4z"/></svg>
        Food
    </div>
    <div class="nav-item">
        <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2a10 10 0 100 20 10 10 0 000-20zm0 18a8 8 0 110-16 8 8 0 010 16zm4-8h-3V9h-2v3H8v2h3v3h2v-3h3z"/></svg>
        Weights
    </div>
    <div class="nav-item">
        <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>
        Profile
    </div>
</div>
""", unsafe_allow_html=True)