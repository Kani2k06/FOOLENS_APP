import streamlit as st
import pandas as pd
from datetime import datetime


# --- Page Config ---
st.set_page_config(page_title="Food Lens - NGO & Donor Portal", layout="wide")

# --- Theme Colors ---
color_dark_green = "#1B5E20"   # Header & buttons
color_light_green = "#A5D6A7"  # Table borders
color_cream = "#FAF9F6"        # Background
color_text_dark = "#1C1C1C"    # Dark text for contrast
color_red = "#D32F2F"          # Error
color_gold = "#FFB300"         # Highlight / accents

# --- Custom CSS ---
st.markdown(f"""
    <style>
    .stApp {{
        background-color: {color_cream};
        font-family: 'Helvetica', sans-serif;
        color: {color_text_dark};
    }}
    h1, h2, h3 {{
        color: {color_dark_green} !important;
    }}
    label, .stTextInput label, .stTextArea label, .stNumberInput label {{
        color: {color_text_dark} !important;
        font-weight: 600;
    }}
    .header-cell {{
        background-color: {color_dark_green};
        color: {color_cream};
        font-weight: bold;
        text-align: center;
        padding: 8px;
        border-radius: 5px;
    }}
    .data-cell {{
        background-color: {color_cream};
        border: 1px solid {color_light_green};
        border-radius: 5px;
        padding: 6px;
        text-align: center;
        font-weight: 600;
        color: {color_text_dark};
        box-shadow: 0px 1px 4px rgba(0,0,0,0.1);
    }}
    .stButton>button {{
        background-color: {color_dark_green};
        color: {color_cream};
        font-weight: bold;
        border-radius: 8px;
        height: 40px;
        width: 180px;
    }}
    </style>
""", unsafe_allow_html=True)

# --- Initialize Data ---
if "donor_df" not in st.session_state:
    st.session_state.donor_df = pd.DataFrame(
        columns=["id", "organization", "address", "menu", "expiry", "location", "quantity", "date"]
    )

donor_df = st.session_state.donor_df

# --- Session Navigation ---
if "page" not in st.session_state:
    st.session_state.page = "home"

# -------------------- PAGES -------------------- #

# --- Home Page ---
if st.session_state.page == "home":
    st.title("🍽 Welcome to Food Lens")
    st.markdown("## 🌱 Connecting Donors, NGOs & Hearts")
    st.write("At *Food Lens*, we fight hunger by connecting surplus food from donors "
             "to NGOs & people in need. Together, let’s build a zero-waste, zero-hunger community. 💚")

    if st.button("🚀 Get Started"):
        st.session_state.page = "select_role"
        st.rerun()

# --- Role Selection ---
elif st.session_state.page == "select_role":
    st.title("🙌 Choose Your Role")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🍴 Donor"):
            st.session_state.page = "donor"
            st.rerun()
    with col2:
        if st.button("🏢 NGO / Acceptor"):
            st.session_state.page = "acceptor"
            st.rerun()
    with col3:
        if st.button("📊 Analysis"):
            st.session_state.page = "analysis"
            st.rerun()

    if st.button("⬅ Back to Home"):
        st.session_state.page = "home"
        st.rerun()

