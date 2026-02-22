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
        st.markdown("<h2 style='text-align: center;'>🔐 KASA KİLİDİ</h2>", unsafe_allow_html=True)
        pin = st.text_input("", type="password", placeholder="****")
        if st.button("Sistemi Aç", use_container_width=True):
            if pin == DOGRU_PIN:
                st.session_state.giris_yapildi = True
                st.rerun()
    st.stop()

st.set_page_config(page_title="SmartSave v7.1", page_icon="📱", layout="wide")

DATA_FILE = "finans_verileri.csv"

# --- AKILLI VERİ YÜKLEME ---
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
    # HATA GİDERİCİ: Tarihleri hatasız oku
    df["Tarih"] = pd.to_datetime(df["Tarih"], errors='coerce')
    # Eğer boş tarih kalırsa bugünü ata
    df["Tarih"] = df["Tarih"].fillna(datetime.now())
else:
    df = pd.DataFrame(columns=["Tarih", "Tür", "İsim", "Kategori", "Miktar"])

# --- SIDEBAR ---
with st.sidebar:
    st.title("📱 iPhone Hedefi")
    hedef_tutar = st.number_input("iPhone Fiyatı (TL)", min_value=1000, value=75000)
    st.divider()
    with st.form("hizli_islem", clear_on_submit=True):
        tur = st.selectbox("Tür", ["Gider 🔻", "Gelir 🔺"])
        isim = st.text_input("Açıklama")
        kat = st.selectbox("Kategori", ["🍔 Yemek", "🛒 Market", "🚌 Ulaşım", "🎮 Eğlence", "🏠 Kira", "👕 Giyim", "💵 Maaş", "🚀 Yatırım"])
        tutar = st.number_input("Tutar", min_value=1)
        if st.form_submit_button("Ekle"):
            # Yeni kayıtları standart ISO formatında ekle
            tarih_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            yeni = pd.DataFrame([{"Tarih": tarih_str, "Tür": "Gider" if "Gider" in tur else "Gelir", "İsim": isim, "Kategori": kat, "Miktar": tutar}])
            df = pd.concat([df, yeni], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.rerun()

# --- ANALİZ VE TAHMİN ---
toplam_gelir = df[df["Tür"] == "Gelir"]["Miktar"].sum()
toplam_gider = df[df["Tür"] == "Gider"]["Miktar"].sum()
net_birikim = toplam_gelir - toplam_gider
yuzde = min((net_birikim / hedef_tutar) * 100, 100) if hedef_tutar > 0 else 0

st.subheader(f"🎯 iPhone Hedef İlerlemesi: %{yuzde:.1f}")
st.progress(yuzde / 100)

c1, c2 = st.columns(2)
with c1:
    st.info("📊 Harcama Dağılımın")
    if not df[df["Tür"]=="Gider"].empty:
        fig_pie = px.pie(df[df["Tür"]=="Gider"], names="Kategori", values="Miktar", hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)
with c2:
    st.info("📉 Birikim Zaman Çizelgesi")
    df_sorted = df.sort_values("Tarih")
    df_sorted["Bakiye"] = df_sorted.apply(lambda x: x["Miktar"] if x["Tür"]=="Gelir" else -x["Miktar"], axis=1).cumsum()
    fig_line = px.line(df_sorted, x="Tarih", y="Bakiye")
    st.plotly_chart(fig_line, use_container_width=True)

st.divider()
st.subheader("📜 Tüm Hareketler")
# Tarihleri kullanıcıya güzel göster
df_display = df.copy()
df_display["Tarih"] = df_display["Tarih"].dt.strftime('%d/%m/%Y %H:%M')
st.dataframe(df_display.iloc[::-1], use_container_width=True, hide_index=True)
