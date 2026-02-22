import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="SmartSave v4", page_icon="💰", layout="wide")

DATA_FILE = "finans_verileri.csv"

# Verileri yükle
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
    df["Tarih"] = pd.to_datetime(df["Tarih"], dayfirst=True)
else:
    df = pd.DataFrame(columns=["Tarih", "Tür", "İsim", "Kategori", "Miktar"])

st.title("💰 SmartSave v4: Finansal Dashboard")

# --- YAN PANEL (GİRİŞ) ---
with st.sidebar:
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
        submit = st.form_submit_button("Sisteme Kaydet ✨")

if submit and isim:
    tarih = datetime.now().strftime("%d/%m/%Y %H:%M")
    yeni_satir = pd.DataFrame([{
        "Tarih": tarih, 
        "Tür": "Gider" if "Gider" in islem_turu else "Gelir",
        "İsim": isim, 
        "Kategori": kategori, 
        "Miktar": miktar
    }])
    yeni_satir["Tarih"] = pd.to_datetime(yeni_satir["Tarih"], dayfirst=True)
    df = pd.concat([df, yeni_satir], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)
    st.toast("İşlem Başarıyla Kaydedildi!", icon='🚀')
    st.rerun()

# --- HESAPLAMALAR ---
toplam_gelir = df[df["Tür"] == "Gelir"]["Miktar"].sum()
toplam_gider = df[df["Tür"] == "Gider"]["Miktar"].sum()
net_durum = toplam_gelir - toplam_gider

# --- ÜST ÖZET KARTLARI ---
st.subheader("🏦 Finansal Özet")
c1, c2, c3 = st.columns(3)
c1.metric("Toplam Gelir", f"{toplam_gelir} TL", delta_color="normal")
c2.metric("Toplam Gider", f"-{toplam_gider} TL", delta_color="inverse")
c3.metric("Net Kasa (Bakiye)", f"{net_durum} TL", delta=f"{net_durum}", delta_color="normal")

# --- GRAFİKLER ---
st.divider()
col_sol, col_sag = st.columns(2)

with col_sol:
    st.subheader("⚖️ Gelir - Gider Dengesi")
    if not df.empty:
        fig_compare = go.Figure(data=[
            go.Bar(name='Gelir', x=['Finansal Durum'], y=[toplam_gelir], marker_color='#00CC96'),
            go.Bar(name='Gider', x=['Finansal Durum'], y=[toplam_gider], marker_color='#EF553B')
        ])
        fig_compare.update_layout(barmode='group', height=400)
        st.plotly_chart(fig_compare, use_container_width=True)

with col_sag:
    st.subheader("🍕 Gider Dağılımı")
    gider_df = df[df["Tür"] == "Gider"]
    if not gider_df.empty:
        fig_pie = px.pie(gider_df, names="Kategori", values="Miktar", hole=0.4, color_discrete_sequence=px.colors.qualitative.Safe)
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("Henüz gider verisi yok.")

# --- İŞLEM GEÇMİŞİ VE FİLTRE ---
st.divider()
st.subheader("📜 Tüm İşlemler")
filtre_turu = st.multiselect("Tür Seç", options=["Gelir", "Gider"], default=["Gelir", "Gider"])
filtreli_df = df[df["Tür"].isin(filtre_turu)]

st.dataframe(filtreli_df.iloc[::-1], use_container_width=True, hide_index=True)

with st.expander("🗑️ İşlemleri Yönet / Sil"):
    for index, row in df.iterrows():
        cols = st.columns([2, 1, 3, 2, 1])
        cols[0].caption(str(row["Tarih"]))
        cols[1].write("➕" if row["Tür"] == "Gelir" else "➖")
        cols[2].write(row["İsim"])
        cols[3].write(f"{row['Miktar']} TL")
        if cols[4].button("Sil", key=f"d_{index}"):
            df = df.drop(index)
            df.to_csv(DATA_FILE, index=False)
            st.rerun()
