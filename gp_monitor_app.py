import streamlit as st
import pandas as pd
import datetime
import plotly.express as px

# পেজ কনফিগারেশন
st.set_page_config(page_title="GP Finance Monitor", page_icon="⚖️", layout="wide")

# ডেমো সিকিউর PIN 
SECURE_PIN = "7001" 

# সেশন স্টেট ইনিশিয়ালাইজেশন (ডেটাবেস সিমুলেশন)
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "collections" not in st.session_state:
    st.session_state.collections = pd.DataFrame(columns=["তারিখ", "রসিদ নং", "উৎস/নাগরিক", "ক্যাটাগরি", "পরিমাণ (₹)", "সংগ্রাহক"])
if "expenditures" not in st.session_state:
    st.session_state.expenditures = pd.DataFrame(columns=["তারিখ", "ভাউচার নং", "খাত/বিবরণ", "ক্যাটাগরি", "পরিমাণ (₹)", "অনুমোদনকারী"])

# --- ১. সিকিউর লগইন গেটওয়ে ---
if not st.session_state.authenticated:
    st.markdown("<h2 style='text-align: center;'>গ্রাম পঞ্চায়েত আর্থিক মনিটরিং পোর্টাল</h2>", unsafe_style=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info("🔒 ফিন্যান্সিয়াল ডেটা অ্যাক্সেস করতে অথরাইজড সিকিউরিটি PIN দিন।")
        input_pin = st.text_input("গোপন PIN লিখুন:", type="password", max_chars=4)
        if st.button("ড্যাশবোর্ড আনলক করুন 🔓", use_container_width=True):
            if input_pin == SECURE_PIN:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ ভুল PIN! সঠিক কোডটি পুনরায় চেষ্টা করুন।")

# --- ২. মূল অ্যাপ্লিকেশন ড্যাশবোর্ড (লগইন সফল হলে) ---
else:
    # টপ হেডার ও লগআউট
    c_title, c_logout = st.columns([4, 1])
    with c_title:
        st.title("⚖️ গ্রাম পঞ্চায়েত ফি কালেকশন ও ব্যয় মনিটর")
    with c_logout:
        if st.button("লg আউট 🔒", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()

    st.divider()

    # ফিন্যান্সিয়াল মেট্রিক্স হিসাব
    total_in = st.session_state.collections["পরিমাণ (₹)"].sum()
    total_out = st.session_state.expenditures["পরিমাণ (₹)"].sum()
    net_balance = total_in - total_out

    # রিয়েল-টাইম ব্যালেন্স কার্ড
    m1, m2, m3 = st.columns(3)
    m1.metric("মোট সংগ্রহ (Total Income)", f"₹ {total_in}/-", delta_color="normal")
    m2.metric("মোট খরচ (Total Expense)", f"₹ {total_out}/-", delta="-")
    m3.metric("নেট ফান্ড ব্যালেন্স (Net Cash)", f"₹ {net_balance}/-", delta=f"{net_balance}", delta_color="off" if net_balance >= 0 else "inverse")

    st.divider()

    # ট্যাব সিস্টেম: ১. এন্ট্রি ফরম, ২. কালেকশন লেজার, ৩. খরচ লেজার, ৪. গ্রাফিক্যাল অ্যানালিটিক্স
    tab_entry, tab_coll, tab_exp, tab_chart = st.tabs(["📝 নতুন এন্ট্রি (Income/Expense)", "📥 আয় খাতা", "📤 ব্যয় খাতা", "📊 আর্থিক গ্রাফ"])

    with tab_entry:
        col_in, col_out = st.columns(2)
        
        # আয়ের ফর্ম
        with col_in:
            st.subheader("📥 ফি/রাজস্ব সংগ্রহের এন্ট্রি")
            with st.form("income_form", clear_on_submit=True):
                citizen = st.text_input("নাগরিক / প্রতিষ্ঠানের নাম:")
                inc_cat = st.selectbox("আয়ের খাত:", ["Assessment Tax", "Trade License", "Certificate Fee", "Building Plan", "Other"])
                amount_in = st.number_input("টাকার পরিমাণ (₹):", min_value=0, step=50)
                staff = st.text_input("সংগ্রাহক কর্মীর নাম:")
                if st.form_submit_button("আয় নথিবদ্ধ করুন"):
                    if citizen and amount_in > 0:
                        r_no = f"REC-{datetime.datetime.now().strftime('%M%S')}"
                        new_inc = {"তারিখ": datetime.date.today(), "রসিদ নং": r_no, "উৎস/নাগরিক": citizen, "ক্যাটাগরি": inc_cat, "পরিমাণ (₹)": amount_in, "সংগ্রাহক": staff}
                        st.session_state.collections = pd.concat([st.session_state.collections, pd.DataFrame([new_inc])], ignore_index=True)
                        st.success("✅ আয় সফলভাবে যোগ করা হয়েছে।")
                        st.rerun()

        # খরচের ফর্ম
        with col_out:
            st.subheader("📤 পঞ্চায়েত ব্যয়ের এント্রি")
            with st.form("expense_form", clear_on_submit=True):
                purpose = st.text_input("খরচের বিবরণ / ভেন্ডর:")
                exp_cat = st.selectbox("ব্যয়ের খাত:", ["অফিস রক্ষণাবেক্ষণ", "রাস্তা/নর্দমা সংস্কার", "স্ট্রিট লাইট মেরামত", "কর্মীদের বেতন/ভাতা", "অন্যান্য উন্নয়নমূলক কাজ"])
                amount_out = st.number_input("টাকার পরিমাণ (₹):", min_value=0, step=50)
                approver = st.text_input("অনুমোদনকারী কর্মকর্তা (যেমন: প্রধান/ইএ):")
                if st.form_submit_button("ব্যয় নথিবদ্ধ করুন", type="primary"):
                    if purpose and amount_out > 0:
                        v_no = f"VOU-{datetime.datetime.now().strftime('%M%S')}"
                        new_exp = {"তারিখ": datetime.date.today(), "ভাউচার নং": v_no, "খাত/বিবরণ": purpose, "ক্যাটাগরি": exp_cat, "পরিমাণ (₹)": amount_out, "অনুমোদনকারী": approver}
                        st.session_state.expenditures = pd.concat([st.session_state.expenditures, pd.DataFrame([new_exp])], ignore_index=True)
                        st.success("⚠️ খরচ সফলভাবে নথিবদ্ধ করা হয়েছে।")
                        st.rerun()

    with tab_coll:
        st.subheader("📥 আদায়কৃত ফি-র খতিয়ান")
        st.dataframe(st.session_state.collections, use_container_width=True)

    with tab_exp:
        st.subheader("📤 খরচের খতিয়ান")
        st.dataframe(st.session_state.expenditures, use_container_width=True)

    with tab_chart:
        st.subheader("📊 বাজেট ও আর্থিক স্থিতি বিশ্লেষণ")
        c1, c2 = st.columns(2)
        with c1:
            if not st.session_state.collections.empty:
                fig1 = px.pie(st.session_state.collections, values="পরিমাণ (₹)", names="ক্যাটাগরি", title="আয়ের উৎস বিভাজন")
                st.plotly_chart(fig1, use_container_width=True)
        with c2:
            if not st.session_state.expenditures.empty:
                fig2 = px.bar(st.session_state.expenditures, x="ক্যাটাগরি", y="পরিমাণ (₹)", color="ক্যাটাগরি", title="খাত ভিত্তিক ব্যয়ের পরিমাণ")
                st.plotly_chart(fig2, use_container_width=True)
