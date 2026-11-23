import streamlit as st
import pandas as pd
from datetime import datetime

# ตั้งค่าหน้าเว็บให้จำลองแอปมือถือ
st.set_page_config(page_title="Dime! - Investment & Saving Simulator", layout="centered")

# ----------------- ตกแต่ง CSS ให้เหมือนแอป Dime -----------------
st.markdown("""
    <style>
    /* ธีมสีหลักและพื้นหลัง */
    .main { background-color: #F8F9FA; }
    
    /* ปรับแต่งปุ่มให้เป็นสีเขียวสไตล์ Dime */
    .stButton>button {
        background-color: #00B14F;
        color: white;
        border-radius: 20px;
        font-weight: bold;
        border: none;
        width: 100%;
        padding: 10px;
    }
    .stButton>button:hover {
        background-color: #009541;
        color: white;
    }
    
    /* กล่องข้อความและ Card */
    div.stMetric {
        background-color: #FFFFFF;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# ----------------- 1. INITIAL STATE (กำหนดค่าเริ่มต้นระบบ) -----------------
if 'thb_balance' not in st.session_state:
    st.session_state.thb_balance = 50000.00  # เงินสดบาท

if 'usd_balance' not in st.session_state:
    st.session_state.usd_balance = 200.00     # เงินสดดอลลาร์

if 'dime_save' not in st.session_state:
    st.session_state.dime_save = 15000.00   # เงินฝากดอกเบี้ยสูง Dime Save

if 'us_portfolio' not in st.session_state:
    st.session_state.us_portfolio = {}        # พอร์ตหุ้น US

if 'th_portfolio' not in st.session_state:
    st.session_state.th_portfolio = {}        # พอร์ตหุ้นไทย

if 'fund_portfolio' not in st.session_state:
    st.session_state.fund_portfolio = {}      # พอร์ตกองทุนรวม

if 'gold_grams' not in st.session_state:
    st.session_state.gold_grams = 0.0         # ทองคำสะสม (กรัม)

if 'history' not in st.session_state:
    st.session_state.history = []             # ประวัติธุรกรรม

EXCHANGE_RATE = 36.50  # อัตราแลกเปลี่ยนจำลอง 1 USD = 36.50 THB

# ฐานข้อมูลตลาด
MARKET = {
    "us": {
        "AAPL": {"name": "Apple Inc.", "price": 185.20},
        "TSLA": {"name": "Tesla Inc.", "price": 242.50},
        "NVDA": {"name": "NVIDIA Corp.", "price": 920.00}
    },
    "th": {
        "PTT.BK": {"name": "บริษัท ปตท. จำกัด (มหาชน)", "price": 34.50},
        "AOT.BK": {"name": "ท่าอากาศยานไทย", "price": 60.25},
        "CPALL.BK": {"name": "ซีพี ออลล์ จำกัด (มหาชน)", "price": 55.00}
    },
    "funds": {
        "K-CHANGE-A(A)": {"name": "กองทุนเปิด K หุ้นยุคใหม่", "nav": 15.45},
        "K-USXNDQ-A(A)": {"name": "กองทุนเปิด K หุ้น Nasdaq 100", "nav": 28.10}
    },
    "gold_price": 2450.0 # บาท/กรัม
}

# ----------------- 2. HEADER & DASHBOARD -----------------
st.title("💸 Dime! (Simulator)")
st.caption("ลงทุนหุ้นสหรัฐฯ หุ้นไทย กองทุน ทองคำ และ Dime Save ในแอปเดียว")

# คำนวณมูลค่าพอร์ตทั้งหมดเป็นบาท
us_val = sum([d['shares'] * MARKET['us'][s]['price'] * EXCHANGE_RATE for s, d in st.session_state.us_portfolio.items()])
th_val = sum([d['shares'] * MARKET['th'][s]['price'] for s, d in st.session_state.th_portfolio.items()])
fund_val = sum([d['units'] * MARKET['funds'][f]['nav'] for f, d in st.session_state.fund_portfolio.items()])
gold_val = st.session_state.gold_grams * MARKET['gold_price']

total_cash = st.session_state.thb_balance + (st.session_state.usd_balance * EXCHANGE_RATE) + st.session_state.dime_save
net_worth = total_cash + us_val + th_val + fund_val + gold_val

st.markdown("### 📊 มูลค่าทรัพย์สินรวมทั้งหมด")
st.subheader(f"฿{net_worth:,.2f}")

c1, c2, c3 = st.columns(3)
c1.metric("💵 เงินสดรวม", f"฿{total_cash:,.2f}")
c2.metric("📈 พอร์ตลงทุนรวม", f"฿{(us_val + th_val + fund_val + gold_val):,.2f}")
c3.metric("💰 Dime Save", f"฿{st.session_state.dime_save:,.2f}")

st.divider()

# ----------------- 3. NAVIGATION MENU (เมนูสไตล์แอป) -----------------
menu = st.selectbox("📌 เลือกเมนูการใช้งาน:", [
    "🏠 หน้าแรก / พอร์ตของฉัน",
    "💰 Dime Save (ออมทรัพย์ดอกเบี้ยสูง)",
    "🇺🇸 หุ้นสหรัฐฯ (US Stocks & Fractional)",
    "🇹🇭 หุ้นไทย (Thai Stocks)",
    "📊 กองทุนรวม (Mutual Funds)",
    "🥇 ทองคำ (Gold Investment)",
    "💱 กระเป๋าเงิน & แลกเงิน (Wallet & FX)",
    "📜 ประวัติการทำรายการ"
])

# -----------------------------------------------------------------
# TAB 1: PORTFOLIO
# -----------------------------------------------------------------
if "หน้าแรก" in menu:
    st.subheader("📂 พอร์ตการลงทุนของคุณ")
    
    st.markdown("#### 🇺🇸 หุ้นสหรัฐฯ (US Stocks)")
    if st.session_state.us_portfolio:
        us_data = []
        for s, d in st.session_state.us_portfolio.items():
            cur_p = MARKET['us'][s]['price']
            us_data.append({"Symbol": s, "Shares": f"{d['shares']:,.6f}", "Value ($)": f"${d['shares']*cur_p:,.2f}"})
        st.dataframe(pd.DataFrame(us_data), use_container_width=True)
    else:
        st.info("ยังไม่มีหุ้นสหรัฐฯ ในพอร์ต")

    st.markdown("#### 🇹🇭 หุ้นไทย (Thai Stocks)")
    if st.session_state.th_portfolio:
        th_data = []
        for s, d in st.session_state.th_portfolio.items():
            cur_p = MARKET['th'][s]['price']
            th_data.append({"Symbol": s, "Shares": d['shares'], "Value (THB)": f"฿{d['shares']*cur_p:,.2f}"})
        st.dataframe(pd.DataFrame(th_data), use_container_width=True)
    else:
        st.info("ยังไม่มีหุ้นไทยในพอร์ต")

    st.markdown("#### 📊 กองทุนรวม & 🥇 ทองคำ")
    st.write(f"กองทุนรวมทั้งหมด: {len(st.session_state.fund_portfolio)} กองทุน | ทองคำสะสม: {st.session_state.gold_grams:,.2f} กรัม")

# -----------------------------------------------------------------
# TAB 2: DIME SAVE
# -----------------------------------------------------------------
elif "Dime Save" in menu:
    st.subheader("💰 บัญชี Dime Save (ดอกเบี้ยสะสมรายวัน)")
    st.write(f"ยอดเงินใน Dime Save: **฿{st.session_state.dime_save:,.2f}**")
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        dep = st.number_input("ฝากเงินเข้า Dime Save (THB):", min_value=1.0, value=1000.0, step=500.0)
        if st.button("ฝากเงิน"):
            if dep > st.session_state.thb_balance:
                st.error("❌ ข้อผิดพลาด: เงินบาทในกระเป๋าหลักไม่เพียงพอ")
            else:
                st.session_state.thb_balance -= dep
                st.session_state.dime_save += dep
                st.session_state.history.append({"Time": datetime.now().strftime("%H:%M:%S"), "Action": "Deposit Dime Save", "Amount": f"฿{dep:,.2f}"})
                st.success(f"✅ ฝากเงินสำเร็จ +฿{dep:,.2f}")
                st.rerun()

    with col_d2:
        wit = st.number_input("ถอนเงินออกจาก Dime Save (THB):", min_value=1.0, value=1000.0, step=500.0)
        if st.button("ถอนเงิน"):
            if wit > st.session_state.dime_save:
                st.error("❌ ข้อผิดพลาด: ยอดเงินใน Dime Save ไม่เพียงพอ")
            else:
                st.session_state.dime_save -= wit
                st.session_state.thb_balance += wit
                st.session_state.history.append({"Time": datetime.now().strftime("%H:%M:%S"), "Action": "Withdraw Dime Save", "Amount": f"฿{wit:,.2f}"})
                st.success(f"✅ ถอนเงินสำเร็จ ฿{wit:,.2f}")
                st.rerun()

# -----------------------------------------------------------------
# TAB 3: US STOCKS
# -----------------------------------------------------------------
elif "หุ้นสหรัฐฯ" in menu:
    st.subheader("🇺🇸 หุ้นสหรัฐฯ (รองรับระบบเศษหุ้น / Fractional Shares)")
    st.dataframe(pd.DataFrame([{"Symbol": s, "Name": i["name"], "Price ($)": i["price"]} for s, i in MARKET["us"].items()]), use_container_width=True)
    
    sel_us = st.selectbox("เลือกหุ้น US:", list(MARKET["us"].keys()))
    price = MARKET["us"][sel_us]["price"]
    st.write(f"ราคาปัจจุบัน: **${price:,.2f} USD**")
    
    mode = st.radio("ซื้อด้วย:", ["จำนวนเงิน ($)", "จำนวนหุ้น (เศษหุ้น)"], horizontal=True)
    
    usd_spend, shares = 0.0, 0.0
    if "จำนวนเงิน" in mode:
        usd_spend = st.number_input("ระบุจำนวนเงินลงทุน ($):", min_value=1.0, value=50.0, step=10.0)
        shares = usd_spend / price
        st.info(f"💡 จะได้รับเศษหุ้น: **{shares:,.6f} {sel_us}**")
    else:
        shares = st.number_input("ระบุจำนวนหุ้น:", min_value=0.00001, value=0.1, step=0.01)
        usd_spend = shares * price
        st.info(f"💡 ยอดชำระ: **${usd_spend:,.2f} USD**")

    if st.button("ยืนยันซื้อหุ้นสหรัฐฯ"):
        if usd_spend <= 0 or shares <= 0:
            st.error("❌ ข้อผิดพลาด: ค่าการลงทุนต้องมากกว่า 0")
        elif usd_spend > st.session_state.usd_balance:
            st.error(f"❌ ข้อผิดพลาด: เงิน USD ไม่พอ! (มี ${st.session_state.usd_balance:,.2f}, ต้องการ ${usd_spend:,.2f})")
        else:
            st.session_state.usd_balance -= usd_spend
            if sel_us in st.session_state.us_portfolio:
                st.session_state.us_portfolio[sel_us]["shares"] += shares
            else:
                st.session_state.us_portfolio[sel_us] = {"shares": shares}
            
            st.session_state.history.append({"Time": datetime.now().strftime("%H:%M:%S"), "Action": f"Buy US ({sel_us})", "Amount": f"${usd_spend:,.2f}"})
            st.success(f"✅ ซื้อสำเร็จ! ได้รับ {shares:,.6f} หุ้นของ {sel_us}")
            st.rerun()

# -----------------------------------------------------------------
# TAB 4: THAI STOCKS
# -----------------------------------------------------------------
elif "หุ้นไทย" in menu:
    st.subheader("🇹🇭 หุ้นไทย (บังคับตามกฎ Board Lot ทีละ 100 หุ้น)")
    st.dataframe(pd.DataFrame([{"Symbol": s, "Name": i["name"], "Price (THB)": i["price"]} for s, i in MARKET["th"].items()]), use_container_width=True)
    
    sel_th = st.selectbox("เลือกหุ้นไทย:", list(MARKET["th"].keys()))
    price_th = MARKET["th"][sel_th]["price"]
    st.write(f"ราคาปัจจุบัน: **฿{price_th:,.2f} ต่อหุ้น**")
    
    th_shares = st.number_input("จำนวนหุ้น (ต้องลงท้ายด้วย 100):", min_value=100, step=100, value=100)
    total_cost = th_shares * price_th
    st.write(f"ยอดชำระรวม: **฿{total_cost:,.2f} THB**")

    if st.button("ยืนยันซื้อหุ้นไทย"):
        if th_shares % 100 != 0:
            st.error("❌ ข้อผิดพลาด: หุ้นไทยต้องซื้อเป็นจำนวนเต็มร้อย (Board Lot เช่น 100, 200...)")
        elif total_cost > st.session_state.thb_balance:
            st.error(f"❌ ข้อผิดพลาด: เงินบาทไม่พอ! (มี ฿{st.session_state.thb_balance:,.2f}, ต้องการ ฿{total_cost:,.2f})")
        else:
            st.session_state.thb_balance -= total_cost
            if sel_th in st.session_state.th_portfolio:
                st.session_state.th_portfolio[sel_th]["shares"] += th_shares
            else:
                st.session_state.th_portfolio[sel_th] = {"shares": th_shares}
            
            st.session_state.history.append({"Time": datetime.now().strftime("%H:%M:%S"), "Action": f"Buy TH ({sel_th})", "Amount": f"฿{total_cost:,.2f}"})
            st.success(f"✅ ซื้อหุ้นไทย {sel_th} จำนวน {th_shares} หุ้น สำเร็จ!")
            st.rerun()

# -----------------------------------------------------------------
# TAB 5: MUTUAL FUNDS
# -----------------------------------------------------------------
elif "กองทุนรวม" in menu:
    st.subheader("📊 กองทุนรวม (Mutual Funds)")
    st.dataframe(pd.DataFrame([{"Code": f, "Name": i["name"], "NAV (THB)": i["nav"]} for f, i in MARKET["funds"].items()]), use_container_width=True)
    
    sel_f = st.selectbox("เลือกกองทุน:", list(MARKET["funds"].keys()))
    nav = MARKET["funds"][sel_f]["nav"]
    
    f_invest = st.number_input("เงินลงทุนกองทุน (THB):", min_value=100.0, value=1000.0, step=500.0)
    units = f_invest / nav
    st.info(f"💡 หน่วยลงทุนที่จะได้รับ: **{units:,.4f} หน่วย**")

    if st.button("ยืนยันซื้อกองทุน"):
        if f_invest > st.session_state.thb_balance:
            st.error("❌ ข้อผิดพลาด: เงินบาทไม่พอซื้อกองทุน")
        else:
            st.session_state.thb_balance -= f_invest
            if sel_f in st.session_state.fund_portfolio:
                st.session_state.fund_portfolio[sel_f]["units"] += units
            else:
                st.session_state.fund_portfolio[sel_f] = {"units": units}
            
            st.session_state.history.append({"Time": datetime.now().strftime("%H:%M:%S"), "Action": f"Buy Fund ({sel_f})", "Amount": f"฿{f_invest:,.2f}"})
            st.success(f"✅ ซื้อกองทุนสำเร็จ {units:,.4f} หน่วย")
            st.rerun()

# -----------------------------------------------------------------
# TAB 6: GOLD
# -----------------------------------------------------------------
elif "ทองคำ" in menu:
    st.subheader("🥇 ทองคำออนไลน์ (Gold Investment)")
    g_price = MARKET["gold_price"]
    st.write(f"ราคาทองคำปัจจุบัน: **฿{g_price:,.2f} ต่อกรัม**")
    
    grams = st.number_input("ต้องการซื้อทองคำ (กรัม):", min_value=0.1, value=1.0, step=0.1)
    g_cost = grams * g_price
    st.write(f"ยอดชำระ: **฿{g_cost:,.2f} THB**")

    if st.button("ยืนยันซื้อทองคำ"):
        if g_cost > st.session_state.thb_balance:
            st.error("❌ ข้อผิดพลาด: เงินบาทไม่พอซื้อทองคำ")
        else:
            st.session_state.thb_balance -= g_cost
            st.session_state.gold_grams += grams
            st.session_state.history.append({"Time": datetime.now().strftime("%H:%M:%S"), "Action": "Buy Gold", "Amount": f"฿{g_cost:,.2f}"})
            st.success(f"✅ ซื้อทองคำสำเร็จ {grams} กรัม")
            st.rerun()

# -----------------------------------------------------------------
# TAB 7: WALLET & FX
# -----------------------------------------------------------------
elif "กระเป๋าเงิน & แลกเงิน" in menu:
    st.subheader("💱 กระเป๋าเงิน & แลกเปลี่ยนสกุลเงิน (FCD Simulation)")
    
    col_w1, col_w2 = st.columns(2)
    with col_w1:
        st.markdown("### 📥 เติมเงินบาท (THB)")
        add_thb = st.number_input("จำนวนเงินบาท:", min_value=100.0, value=10000.0, step=1000.0)
        if st.button("เติมเงิน THB"):
            st.session_state.thb_balance += add_thb
            st.success(f"✅ เติมเงินสำเร็จ +฿{add_thb:,.2f}")
            st.rerun()

    with col_w2:
        st.markdown("### 💱 แลกเงิน THB เป็น USD")
        st.write(f"เรทแลกเปลี่ยน: 1 USD = {EXCHANGE_RATE} THB")
        thb_ex = st.number_input("ใช้เงินบาทแลก:", min_value=365.0, value=3650.0, step=365.0)
        usd_got = thb_ex / EXCHANGE_RATE
        if st.button("ยืนยันแลกเงิน"):
            if thb_ex > st.session_state.thb_balance:
                st.error("❌ ข้อผิดพลาด: เงินบาทไม่พอแลก")
            else:
                st.session_state.thb_balance -= thb_ex
                st.session_state.usd_balance += usd_got
                st.success(f"✅ แลกสำเร็จ! ได้รับ ${usd_got:,.2f} USD")
                st.rerun()

# -----------------------------------------------------------------
# TAB 8: HISTORY
# -----------------------------------------------------------------
elif "ประวัติการทำรายการ" in menu:
    st.subheader("📜 ประวัติการทำรายการทั้งหมด")
    if st.session_state.history:
        st.dataframe(pd.DataFrame(st.session_state.history), use_container_width=True)
    else:
        st.info("ยังไม่มีประวัติธุรกรรม")