# --- Donor Page ---
elif st.session_state.page == "donor":
    st.title("🍴 Donor Portal")
    st.subheader("Enter Food Availability Details")

    with st.form("donor_form", clear_on_submit=True):
        org_name = st.text_input("🏢 Organization Name")
        address = st.text_area("📍 Address")
        menu = st.text_input("🍛 Menu (Food Description)")
        expiry = st.text_input("⏰ Expiry / Time Limit (e.g., 2 PM - 5 PM)")
        location = st.text_input("🌍 Location (City / Area)")
        quantity = st.number_input("🥗 Quantity (No. of meals)", min_value=1, step=1)

        submitted = st.form_submit_button("➕ Submit Food")
        if submitted:
            if org_name and address and menu and expiry and location and quantity:
                new_id = len(donor_df) + 1
                new_entry = {
                    "id": new_id,
                    "organization": org_name,
                    "address": address,
                    "menu": menu,
                    "expiry": expiry,
                    "location": location,
                    "quantity": quantity,
                    "date": datetime.now().strftime("%Y-%m-%d")
                }
                st.session_state.donor_df = pd.concat([donor_df, pd.DataFrame([new_entry])], ignore_index=True)
                st.markdown(
                    f"<div style='background-color:#d4edda; color:{color_text_dark}; "
                    f"padding:10px; border-radius:5px; font-weight:700;'>🎉 Food details submitted successfully for {org_name}!</div>",
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"<div style='background-color:#f8d7da; color:{color_text_dark}; "
                    f"padding:10px; border-radius:5px; font-weight:700;'>⚠ Please fill all fields before submitting.</div>",
                    unsafe_allow_html=True
                )

    st.subheader("Current Food Availability")
    if not st.session_state.donor_df.empty:
        cols = st.columns([1, 2, 3, 2, 2, 2, 1, 2])
        headers = ["ID", "Organization", "Address", "Menu", "Expiry", "Location", "Qty", "Date"]
        for col, head in zip(cols, headers):
            col.markdown(f"<div class='header-cell'>{head}</div>", unsafe_allow_html=True)

        for _, row in st.session_state.donor_df.iterrows():
            cols = st.columns([1, 2, 3, 2, 2, 2, 1, 2])
            cols[0].markdown(f"<div class='data-cell'>{row['id']}</div>", unsafe_allow_html=True)
            cols[1].markdown(f"<div class='data-cell'>{row['organization']}</div>", unsafe_allow_html=True)
            cols[2].markdown(f"<div class='data-cell'>{row['address']}</div>", unsafe_allow_html=True)
            cols[3].markdown(f"<div class='data-cell'>{row['menu']}</div>", unsafe_allow_html=True)
            cols[4].markdown(f"<div class='data-cell'>{row['expiry']}</div>", unsafe_allow_html=True)
            cols[5].markdown(f"<div class='data-cell'>{row['location']}</div>", unsafe_allow_html=True)
            cols[6].markdown(f"<div class='data-cell'>{row['quantity']}</div>", unsafe_allow_html=True)
            cols[7].markdown(f"<div class='data-cell'>{row['date']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(
            f"<div style='background-color:#e2e3e5; color:{color_text_dark}; "
            f"padding:10px; border-radius:5px; font-weight:700;'>ℹ No food details submitted yet.</div>",
            unsafe_allow_html=True
        )

    if st.button("⬅ Back"):
        st.session_state.page = "select_role"
        st.rerun()

