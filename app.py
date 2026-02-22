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

st.set_page_config(page_title="SmartSave v8.0", page_icon="📱", layout="wide")

DATA_FILE = "finans_verileri.csv"
CONFIG_FILE = "ayarlar.txt"

# --- YARDIMCI FONKSİYONLAR ---
def ikon_bulucu(isim):
    sozluk = {"yemek": "🍔", "döner": "🌯", "kahve": "☕", "market": "🛒", "kira": "🏠", "fatura": "🔌", "ulaşım": "🚌", "maaş": "💰", "yatırım": "🚀"}
    for anahtar, ikon in sozluk.items():
        if anahtar in isim.lower(): return f"{ikon} {isim}"
    return f"✨ {isim}"

# --- AYARLARI VE VERİLERİ YÜKLE ---
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r") as f:
        try: kayitli_fiyat = int(float(f.read().strip()))
        except: kayitli_fiyat = 75000
else: kayitli_fiyat = 75000

if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
    df["Tarih"] = pd.to_datetime(df["Tarih"], errors='coerce').fillna(datetime.now())
else:
    df = pd.DataFrame(columns=["Tarih", "Tür", "İsim", "Kategori", "Miktar", "Tip"])

# --- SIDEBAR: PRO AYARLAR ---
with st.sidebar:
    st.title("📱 iPhone Avcısı PRO")
    yeni_fiyat = st.number_input("iPhone TL Fiyatı", value=int(kayitli_fiyat), step=1000)
    usd_kuru = st.number_input("Güncel USD Kuru (Tahmini)", value=31.5, step=0.1)
    
    if yeni_fiyat != kayitli_fiyat:
        with open(CONFIG_FILE, "w") as f: f.write(str(int(yeni_fiyat)))
        st.rerun()
    
    st.divider()
    with st.form("hizli_kayit_v8", clear_on_submit=True):
        st.subheader("İşlem Ekle")
        tur = st.selectbox("Tür", ["Gider 🔻", "Gelir 🔺"])
        isim_in = st.text_input("Açıklama")
        kat = st.selectbox("Kategori", ["🍔 Yemek", "🛒 Market", "🚌 Ulaşım", "🎮 Eğlence", "🏠 Kira/Fatura", "👕 Giyim", "💵 Maaş", "🚀 Yatırım"])
        tip = st.selectbox("Tip", ["Zorunlu ✅", "Keyfi ✨"]) if "Gider" in tur else "Gelir"
        tutar = st.number_input("Tutar (TL)", min_value=1)
        if st.form_submit_button("Kaydet ✨"):
            yeni = pd.DataFrame([{"Tarih": datetime.now(), "Tür": "Gider" if "Gider" in tur else "Gelir", "İsim": ikon_bulucu(isim_in), "Kategori": kat, "Miktar": int(tutar), "Tip": tip}])
            df = pd.concat([df, yeni], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.rerun()

# --- HESAPLAMALAR ---
net_bakiye = df[df["Tür"] == "Gelir"]["Miktar"].sum() - df[df["Tür"] == "Gider"]["Miktar"].sum()
bugun_dt = datetime.now().date()
ay_sonu = (bugun_dt.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
kalan_gun = (ay_sonu - bugun_dt).days + 1
gunluk_limit = max((net_bakiye / kalan_gun), 0)

# Bugün ne kadar harcandı?
bugun_harcama = df[(df["Tarih"].dt.date == bugun_dt) & (df["Tür"] == "Gider")]["Miktar"].sum()

# --- ANALİZ DASHBOARD ---
st.markdown(f"### 🎯 Hedef İlerlemesi: %{min((net_bakiye/yeni_fiyat)*100, 100):.1f}")
st.progress(min(net_bakiye/yeni_fiyat, 1.0))

c1, c2, c3, c4 = st.columns(4)
c1.metric("Bakiye (TL)", f"₺{int(net_bakiye):,}")
c2.metric("Bakiye (USD)", f"${(net_bakiye/usd_kuru):,.2f}")
c3.metric("Günlük Limit", f"₺{int(gunluk_limit):,}")
c4.metric("iPhone USD", f"${(yeni_fiyat/usd_kuru):,.0f}")

# --- AKILLI UYARI SENSÖRÜ ---
if bugun_harcama > gunluk_limit:
    st.error(f"🚨 LİMİT AŞILDI! Bugün limitinden ₺{int(bugun_harcama - gunluk_limit)} fazla harcadın. iPhone bir adım uzaklaştı!")
elif bugun_harcama > gunluk_limit * 0.8:
    st.warning("⚠️ Sınırdasın! iPhone aşkına bugün başka harcama yapma.")
else:
    st.success(f"✅ Harikasın! Bugün daha ₺{int(gunluk_limit - bugun_harcama)} harcama iznin var.")

# --- GRAFİKLER ---
col_l, col_r = st.columns(2)
with col_l:
    st.write("### 🍩 Kategori Analizi")
    fig = px.pie(df[df["Tür"]=="Gider"], names="Kategori", values="Miktar", hole=0.6)
    st.plotly_chart(fig, use_container_width=True)

with col_r:
    st.write("### 💹 Birikim Tahmini (TL vs USD)")
    df_sorted = df.sort_values("Tarih")
    df_sorted["Bakiye_TL"] = df_sorted.apply(lambda x: x["Miktar"] if x["Tür"]=="Gelir" else -x["Miktar"], axis=1).cumsum()
    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(x=df_sorted["Tarih"], y=df_sorted["Bakiye_TL"], fill='tozeroy', name='TL Birikim'))
    st.plotly_chart(fig_line, use_container_width=True)

st.divider()
st.subheader("📜 Son Hareketler")
st.dataframe(df.iloc[::-1], use_container_width=True, hide_index=True)
