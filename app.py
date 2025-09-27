import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import os

# ---------- CONFIG ----------
DB_PATH = "donations.db"

# ---------- UI THEME ----------
PRIMARY_COLOR = "#004d40"       # Dark Teal
SECONDARY_COLOR = "#f5f5f5"     # Light Gray
ACCENT_COLOR = "#ff7043"        # Orange for highlights
TEXT_COLOR = "#212121"          # Dark text for visibility

st.set_page_config(page_title="FoodLens - NGO & Donor Portal", layout="wide")

# ---------- CUSTOM CSS ----------
st.markdown(f"""
    <style>
    .stApp {{
        background-color: {SECONDARY_COLOR};
        font-family: 'Helvetica', sans-serif;
        color: {TEXT_COLOR} !important;
    }}
    h1, h2, h3 {{ color: {PRIMARY_COLOR} !important; }}
    label, .stTextInput label, .stTextArea label, .stNumberInput label {{
        color: {TEXT_COLOR} !important;
        font-weight: 600;
    }}
    .stButton>button {{
        background-color: {PRIMARY_COLOR};
        color: white !important;
        font-weight:bold;
        border-radius:8px;
        height:40px;
        width:180px;
    }}
    .st-download-button>button {{
        background-color: {ACCENT_COLOR};
        color:white !important;
        font-weight:bold;
        border-radius:8px;
        height:40px;
    }}
    .stDataFrame div {{
        color: {TEXT_COLOR} !important;
    }}
    .rewards-text {{
        color: black !important;
    }}
    </style>
""", unsafe_allow_html=True)

