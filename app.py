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

st.set_page_config(page_title="SmartSave v7.3", page_icon="📈", layout="wide")

DATA_FILE = "finans_verileri.csv"

# --- AKILLI VERİ YÜKLEME VE ONARMA ---
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
    # HATA DÜZELTME: Eğer 'Tip' sütunu yoksa oluştur ve 'Bilinmiyor' ata
    if "Tip" not in df.columns:
        df["Tip"] = "Zorunlu ✅"
    # Tarih onarma
    df["Tarih"] = pd.to_datetime(df["Tarih"], errors='coerce').fillna(datetime.now())
else:
    df = pd.DataFrame(columns=["Tarih", "Tür", "İsim", "Kategori", "Miktar", "Tip"])

# --- SIDEBAR ---
with st.sidebar:
    st.title("📈 Strateji Merkezi")
    hedef_tutar = st.number_input("iPhone Hedef Fiyatı", value=75000, step=500)
    
    st.divider()
    with st.form("hizli_kayit_v73", clear_on_submit=True):
        st.subheader("İşlem Ekle")
        tur = st.selectbox("Tür", ["Gider 🔻", "Gelir 🔺"])
        isim = st.text_input("Açıklama")
        kat = st.selectbox("Kategori", ["🍔 Yemek", "🛒 Market", "🚌 Ulaşım", "🎮 Eğlence", "🏠 Kira/Fatura", "👕 Giyim", "💵 Maaş", "🚀 Yatırım"])
        # Seçim türüne göre tip belirleme
        tip_secimi = st.selectbox("Harcama Tipi", ["Zorunlu ✅", "Keyfi ✨"]) if "Gider" in tur else "Gelir"
        tutar = st.number_input("Tutar", min_value=1)
        
        if st.form_submit_button("Kaydet"):
            tarih_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            yeni = pd.DataFrame([{"Tarih": tarih_str, "Tür": "Gider" if "Gider" in tur else "Gelir", "İsim": isim, "Kategori": kat, "Miktar": tutar, "Tip": tip_secimi}])
            df = pd.concat([df, yeni], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.rerun()

# --- ANALİTİK HESAPLAR ---
toplam_gelir = df[df["Tür"] == "Gelir"]["Miktar"].sum()
toplam_gider = df[df["Tür"] == "Gider"]["Miktar"].sum()
net_bakiye = toplam_gelir - toplam_gider

# --- GÖRSEL DASHBOARD ---
st.markdown(f"### 🎯 Hedef Durumu: %{min((net_bakiye/hedef_tutar)*100, 100):.1f}")
st.progress(min(net_bakiye/hedef_tutar, 1.0))

c1, c2, c3 = st.columns(3)
c1.metric("Net Bakiye", f"₺{net_bakiye:,}")
c2.metric("Gelir", f"₺{toplam_gelir:,}")
c3.metric("Gider", f"₺{toplam_gider:,}")

# GRAFİKLER
col_left, col_right = st.columns(2)
with col_left:
    if not df[df["Tür"]=="Gider"].empty:
        fig = px.pie(df[df["Tür"]=="Gider"], names="Tip", values="Miktar", hole=0.6, title="Harcama Karakteri")
        st.plotly_chart(fig, use_container_width=True)
with col_right:
    # Kumulatif birikim
    df_sorted = df.sort_values("Tarih")
    df_sorted["Bakiye"] = df_sorted.apply(lambda x: x["Miktar"] if x["Tür"]=="Gelir" else -x["Miktar"], axis=1).cumsum()
    fig_line = px.area(df_sorted, x="Tarih", y="Bakiye", title="Birikim Seyri")
    st.plotly_chart(fig_line, use_container_width=True)

st.divider()
st.subheader("📜 Tüm Hareketler")
st.dataframe(df.iloc[::-1], use_container_width=True, hide_index=True)
