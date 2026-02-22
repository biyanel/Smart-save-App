import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# --- 1. AYARLAR VE GÜVENLİK ---
st.set_page_config(page_title="SmartSave Cloud", page_icon="📱", layout="wide")

# Oturum Durumu Kontrolü
if 'user' not in st.session_state:
    st.session_state.user = None

# --- 2. GİRİŞ VE KAYIT EKRANI ---
if st.session_state.user is None:
    st.title("🔐 SmartSave: Bulut Kasan")
    tab_in, tab_up = st.tabs(["Giriş Yap", "Kayıt Ol"])
    
    with tab_in:
        email = st.text_input("E-posta Adresin")
        pw = st.text_input("Şifre", type="password")
        if st.button("Kasayı Aç 🔓", use_container_width=True):
            if email and pw: # Şimdilik basit giriş, Firebase ekleyene kadar her şifreyi kabul eder
                st.session_state.user = email
                st.rerun()
            else:
                st.warning("Lütfen bilgileri doldur.")
    
    with tab_up:
        st.info("Kayıt sistemi şu an test aşamasında. Yukarıdan direkt giriş yapabilirsin.")
    st.stop() # Giriş yapılmadıysa kodun devamını çalıştırma (Siyah ekranı önler)

# --- 3. KULLANICIYA ÖZEL VERİ YÜKLEME ---
# Her kullanıcının verisi kendi e-posta adıyla kaydedilir
user_id = st.session_state.user.replace('@', '_').replace('.', '_')
DATA_FILE = f"data_{user_id}.csv"
CONFIG_FILE = f"config_{user_id}.txt"

if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
    df["Tarih"] = pd.to_datetime(df["Tarih"], errors='coerce').fillna(datetime.now())
else:
    df = pd.DataFrame(columns=["Tarih", "Tür", "İsim", "Kategori", "Miktar", "Tip"])

if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r") as f:
        try: kayitli_fiyat = int(float(f.read().strip()))
        except: kayitli_fiyat = 75000
else:
    kayitli_fiyat = 75000

# --- 4. SIDEBAR (YÖNETİM) ---
with st.sidebar:
    st.markdown(f"### 👋 Hoş geldin,\n**{st.session_state.user.split('@')[0]}**")
    if st.button("Güvenli Çıkış"):
        st.session_state.user = None
        st.rerun()
    
    st.divider()
    yeni_fiyat = st.number_input("iPhone Hedef (TL)", value=int(kayitli_fiyat), step=1000)
    if yeni_fiyat != kayitli_fiyat:
        with open(CONFIG_FILE, "w") as f: f.write(str(int(yeni_fiyat)))
        st.rerun()

    with st.form("yeni_islem", clear_on_submit=True):
        tur = st.selectbox("İşlem", ["Gider 🔻", "Gelir 🔺"])
        isim = st.text_input("Açıklama")
        kat = st.selectbox("Kategori", ["🍔 Yemek", "🛒 Market", "🚌 Ulaşım", "🎮 Eğlence", "🏠 Kira/Fatura", "👕 Giyim", "💵 Maaş", "🚀 Yatırım"])
        tip = st.selectbox("Tip", ["Zorunlu ✅", "Keyfi ✨"]) if "Gider" in tur else "Gelir"
        tutar = st.number_input("Tutar", min_value=1)
        if st.form_submit_button("Sisteme İşle"):
            yeni = pd.DataFrame([{"Tarih": datetime.now(), "Tür": "Gider" if "Gider" in tur else "Gelir", "İsim": isim, "Kategori": kat, "Miktar": int(tutar), "Tip": tip}])
            df = pd.concat([df, yeni], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.rerun()

# --- 5. ANA EKRAN ANALİZLER ---
net_bakiye = df[df["Tür"] == "Gelir"]["Miktar"].sum() - df[df["Tür"] == "Gider"]["Miktar"].sum()
st.markdown(f"### 🎯 iPhone Yolculuğu: %{min((net_bakiye/yeni_fiyat)*100, 100):.1f}")
st.progress(min(net_bakiye/yeni_fiyat, 1.0))

c1, c2, c3 = st.columns(3)
c1.metric("Net Bakiye", f"₺{int(net_bakiye):,}")
c2.metric("Kalan Hedef", f"₺{max(int(yeni_fiyat - net_bakiye), 0):,}")
c3.metric("İşlem Sayısı", len(df))

# Grafikler
col_l, col_r = st.columns(2)
with col_l:
    if not df[df["Tür"]=="Gider"].empty:
        fig_pie = px.pie(df[df["Tür"]=="Gider"], names="Kategori", values="Miktar", hole=0.6, title="Gider Dağılımı")
        st.plotly_chart(fig_pie, use_container_width=True)
with col_r:
    if not df.empty:
        df_sorted = df.sort_values("Tarih")
        df_sorted["Bakiye"] = df_sorted.apply(lambda x: x["Miktar"] if x["Tür"]=="Gelir" else -x["Miktar"], axis=1).cumsum()
        fig_line = px.area(df_sorted, x="Tarih", y="Bakiye", title="Birikim Grafiği")
        st.plotly_chart(fig_line, use_container_width=True)

st.divider()
st.subheader("📜 Son İşlemler")
st.dataframe(df.iloc[::-1], use_container_width=True, hide_index=True)
