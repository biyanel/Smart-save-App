import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px

st.set_page_config(page_title="SmartSave v3", page_icon="💎", layout="wide")

DATA_FILE = "harcamalar.csv"

# Verileri yükle
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
    df["Tarih"] = pd.to_datetime(df["Tarih"], dayfirst=True)
else:
    df = pd.DataFrame(columns=["Tarih", "İsim", "Kategori", "Miktar"])

st.title("💎 SmartSave v3: Analiz Üstadı")

# --- YAN PANEL ---
with st.sidebar:
    st.header("⚙️ Ayarlar")
    butce_limiti = st.number_input("Aylık Bütçe Hedefin", min_value=100, value=5000)
    
    st.divider()
    st.header("➕ Yeni Harcama")
    with st.form(key="form", clear_on_submit=True):
        isim = st.text_input("Harcama Kalemi")
        kategori = st.selectbox("Kategori", ["🍔 Yemek", "🛒 Market", "🚌 Ulaşım", "🎮 Eğlence", "📈 Yatırım", "🏠 Kira/Fatura", "👕 Giyim"])
        miktar = st.number_input("Tutar (TL)", min_value=1)
        submit = st.form_submit_button("Kaydet ✨")

if submit and isim:
    yeni_satir = pd.DataFrame([{"Tarih": datetime.now().strftime("%d/%m/%Y %H:%M"), "İsim": isim, "Kategori": kategori, "Miktar": miktar}])
    yeni_satir["Tarih"] = pd.to_datetime(yeni_satir["Tarih"], dayfirst=True)
    df = pd.concat([df, yeni_satir], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)
    st.toast("İşlem Başarılı!", icon='🚀')
    st.rerun()

# --- ÜST ÖZET KARTLARI ---
toplam = df['Miktar'].sum()
st.subheader("🏁 Genel Durum")
c1, c2, c3 = st.columns(3)
c1.metric("Toplam Harcama", f"{toplam} TL")
c2.metric("Kalan Bütçe", f"{max(butce_limiti - toplam, 0)} TL")
c3.progress(min(toplam/butce_limiti, 1.0))

# --- AKILLI UYARI ---
if toplam > butce_limiti * 0.8:
    st.warning(f"⚠️ Dikkat! Bütçenin %80'ini tükettin. Tasarruf moduna geçmeni öneririm!")

# --- GELİŞMİŞ ANALİZ ---
st.divider()
col_sol, col_sag = st.columns(2)

with col_sol:
    st.subheader("📊 Kategori Dağılımı")
    if not df.empty:
        fig_pie = px.pie(df, names="Kategori", values="Miktar", hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_pie, use_container_width=True)

with col_sag:
    st.subheader("📈 Harcama Trendi (Günlük)")
    if not df.empty:
        # Günlük toplamları hesapla
        daily_df = df.groupby(df['Tarih'].dt.date)['Miktar'].sum().reset_index()
        fig_line = px.line(daily_df, x="Tarih", y="Miktar", markers=True, line_shape="spline")
        st.plotly_chart(fig_line, use_container_width=True)

# --- FİLTRELEME VE LİSTE ---
st.divider()
st.subheader("🔍 Harcama Geçmişi")
secilen_kategori = st.multiselect("Kategorilere Göre Filtrele", options=df["Kategori"].unique(), default=df["Kategori"].unique())
filtreli_df = df[df["Kategori"].isin(secilen_kategori)]

st.dataframe(filtreli_df.iloc[::-1], use_container_width=True, hide_index=True)

with st.expander("🗑️ Kayıt Yönetimi (Silme)"):
    for index, row in df.iterrows():
        cols = st.columns([2, 3, 2, 1])
        cols[0].caption(str(row["Tarih"]))
        cols[1].write(row["İsim"])
        cols[2].write(f"{row['Miktar']} TL")
        if cols[3].button("Sil", key=f"d_{index}"):
            df = df.drop(index)
            df.to_csv(DATA_FILE, index=False)
            st.rerun()
