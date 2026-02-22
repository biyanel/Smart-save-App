import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# --- TEMA AYARLARI (GECE / GÜNDÜZ) ---
# Not: Streamlit'te tam dinamik tema değişimi için config dosyası gerekir. 
# Ancak biz uygulama içinden grafik renklerini ve kartları buna göre manipüle edeceğiz.

st.set_page_config(page_title="SmartSave v5", page_icon="🌙", layout="wide")

DATA_FILE = "finans_verileri.csv"

# Verileri yükle
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
    df["Tarih"] = pd.to_datetime(df["Tarih"], dayfirst=True)
else:
    df = pd.DataFrame(columns=["Tarih", "Tür", "İsim", "Kategori", "Miktar"])

# --- SIDEBAR: TEMA VE GİRİŞ ---
with st.sidebar:
    st.title("🌓 SmartSave Panel")
    mode = st.toggle("Gece Modu Grafikleri", value=True)
    tema_rengi = "plotly_dark" if mode else "plotly_white"
    kart_bg = "#1E1E1E" if mode else "#F0F2F6"
    yazi_rengi = "white" if mode else "black"
    
    st.divider()
    st.header("📥 Veri Girişi")
    islem_turu = st.radio("İşlem Türü", ["Gider 🔻", "Gelir 🔺"])
    
    with st.form(key="islem_formu", clear_on_submit=True):
        isim = st.text_input("Açıklama")
        if islem_turu == "Gider 🔻":
            kat_listesi = ["🍔 Yemek", "🛒 Market", "🚌 Ulaşım", "🎮 Eğlence", "🏠 Kira/Fatura", "👕 Giyim", "📦 Diğer"]
        else:
            kat_listesi = ["💵 Maaş", "📈 Yatırım Karı", "🎁 Hediye", "🛠️ Ek İş", "💰 Diğer"]
            
        kategori = st.selectbox("Kategori", kat_listesi)
        miktar = st.number_input("Tutar (TL)", min_value=1)
        submit = st.form_submit_button("Kaydet ✨")

if submit and isim:
    tarih = datetime.now().strftime("%d/%m/%Y %H:%M")
    yeni_satir = pd.DataFrame([{
        "Tarih": tarih, 
        "Tür": "Gider" if "Gider" in islem_turu else "Gelir",
        "İsim": isim, "Kategori": kategori, "Miktar": miktar
    }])
    yeni_satir["Tarih"] = pd.to_datetime(yeni_satir["Tarih"], dayfirst=True)
    df = pd.concat([df, yeni_satir], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)
    st.rerun()

# --- ÜST ÖZET KARTLARI (ÖZEL TASARIM) ---
toplam_gelir = df[df["Tür"] == "Gelir"]["Miktar"].sum()
toplam_gider = df[df["Tür"] == "Gider"]["Miktar"].sum()
net_durum = toplam_gelir - toplam_gider

st.markdown(f"""
    <div style="display: flex; justify-content: space-around; padding: 10px;">
        <div style="background-color: {kart_bg}; padding: 20px; border-radius: 15px; border-left: 5px solid #00CC96; width: 30%;">
            <p style="color: {yazi_rengi}; margin-bottom: 5px;">Toplam Gelir</p>
            <h2 style="color: #00CC96; margin: 0;">₺{toplam_gelir}</h2>
        </div>
        <div style="background-color: {kart_bg}; padding: 20px; border-radius: 15px; border-left: 5px solid #EF553B; width: 30%;">
            <p style="color: {yazi_rengi}; margin-bottom: 5px;">Toplam Gider</p>
            <h2 style="color: #EF553B; margin: 0;">₺{toplam_gider}</h2>
        </div>
        <div style="background-color: {kart_bg}; padding: 20px; border-radius: 15px; border-left: 5px solid #636EFA; width: 30%;">
            <p style="color: {yazi_rengi}; margin-bottom: 5px;">Bakiye</p>
            <h2 style="color: #636EFA; margin: 0;">₺{net_durum}</h2>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- GRAFİKLER ---
st.divider()
col_sol, col_sag = st.columns(2)

with col_sol:
    st.subheader("⚖️ Durum Analizi")
    fig_compare = go.Figure(data=[
        go.Bar(name='Gelir', x=['Kasa'], y=[toplam_gelir], marker_color='#00CC96'),
        go.Bar(name='Gider', x=['Kasa'], y=[toplam_gider], marker_color='#EF553B')
    ])
    fig_compare.update_layout(template=tema_rengi, barmode='group', height=350, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_compare, use_container_width=True)

with col_sag:
    st.subheader("🍕 Giderler")
    gider_df = df[df["Tür"] == "Gider"]
    if not gider_df.empty:
        fig_pie = px.pie(gider_df, names="Kategori", values="Miktar", hole=0.5)
        fig_pie.update_layout(template=tema_rengi, height=350, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_pie, use_container_width=True)

# --- LİSTE ---
st.subheader("📜 Son Hareketler")
st.dataframe(df.iloc[::-1], use_container_width=True, hide_index=True)
