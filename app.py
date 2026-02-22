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

st.set_page_config(page_title="SmartSave v7.2", page_icon="📈", layout="wide")

# --- VERİ YÜKLEME ---
DATA_FILE = "finans_verileri.csv"
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
    df["Tarih"] = pd.to_datetime(df["Tarih"], errors='coerce').fillna(datetime.now())
else:
    df = pd.DataFrame(columns=["Tarih", "Tür", "İsim", "Kategori", "Miktar", "Tip"])

# --- SIDEBAR: YENİ NESİL YÖNETİM ---
with st.sidebar:
    st.title("📈 Strateji Merkezi")
    hedef_tutar = st.number_input("iPhone Hedef Fiyatı (TL)", value=75000, step=500)
    
    st.divider()
    with st.form("hizli_kayit_v72", clear_on_submit=True):
        st.subheader("İşlem Ekle")
        tur = st.selectbox("Tür", ["Gider 🔻", "Gelir 🔺"])
        isim = st.text_input("Açıklama")
        kat = st.selectbox("Kategori", ["🍔 Yemek", "🛒 Market", "🚌 Ulaşım", "🎮 Eğlence", "🏠 Kira/Fatura", "👕 Giyim", "💵 Maaş", "🚀 Yatırım"])
        # YENİ: Harcama Tipi
        tip = st.selectbox("Harcama Tipi", ["Zorunlu ✅", "Keyfi ✨"]) if "Gider" in tur else "Gelir"
        tutar = st.number_input("Tutar", min_value=1)
        
        if st.form_submit_button("Sisteme İşle"):
            tarih_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            yeni = pd.DataFrame([{"Tarih": tarih_str, "Tür": "Gider" if "Gider" in tur else "Gelir", "İsim": isim, "Kategori": kat, "Miktar": tutar, "Tip": tip}])
            df = pd.concat([df, yeni], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.rerun()

# --- ANALİTİK HESAPLAR ---
toplam_gelir = df[df["Tür"] == "Gelir"]["Miktar"].sum()
toplam_gider = df[df["Tür"] == "Gider"]["Miktar"].sum()
net_bakiye = toplam_gelir - toplam_gider

# Keyfi Harcama Analizi
keyfi_toplam = df[df["Tip"] == "Keyfi ✨"]["Miktar"].sum()
zorunlu_toplam = df[df["Tip"] == "Zorunlu ✅"]["Miktar"].sum()

# --- GÖRSEL DASHBOARD ---
st.markdown(f"### 🎯 Hedef Durumu: %{min((net_bakiye/hedef_tutar)*100, 100):.1f}")
st.progress(min(net_bakiye/hedef_tutar, 1.0))

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Net Bakiye", f"₺{net_bakiye:,}")
with c2:
    st.metric("Keyfi Harcamalar", f"₺{keyfi_toplam:,}", delta="-iPhone'dan çalıyor", delta_color="inverse")
with c3:
    st.metric("Zorunlu Giderler", f"₺{zorunlu_toplam:,}")



st.divider()

col_left, col_right = st.columns(2)
with col_left:
    st.subheader("💡 Tasarruf Potansiyeli")
    # Keyfi vs Zorunlu Dağılımı
    if not df[df["Tür"]=="Gider"].empty:
        fig_tip = px.pie(df[df["Tür"]=="Gider"], names="Tip", values="Miktar", 
                         color_discrete_map={"Keyfi ✨": "#FF4B4B", "Zorunlu ✅": "#00CC96"},
                         hole=0.6, title="Harcama Karakterin")
        st.plotly_chart(fig_tip, use_container_width=True)

with col_right:
    st.subheader("📉 iPhone Yol Haritası")
    if net_bakiye > 0:
        aylik_birikim = net_bakiye # Basit model
        st.write(f"Şu anki net kasanla iPhone'un **%{ (net_bakiye/hedef_tutar)*100:.1f}** tamamlandı.")
        if keyfi_toplam > 0:
            st.info(f"✨ Eğer keyfi harcamalarını durdurursan iPhone'u **{ (hedef_tutar - net_bakiye) / (net_bakiye + keyfi_toplam / (len(df)+1)):.1f}** ay daha erken alabilirsin.")
    else:
        st.error("❌ Kasan şu an ekside! iPhone için acilen 'Zorunlu' olmayan harcamaları durdurmalısın.")

# --- İŞLEM LİSTESİ ---
st.divider()
st.subheader("📜 Tüm Hareketler")
st.dataframe(df.iloc[::-1], use_container_width=True)
