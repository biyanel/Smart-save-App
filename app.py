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

st.set_page_config(page_title="SmartSave v8.1", page_icon="📱", layout="wide")

# --- TÜRKÇE GÜN SÖZLÜĞÜ ---
GUNLER_TR = {
    "Monday": "Pazartesi", "Tuesday": "Salı", "Wednesday": "Çarşamba",
    "Thursday": "Perşembe", "Friday": "Cuma", "Saturday": "Cumartesi", "Sunday": "Pazar"
}

DATA_FILE = "finans_verileri.csv"
CONFIG_FILE = "ayarlar.txt"

# --- YARDIMCI FONKSİYONLAR ---
def ikon_bulucu(isim):
    sozluk = {"yemek": "🍔", "döner": "🌯", "kahve": "☕", "market": "🛒", "kira": "🏠", "fatura": "🔌", "ulaşım": "🚌", "maaş": "💰", "yatırım": "🚀"}
    for anahtar, ikon in sozluk.items():
        if anahtar in isim.lower(): return f"{ikon} {isim}"
    return f"✨ {isim}"

# --- VERİ VE AYAR YÜKLEME ---
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

# --- SIDEBAR ---
with st.sidebar:
    st.title("📱 iPhone Avcısı")
    yeni_fiyat = st.number_input("iPhone TL Fiyatı", value=int(kayitli_fiyat), step=1000)
    usd_kuru = st.number_input("Güncel USD Kuru", value=31.5, step=0.1)
    
    if yeni_fiyat != kayitli_fiyat:
        with open(CONFIG_FILE, "w") as f: f.write(str(int(yeni_fiyat)))
        st.rerun()
    
    st.divider()
    with st.form("hizli_kayit_v81", clear_on_submit=True):
        st.subheader("İşlem Ekle")
        tur = st.selectbox("Tür", ["Gider 🔻", "Gelir 🔺"])
        isim_in = st.text_input("Açıklama")
        kat = st.selectbox("Kategori", ["🍔 Yemek", "🛒 Market", "🚌 Ulaşım", "🎮 Eğlence", "🏠 Kira/Fatura", "👕 Giyim", "💵 Maaş", "🚀 Yatırım"])
        tip = st.selectbox("Tip", ["Zorunlu ✅", "Keyfi ✨"]) if "Gider" in tur else "Gelir"
        tutar = st.number_input("Tutar (TL)", min_value=1)
        if st.form_submit_button("Sisteme İşle ✨"):
            yeni = pd.DataFrame([{"Tarih": datetime.now(), "Tür": "Gider" if "Gider" in tur else "Gelir", "İsim": ikon_bulucu(isim_in), "Kategori": kat, "Miktar": int(tutar), "Tip": tip}])
            df = pd.concat([df, yeni], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.rerun()

# --- ANALİZLER ---
net_bakiye = df[df["Tür"] == "Gelir"]["Miktar"].sum() - df[df["Tür"] == "Gider"]["Miktar"].sum()
bugun_dt = datetime.now().date()
ay_sonu = (bugun_dt.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
kalan_gun = (ay_sonu - bugun_dt).days + 1
gunluk_limit = max((net_bakiye / kalan_gun), 0) if kalan_gun > 0 else 0
bugun_harcama = df[(df["Tarih"].dt.date == bugun_dt) & (df["Tür"] == "Gider")]["Miktar"].sum()

# --- DASHBOARD ---
st.markdown(f"### 🎯 Hedef İlerlemesi: %{min((net_bakiye/yeni_fiyat)*100, 100):.1f}")
st.progress(min(net_bakiye/yeni_fiyat, 1.0))

c1, c2, c3, c4 = st.columns(4)
c1.metric("Bakiye", f"₺{int(net_bakiye):,}")
c2.metric("Dolar Karşılığı", f"${(net_bakiye/usd_kuru):,.2f}")
c3.metric("Günlük Limit", f"₺{int(gunluk_limit):,}")
c4.metric("Kalan Hedef", f"₺{max(int(yeni_fiyat - net_bakiye), 0):,}")

# --- LİMİT UYARISI ---
if bugun_harcama > gunluk_limit:
    st.error(f"🚨 Bugün ₺{int(bugun_harcama - gunluk_limit)} kadar limitini aştın!")
else:
    st.success(f"✅ Harika! Bugün daha ₺{int(gunluk_limit - bugun_harcama)} harcama hakkın var.")

# --- 📅 TÜRKÇE GÜNLÜK ANALİZ ---
st.divider()
st.subheader("📅 Günlük Harcama Analizi")
if not df[df["Tür"]=="Gider"].empty:
    df_gider = df[df["Tür"]=="Gider"].copy()
    # İngilizce gün ismini al ve sözlükten Türkçesini bul
    df_gider['Gun_Ing'] = df_gider['Tarih'].dt.day_name()
    df_gider['Gün'] = df_gider['Gun_Ing'].map(GUNLER_TR)
    
    gunluk_grafik = df_gider.groupby('Gün')['Miktar'].sum().reindex(list(GUNLER_TR.values())).fillna(0)
    fig_gun = px.bar(x=gunluk_grafik.index, y=gunluk_grafik.values, color=gunluk_grafik.values,
                     labels={'x':'Haftanın Günü', 'y':'Toplam Gider (TL)'},
                     color_continuous_scale='Reds', title="Hangi Gün Ne Kadar Harcadın?")
    st.plotly_chart(fig_gun, use_container_width=True)

st.divider()
st.subheader("📜 İşlem Geçmişi")
# Tabloda tarihleri kullanıcı dostu yap
df_list = df.copy()
df_list["Tarih"] = df_list["Tarih"].dt.strftime('%d.%m.%Y %H:%M')
st.dataframe(df_list.iloc[::-1], use_container_width=True, hide_index=True)
