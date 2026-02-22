import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# --- GÜVENLİK ---
DOGRU_PIN = "1234"
if 'giris_yapildi' not in st.session_state: st.session_state.giris_yapildi = False
if not st.session_state.giris_yapildi:
    st.set_page_config(page_title="SmartSave Lock", page_icon="🔐")
    col_p1, col_p2, col_p3 = st.columns([1,2,1])
    with col_p2:
        st.markdown("<h2 style='text-align: center;'>🔐 GÜVENLİ GİRİŞ</h2>", unsafe_allow_html=True)
        pin = st.text_input("", type="password", placeholder="****")
        if st.button("Sistemi Aç", use_container_width=True):
            if pin == DOGRU_PIN:
                st.session_state.giris_yapildi = True
                st.rerun()
    st.stop()

st.set_page_config(page_title="SmartSave v7.9", page_icon="💎", layout="wide")

DATA_FILE = "finans_verileri.csv"
CONFIG_FILE = "ayarlar.txt"

# --- 🧠 AKILLI İKON ASİSTANI ---
def ikon_bulucu(isim):
    sozluk = {
        "yemek": "🍔", "döner": "🌯", "kahve": "☕", "market": "🛒", "ekmek": "🍞",
        "kira": "🏠", "fatura": "🔌", "su": "💧", "elektrik": "⚡", "internet": "🌐",
        "ulaşım": "🚌", "benzin": "⛽", "kart": "💳", "oyun": "🎮", "maaş": "💰",
        "yatırım": "🚀", "giyim": "👕", "ayakkabı": "👟", "spor": "🏃", "hediye": "🎁"
    }
    isim_lower = isim.lower()
    for anahtar, ikon in sozluk.items():
        if anahtar in isim_lower:
            return f"{ikon} {isim}"
    return f"✨ {isim}"

# --- AYARLARI YÜKLE ---
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r") as f:
        try: kayitli_fiyat = int(float(f.read().strip()))
        except: kayitli_fiyat = 75000
else: kayitli_fiyat = 75000

# --- VERİ YÜKLEME ---
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
    if "Tip" not in df.columns: df["Tip"] = "Zorunlu ✅"
    df["Tarih"] = pd.to_datetime(df["Tarih"], errors='coerce').fillna(datetime.now())
else:
    df = pd.DataFrame(columns=["Tarih", "Tür", "İsim", "Kategori", "Miktar", "Tip"])

# --- SIDEBAR ---
with st.sidebar:
    st.title("💎 SmartSave PRO")
    yeni_fiyat = st.number_input("iPhone Hedef Fiyatı", value=int(kayitli_fiyat), step=1000)
    if yeni_fiyat != kayitli_fiyat:
        with open(CONFIG_FILE, "w") as f: f.write(str(int(yeni_fiyat)))
        st.rerun()
    
    st.divider()
    with st.form("hizli_kayit_v79", clear_on_submit=True):
        st.subheader("Hızlı İşlem")
        tur = st.selectbox("Tür", ["Gider 🔻", "Gelir 🔺"])
        isim_input = st.text_input("Açıklama (Örn: Kahve)")
        kat = st.selectbox("Kategori", ["🍔 Yemek", "🛒 Market", "🚌 Ulaşım", "🎮 Eğlence", "🏠 Kira/Fatura", "👕 Giyim", "💵 Maaş", "🚀 Yatırım"])
        tip_secimi = st.selectbox("Harcama Tipi", ["Zorunlu ✅", "Keyfi ✨"]) if "Gider" in tur else "Gelir"
        tutar = st.number_input("Tutar", min_value=1, step=1)
        
        if st.form_submit_button("Kaydet ✨"):
            isim_ikonlu = ikon_bulucu(isim_input)
            tarih_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            yeni = pd.DataFrame([{"Tarih": tarih_str, "Tür": "Gider" if "Gider" in tur else "Gelir", "İsim": isim_ikonlu, "Kategori": kat, "Miktar": int(tutar), "Tip": tip_secimi}])
            df = pd.concat([df, yeni], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.rerun()

# --- DASHBOARD ANALİZ ---
toplam_gelir = df[df["Tür"] == "Gelir"]["Miktar"].sum()
toplam_gider = df[df["Tür"] == "Gider"]["Miktar"].sum()
net_bakiye = toplam_gelir - toplam_gider

st.markdown(f"### 🎯 iPhone Yolculuğu: %{min((net_bakiye/yeni_fiyat)*100, 100):.1f}")
st.progress(min(net_bakiye/yeni_fiyat, 1.0))

c1, c2, c3 = st.columns(3)
c1.metric("Net Kasa", f"₺{int(net_bakiye):,}")
c2.metric("Toplam Gelir", f"₺{int(toplam_gelir):,}")
c3.metric("Toplam Gider", f"₺{int(toplam_gider):,}")

# --- 📊 PREMIUM GRAFİKLER ---
st.divider()
col_l, col_r = st.columns(2)

with col_l:
    st.write("### 🍩 Gider Dağılımı")
    if not df[df["Tür"]=="Gider"].empty:
        # Şık bir Donut Chart
        fig_donut = px.pie(df[df["Tür"]=="Gider"], names="Kategori", values="Miktar", 
                           hole=0.6, color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_donut.update_traces(textinfo='percent+label', marker=dict(line=dict(color='#000000', width=1)))
        st.plotly_chart(fig_donut, use_container_width=True)



with col_r:
    st.write("### 📈 Birikim Gelişimi")
    df_sorted = df.sort_values("Tarih")
    df_sorted["Bakiye"] = df_sorted.apply(lambda x: x["Miktar"] if x["Tür"]=="Gelir" else -x["Miktar"], axis=1).cumsum()
    # Alan Grafiği
    fig_area = px.area(df_sorted, x="Tarih", y="Bakiye", color_discrete_sequence=['#00CC96'])
    fig_area.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_area, use_container_width=True)

# --- ŞIK TABLO ---
st.divider()
st.subheader("📜 Son İşlemler")
st.dataframe(df.iloc[::-1], use_container_width=True, hide_index=True)