# ---------- DATABASE HELPERS ----------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS donations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            organization TEXT NOT NULL,
            address TEXT,
            menu TEXT,
            expiry TEXT,
            location TEXT,
            initial_quantity INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            date TEXT
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pickups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            donation_id INTEGER NOT NULL,
            ngo_id TEXT,
            picked_quantity INTEGER NOT NULL,
            picked_at TEXT,
            FOREIGN KEY(donation_id) REFERENCES donations(id)
        );
    """)
    conn.commit()
    conn.close()

def get_all_donations():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM donations ORDER BY id DESC", conn)
    conn.close()
    return df

def add_donation(org, addr, menu, expiry, loc, qty, date_str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO donations (organization,address,menu,expiry,location,initial_quantity,quantity,date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (org, addr, menu, expiry, loc, qty, qty, date_str))
    conn.commit()
    last_id = cur.lastrowid
    conn.close()
    return last_id

def update_quantity(donation_id, delta):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT quantity FROM donations WHERE id = ?", (donation_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return False, "Donation not found.", None
    current = int(row[0])
    new_qty = current + delta
    if new_qty < 0:
        conn.close()
        return False, "Not enough quantity available.", current
    cur.execute("UPDATE donations SET quantity = ? WHERE id = ?", (new_qty, donation_id))
    conn.commit()
    conn.close()
    return True, "Quantity updated.", new_qty

def log_pickup(donation_id, ngo_id, picked_qty):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO pickups (donation_id, ngo_id, picked_quantity, picked_at) VALUES (?, ?, ?, ?)",
                (donation_id, ngo_id, picked_qty, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

# ---------- REWARDS HELPERS ----------
def get_badge(points):
    if points >= 500:
        return "🏅 Gold"
    elif points >= 250:
        return "🥈 Silver"
    elif points >= 100:
        return "🥉 Bronze"
    else:
        return "✨ Starter"

def get_donor_points():
    df = get_all_donations()
    return df.groupby("organization")["initial_quantity"].sum().to_dict()

def get_ngo_points():
    conn = sqlite3.connect(DB_PATH)
    pickups = pd.read_sql_query("SELECT ngo_id, SUM(picked_quantity) as total_picked FROM pickups GROUP BY ngo_id", conn)
    conn.close()
    return dict(zip(pickups['ngo_id'], pickups['total_picked']))

# ---------- INIT ----------
init_db()
if "donor_df" not in st.session_state:
    st.session_state.donor_df = get_all_donations()

# ---------- SIDEBAR NAVIGATION ----------
st.sidebar.title("🍽 FoodLens")
menu = st.sidebar.radio("Navigation", ["Home", "Donor Portal", "NGO Portal", "Analysis", "Rewards"])

# ---------- PAGES ----------

# ----- HOME -----
if menu == "Home":
    st.markdown(
        """
        <div style="text-align: center; padding:20px;">
            <h1 style="color:#004d40; margin-bottom:10px;">🍽 Welcome to FoodLens</h1>
            <h3 style="color:#333; margin-top:0;">Objective</h3>
            <p style="font-size:16px; color:#555;">
                FoodLens aims to connect donors with NGOs efficiently to reduce food wastage and fight hunger.<br>
                Organizations can submit surplus food details, and NGOs can claim what they need in real-time.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Centered homepage image (width 300)
    image_path = "images/homepage.jpg"
    if os.path.exists(image_path):
        st.image(image_path, caption="Together, let's fight hunger", width=300)
    else:
        st.warning("⚠️ Homepage image not found. Please place an image at `images/homepage.jpg`")

    st.markdown(
        """
        <div style="text-align: center; margin-top:12px;">
            <p style="font-size:15px; color:#555;">
                Track donations, pickups, and analyze food distribution trends with ease.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

# ----- DONOR PORTAL -----
elif menu == "Donor Portal":
    st.title("Donor Portal 🍴")
    st.subheader("Submit Food Availability Details")
    with st.form("donor_form", clear_on_submit=True):
        org_name = st.text_input("Organization Name")
        address = st.text_area("Address")
        menu_desc = st.text_input("Menu (Food Description)")
        expiry = st.text_input("Expiry / Time Limit (e.g., 2 PM - 5 PM)")
        location = st.text_input("Location (City / Area)")
        quantity = st.number_input("Quantity (No. of meals)", min_value=1, step=1)
        submitted = st.form_submit_button("Submit Food")
    if submitted:
        if org_name and address and menu_desc and expiry and location and quantity:
            date_str = datetime.now().strftime("%Y-%m-%d")
            new_id = add_donation(org_name, address, menu_desc, expiry, location, int(quantity), date_str)
            st.session_state.donor_df = get_all_donations()
            st.success(f"Food submitted successfully for {org_name} (ID: {new_id})")
        else:
            st.error("Please fill all fields before submitting.")

    st.subheader("Current Food Availability")
    df = get_all_donations()
    if not df.empty:
        st.dataframe(df[['id','organization','address','menu','expiry','location','quantity','date']].rename(
            columns={'id':'ID','organization':'Organization','address':'Address','menu':'Menu',
                     'expiry':'Expiry','location':'Location','quantity':'Qty Left','date':'Date'}
        ), use_container_width=True)
    else:
        st.info("No food details submitted yet.")

# ----- NGO PORTAL -----
# ----- NGO PORTAL -----
elif menu == "NGO Portal":
    st.title("NGO / Acceptor Portal 🏢")
    ngo_id = st.text_input("Enter your NGO Registration Number")
    verify_btn = st.button("Verify NGO")
    if verify_btn:
        recognized_ngos = ["NGO1001", "NGO1002", "NGO1003"]
        if ngo_id in recognized_ngos:
            st.success("NGO Verified!")
            st.session_state['ngo_verified'] = True
            st.session_state['ngo_id'] = ngo_id
        else:
            st.error("Your NGO is not recognized.")
            st.session_state['ngo_verified'] = False

    if st.session_state.get('ngo_verified', False):
        df = get_all_donations()
        if not df.empty:
            st.subheader("Available Food from Donors")

            # ✅ Show as a table with Organization & Food Type headers
            display_df = df[df['quantity'] > 0][['organization', 'menu', 'quantity']].rename(
                columns={'organization': 'Organization', 'menu': 'Food Type', 'quantity': 'Qty Left'}
            )

            st.dataframe(display_df, use_container_width=True)

            # ✅ Allow pickup with selection
            for _, row in df.iterrows():
                if row['quantity'] > 0:
                    with st.expander(f"{row['organization']} - {row['menu']} ({row['quantity']} left)"):
                        pick_qty = st.number_input(
                            f"Pick quantity for ID {row['id']}",
                            min_value=1,
                            max_value=int(row['quantity']),
                            step=1,
                            key=f"pick_{row['id']}"
                        )
                        if st.button("Pick", key=f"btn_{row['id']}"):
                            success, msg, new_qty = update_quantity(row['id'], -pick_qty)
                            if success:
                                log_pickup(row['id'], st.session_state.get('ngo_id', 'unknown'), pick_qty)
                                st.markdown(
                                    f"<p style='color:black; font-weight:bold;'>🎉 Picked {pick_qty} meals. Remaining: {new_qty}</p>",
                                    unsafe_allow_html=True
                                )
                                st.session_state.donor_df = get_all_donations()

# ----- ANALYSIS -----
elif menu == "Analysis":
    # ---------- ANALYSIS PAGE ----------
    # Wrap the entire content in a div with black font and professional font-family
    st.markdown("""
        <div style="color:black; font-family: 'Helvetica', Arial, sans-serif;">
    """, unsafe_allow_html=True)

    st.title("Donation Analysis Dashboard 📊")
    df = get_all_donations()
    if not df.empty:
        total_meals_received = int(df['initial_quantity'].sum())
        total_current_available = int(df['quantity'].sum())
        total_entries = len(df)
        st.markdown(f"### ✅ Overall Summary")
        st.markdown(f"- Total Meals Donated: {total_meals_received}")
        st.markdown(f"- Total Meals Currently Available: {total_current_available}")
        st.markdown(f"- Total Donation Entries: {total_entries}")

        # Example of Plotly chart with black text
        import plotly.graph_objects as go
        org_avail = df.groupby("organization")["quantity"].sum().reset_index()
        date_summary = df.groupby("date")["initial_quantity"].sum().reset_index().sort_values("date")
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=org_avail['organization'], 
            y=org_avail['quantity'], 
            name="Meals Available", 
            marker_color="#004d40"
        ))
        fig.add_trace(go.Scatter(
            x=date_summary['date'], 
            y=date_summary['initial_quantity'], 
            name="Meals Donated Over Time", 
            mode='lines+markers', 
            line=dict(color="#ff7043", width=3)
        ))
        fig.update_layout(
            title="Meals Available by Organization & Donations Over Time",
            xaxis_title="Organization / Date",
            yaxis_title="Number of Meals",
            template="plotly_white",
            font=dict(color="black"),  # ensures Plotly text is black
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)

        # Detailed Data Table
        st.subheader("📋 Detailed Donation Records")
        st.dataframe(df[['id','organization','address','menu','expiry','location','initial_quantity','quantity','date']].rename(
            columns={'id':'ID','organization':'Organization','address':'Address','menu':'Menu',
                     'expiry':'Expiry','location':'Location','initial_quantity':'Total Donated',
                     'quantity':'Qty Left','date':'Date'}
        ), use_container_width=True)

        # CSV download
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Donation Data (CSV)", data=csv_data, file_name="donations.csv", mime="text/csv")

    else:
        st.info("No donation data available for analysis yet.")

    # Close the black font div
    st.markdown("</div>", unsafe_allow_html=True)

# ----- REWARDS -----
# ----- REWARDS -----
elif menu == "Rewards":
    st.markdown("<div style='color:black;'>", unsafe_allow_html=True)
    st.title("🏆 Rewards & Leaderboard")
    st.markdown("Recognizing Donors & NGOs for their efforts")

    # ✅ Donor Points = total meals donated
    donor_df = get_all_donations()
    if not donor_df.empty:
        donor_points = donor_df.groupby("organization")["initial_quantity"].sum().reset_index()
        donor_points.columns = ["Donor", "Points"]
        donor_points["Badge"] = donor_points["Points"].apply(get_badge)
        donor_points = donor_points.sort_values("Points", ascending=False).reset_index(drop=True)

        st.subheader("📊 Donor Leaderboard")
        st.dataframe(donor_points, use_container_width=True)
    else:
        st.info("No donors yet.")

    # ✅ NGO Points = total meals picked
    conn = sqlite3.connect(DB_PATH)
    ngo_df = pd.read_sql_query(
        "SELECT ngo_id as NGO, SUM(picked_quantity) as Points FROM pickups GROUP BY ngo_id", conn
    )
    conn.close()

    if not ngo_df.empty:
        ngo_df["Badge"] = ngo_df["Points"].apply(get_badge)
        ngo_df = ngo_df.sort_values("Points", ascending=False).reset_index(drop=True)

        st.subheader("📊 NGO Leaderboard")
        st.dataframe(ngo_df, use_container_width=True)
    else:
        st.info("No NGOs have picked meals yet.")

    st.markdown("</div>", unsafe_allow_html=True)
