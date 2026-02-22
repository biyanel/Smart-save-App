import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="SmartSave v5.2", page_icon="💰", layout="wide")

DATA_FILE = "finans_verileri.csv"

# --- VERİ YÜKLEME ---
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
    df["Tarih"] = pd.to_datetime(df["Tarih"], dayfirst=True)
else:
    df = pd.DataFrame(columns=["Tarih", "Tür", "İsim", "Kategori", "Miktar"])

# --- DEĞİŞKENLER VE TEMA (HATAYI ÖNLEMEK İÇİN ÜSTTE) ---
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
        kat_listesi = ["🍔 Yemek", "🛒 Market", "🚌 Ulaşım", "🎮 Eğlence", "🏠 Kira/Fatura", "👕 Giyim", "📦 Diğer"] if "Gider" in islem_turu else ["💵 Maaş", "📈 Yatırım Karı", "🎁 Hediye", "🛠️ Ek İş", "💰 Diğer"]
        kategori = st.selectbox("Kategori", kat_listesi)
        miktar = st.number_input("Tutar (TL)", min_value=1)
        submit = st.form_submit_button("Kaydet ✨")

if submit and isim:
    tarih = datetime.now().strftime("%d/%m/%Y %H:%M")
    yeni_satir = pd.DataFrame([{"Tarih": tarih, "Tür": "Gider" if "Gider" in islem_turu else "Gelir", "İsim": isim, "Kategori": kategori, "Miktar": miktar}])
    yeni_satir["Tarih"] = pd.to_datetime(yeni_satir["Tarih"], dayfirst=True)
    df = pd.concat([df, yeni_satir], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)
    st.rerun()

# --- HESAPLAMALAR ---
toplam_gelir = df[df["Tür"] == "Gelir"]["Miktar"].sum()
toplam_gider = df[df["Tür"] == "Gider"]["Miktar"].sum()
net_durum = toplam_gelir - toplam_gider

# --- ÜST ÖZET KARTLARI (DÜZELTİLMİŞ TASARIM) ---
st.markdown(f"""
    <div style="display: flex; flex-wrap: wrap; justify-content: space-between; gap: 10px; margin-bottom: 20px;">
        <div style="background-color: {kart_bg}; padding: 15px; border-radius: 12px; flex: 1; min-width: 100px; border-bottom: 4px solid #00CC96; text-align: center;">
            <p style="color: {yazi_rengi}; font-size: 0.8rem; margin-bottom: 5px; opacity: 0.8;">Gelir</p>
            <p style="color: #00CC96; font-size: 1.2rem; font-weight: bold; margin: 0; white-space: nowrap;">₺{toplam_gelir:,.0f}</p>
        </div>
        <div style="background-color: {kart_bg}; padding: 15px; border-radius: 12px; flex: 1; min-width: 100px; border-bottom: 4px solid #EF553B; text-align: center;">
            <p style="color: {yazi_rengi}; font-size: 0.8rem; margin-bottom: 5px; opacity: 0.8;">Gider</p>
            <p style="color: #EF553B; font-size: 1.2rem; font-weight: bold; margin: 0; white-space: nowrap;">₺{toplam_gider:,.0f}</p>
        </div>
        <div style="background-color: {kart_bg}; padding: 15px; border-radius: 12px; flex: 1; min-width: 100px; border-bottom: 4px solid #636EFA; text-align: center;">
            <p style="color: {yazi_rengi}; font-size: 0.8rem; margin-bottom: 5px; opacity: 0.8;">Bakiye</p>
            <p style="color: #636EFA; font-size: 1.2rem; font-weight: bold; margin: 0; white-space: nowrap;">₺{net_durum:,.0f}</p>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- GRAFİKLER ---
c_sol, c_sag = st.columns(2)
with c_sol:
    fig_comp = go.Figure(data=[go.Bar(name='Gelir', x=['Kasa'], y=[toplam_gelir], marker_color='#00CC96'), go.Bar(name='Gider', x=['Kasa'], y=[toplam_gider], marker_color='#EF553B')])
    fig_comp.update_layout(template=tema_rengi, barmode='group', height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_comp, use_container_width=True)
with c_sag:
    gider_df = df[df["Tür"] == "Gider"]
    if not gider_df.empty:
        fig_pie = px.pie(gider_df, names="Kategori", values="Miktar", hole=0.5)
        fig_pie.update_layout(template=tema_rengi, height=300, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_pie, use_container_width=True)

st.subheader("📜 Son Hareketler")
st.dataframe(df.iloc[::-1], use_container_width=True, hide_index=True)