# --- Acceptor Page ---
elif st.session_state.page == "acceptor":
    st.title("🏢 NGO / Acceptor Portal")
    st.subheader("💡 Verified NGOs can pick food from donors")

    ngo_id = st.text_input("🔑 Enter your NGO Registration Number")
    if st.button("Verify NGO"):
        recognized_ngos = ["NGO1001", "NGO1002", "NGO1003"]
        if ngo_id in recognized_ngos:
            st.markdown(
                f"<div style='background-color:#d4edda; color:{color_text_dark}; "
                f"padding:10px; border-radius:5px; font-weight:700;'>✅ NGO Verified! You can access available food.</div>",
                unsafe_allow_html=True
            )
            st.session_state['ngo_verified'] = True
        else:
            st.markdown(
                f"<div style='background-color:#f8d7da; color:{color_text_dark}; "
                f"padding:10px; border-radius:5px; font-weight:700;'>❌ Your NGO is not recognized.</div>",
                unsafe_allow_html=True
            )
            st.session_state['ngo_verified'] = False

    if st.session_state.get('ngo_verified', False):
        if not st.session_state.donor_df.empty:
            st.subheader("📋 Available Food from Donors")
            # Table Header
            cols = st.columns([1, 2, 3, 2, 2, 2, 2, 2])
            headers = ["ID", "Organization", "Address", "Menu", "Expiry", "Location", "Qty Left", "Pick Qty"]
            for col, head in zip(cols, headers):
                col.markdown(f"<div class='header-cell'>{head}</div>", unsafe_allow_html=True)

            # Table Rows
            for _, row in st.session_state.donor_df.iterrows():
                cols = st.columns([1, 2, 3, 2, 2, 2, 2, 2])
                cols[0].markdown(f"<div class='data-cell'>{row['id']}</div>", unsafe_allow_html=True)
                cols[1].markdown(f"<div class='data-cell'>{row['organization']}</div>", unsafe_allow_html=True)
                cols[2].markdown(f"<div class='data-cell'>{row['address']}</div>", unsafe_allow_html=True)
                cols[3].markdown(f"<div class='data-cell'>{row['menu']}</div>", unsafe_allow_html=True)
                cols[4].markdown(f"<div class='data-cell'>{row['expiry']}</div>", unsafe_allow_html=True)
                cols[5].markdown(f"<div class='data-cell'>{row['location']}</div>", unsafe_allow_html=True)
                qty_left = row['quantity']
                cols[6].markdown(f"<div class='data-cell'>{qty_left if qty_left>0 else '❌'}</div>", unsafe_allow_html=True)

                if qty_left > 0:
                    qty_input = cols[7].text_input("", key=f"accept_qty_{row['id']}")
                    pick_btn = cols[7].button("Pick", key=f"pick_btn_{row['id']}")
                    if pick_btn:
                        if qty_input.isdigit():
                            qty = int(qty_input)
                            if 1 <= qty <= qty_left:
                                st.session_state.donor_df.loc[st.session_state.donor_df['id'] == row['id'], 'quantity'] -= qty
                                st.markdown(
                                    f"<div style='background-color:#d4edda; color:{color_text_dark}; "
                                    f"padding:10px; border-radius:5px; font-weight:700;'>🎉 You picked {qty} meals from {row['organization']}</div>",
                                    unsafe_allow_html=True
                                )
                            else:
                                st.markdown(
                                    f"<div style='background-color:#f8d7da; color:{color_text_dark}; "
                                    f"padding:10px; border-radius:5px; font-weight:700;'>⚠ Enter a quantity between 1 and {qty_left}</div>",
                                    unsafe_allow_html=True
                                )
                        else:
                            st.markdown(
                                f"<div style='background-color:#f8d7da; color:{color_text_dark}; "
                                f"padding:10px; border-radius:5px; font-weight:700;'>⚠ Please enter a valid number</div>",
                                unsafe_allow_html=True
                            )
        else:
            st.markdown(
                f"<div style='background-color:#e2e3e5; color:{color_text_dark}; "
                f"padding:10px; border-radius:5px; font-weight:700;'>ℹ No food available from donors yet.</div>",
                unsafe_allow_html=True
            )

    if st.button("⬅ Back"):
        st.session_state.page = "select_role"
        st.rerun()

# --- Analysis Page ---
elif st.session_state.page == "analysis":
    st.title("📊 Donation Analysis")
    if not st.session_state.donor_df.empty:
        df = st.session_state.donor_df.copy()

        st.subheader("✅ Overall Summary")
        total_meals = df['quantity'].sum()
        total_donations = len(df)
        st.markdown(f"- 🍽 **Total Meals Donated:** {total_meals}")
        st.markdown(f"- 🏢 **Total Donation Entries:** {total_donations}")

        st.subheader("🏢 Meals Donated by Organization")
        org_summary = df.groupby("organization")["quantity"].sum().reset_index()
        st.bar_chart(org_summary.set_index("organization"))

        st.subheader("📅 Donations Over Time")
        date_summary = df.groupby("date")["quantity"].sum().reset_index()
        st.line_chart(date_summary.set_index("date"))
    else:
        st.markdown(
            f"<div style='background-color:#e2e3e5; color:{color_text_dark}; "
            f"padding:10px; border-radius:5px; font-weight:700;'>ℹ No donation data available for analysis yet.</div>",
            unsafe_allow_html=True
        )

    if st.button("⬅ Back"):
        st.session_state.page = "select_role"
        st.rerun()
