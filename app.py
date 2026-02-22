import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
# --- GÜVENLİK AYARI ---
DOGRU_PIN = "1234"  # Buraya kendi 4 haneli şifreni yaz!

if 'giris_yapildi' not in st.session_state:
    st.session_state.giris_yapildi = False

if not st.session_state.giris_yapildi:
    st.title("🔐 SmartSave Koruması")
    pin = st.text_input("Giriş için 4 haneli PIN giriniz:", type="password")
    if st.button("Giriş Yap"):
        if pin == DOGRU_PIN:
            st.session_state.giris_yapildi = True
            st.success("Giriş Başarılı!")
            st.rerun()
        else:
            st.error("Hatalı PIN! Tekrar deneyin.")
    st.stop() # Şifre doğru değilse kodun geri kalanını çalıştırma!

# --- BURADAN SONRASI MEVCUT KODLARIN (df yükleme, grafikler vs.) ---

import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# --- GÜVENLİK VE AYARLAR ---
DOGRU_PIN = "1234"
if 'giris_yapildi' not in st.session_state: st.session_state.giris_yapildi = False
if not st.session_state.giris_yapildi:
    st.set_page_config(page_title="SmartSave Lock", page_icon="🔐")
    col_p1, col_p2, col_p3 = st.columns([1,2,1])
    with col_p2:
        st.markdown("<h2 style='text-align: center;'>🔐 PIN GİRİŞİ</h2>", unsafe_allow_html=True)
        pin = st.text_input("", type="password", placeholder="****")
        if st.button("Sistemi Aç", use_container_width=True):
            if pin == DOGRU_PIN:
                st.session_state.giris_yapildi = True
                st.rerun()
    st.stop()

st.set_page_config(page_title="SmartSave v6", page_icon="🚀", layout="wide")

# --- VERİ VE FONKSİYONLAR ---
DATA_FILE = "finans_verileri.csv"
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
    df["Tarih"] = pd.to_datetime(df["Tarih"], dayfirst=True)
else:
    df = pd.DataFrame(columns=["Tarih", "Tür", "İsim", "Kategori", "Miktar"])

# --- SIDEBAR: YENİ NESİL GİRİŞ ---
with st.sidebar:
    st.title("🚀 SmartSave v6")
    tab1, tab2 = st.tabs(["➕ İşlem", "🎯 Hedefler"])
    
    with tab1:
        islem_turu = st.selectbox("Tür", ["Gider 🔻", "Gelir 🔺"])
        with st.form("form_v6", clear_on_submit=True):
            isim = st.text_input("Açıklama")
            kategoriler = ["🍔 Yemek", "🛒 Market", "🚌 Ulaşım", "🎮 Eğlence", "🏠 Kira", "👕 Giyim", "📦 Diğer"] if "Gider" in islem_turu else ["💵 Maaş", "🚀 Yatırım", "🎁 Hediye", "🔧 Ek İş"]
            kat = st.selectbox("Kategori", kategoriler)
            tutar = st.number_input("Tutar", min_value=1)
            if st.form_submit_button("Kaydet"):
                tarih = datetime.now().strftime("%d/%m/%Y %H:%M")
                yeni = pd.DataFrame([{"Tarih": tarih, "Tür": "Gider" if "Gider" in islem_turu else "Gelir", "İsim": isim, "Kategori": kat, "Miktar": tutar}])
                df = pd.concat([df, yeni], ignore_index=True)
                df.to_csv(DATA_FILE, index=False)
                st.rerun()

    with tab2:
        st.subheader("Birikim Hedefi")
        hedef_ad = st.text_input("Hedef Ne? (Örn: iPhone)")
        hedef_tutar = st.number_input("Hedef Tutar", min_value=1000, value=50000)
        st.info(f"Hedefe ulaşmak için harcamalarını kısman gerekebilir!")

# --- ANA EKRAN: ANALİZ ---
toplam_gelir = df[df["Tür"] == "Gelir"]["Miktar"].sum()
toplam_gider = df[df["Tür"] == "Gider"]["Miktar"].sum()
net = toplam_gelir - toplam_gider

# 🎯 HEDEF GÖSTERGESİ (Gauge Chart)
st.subheader("🎯 Hedef Takibi")
fig_target = go.Figure(go.Indicator(
    mode = "gauge+number+delta",
    value = net if net > 0 else 0,
    domain = {'x': [0, 1], 'y': [0, 1]},
    title = {'text': f"{hedef_ad} İçin Birikim Durumu", 'font': {'size': 24}},
    delta = {'reference': hedef_tutar, 'increasing': {'color': "green"}},
    gauge = {
        'axis': {'range': [None, hedef_tutar], 'tickwidth': 1},
        'bar': {'color': "#636EFA"},
        'bgcolor': "white",
        'borderwidth': 2,
        'steps': [
            {'range': [0, hedef_tutar*0.5], 'color': '#FFCCCC'},
            {'range': [hedef_tutar*0.5, hedef_tutar], 'color': '#CCFFCC'}],
        'threshold': {
            'line': {'color': "red", 'width': 4},
            'thickness': 0.75,
            'value': hedef_tutar}}))
st.plotly_chart(fig_target, use_container_width=True)



# 💡 AKILLI TAVSİYELER
st.divider()
st.subheader("💡 Finansal Asistan Notu")
eglence_harcama = df[(df["Kategori"] == "🎮 Eğlence") & (df["Tür"] == "Gider")]["Miktar"].sum()
if eglence_harcama > net * 0.2:
    st.warning(f"🚨 Eğlence harcamaların ({eglence_harcama} TL) bakiyene oranla biraz yüksek! Bu hafta dışarı çıkmak yerine evde film izleyebilirsin.")
elif net > 0:
    st.success(f"✅ Harika gidiyorsun! Şu an kasan artıda. Kalan {net} TL'nin bir kısmını yatırıma ayırmaya ne dersin?")
else:
    st.error("❌ Dikkat! Giderlerin gelirini aşmış durumda. Acil tasarruf moduna geçmelisin!")

# 📊 TAKVİM ISI HARİTASI (Basitleştirilmiş)
st.divider()
st.subheader("📅 Günlük Harcama Yoğunluğu")
if not df.empty:
    df['Sadece_Tarih'] = pd.to_datetime(df['Tarih']).dt.date
    daily_trend = df[df["Tür"]=="Gider"].groupby('Sadece_Tarih')['Miktar'].sum().reset_index()
    fig_heat = px.bar(daily_trend, x='Sadece_Tarih', y='Miktar', color='Miktar', 
                     color_continuous_scale='Reds', title="Hangi Gün Ne Kadar Kaçtı?")
    st.plotly_chart(fig_heat, use_container_width=True)

st.divider()
st.subheader("📜 Tüm Hareketler")
st.dataframe(df.iloc[::-1], use_container_width=True)
