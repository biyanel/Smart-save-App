import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="SmartSave PRO", page_icon="💎", layout="wide")

# Google Sheets Bağlantısı
conn = st.connection("gsheets", type=GSheetsConnection)

# Mevcut verileri çekmeye çalış, yoksa boş tablo oluştur
try:
    df = conn.read()
    # Eğer tablo tamamen boşsa sütunları tanımla
    if df.empty:
        df = pd.DataFrame(columns=["İsim", "Kategori", "Miktar"])
except:
    df = pd.DataFrame(columns=["İsim", "Kategori", "Miktar"])

st.title("💎 SmartSave PRO")

# --- GİRİŞ FORMU ---
with st.form(key="harcama_formu"):
    c1, c2, c3 = st.columns([2, 2, 1])
    with c1:
        isim = st.text_input("Harcama Kalemi")
    with c2:
        kategori = st.selectbox("Kategori", ["🍔 Yemek", "🛒 Market", "🚌 Ulaşım", "🎮 Eğlence", "📈 Yatırım"])
    with c3:
        miktar = st.number_input("Tutar (TL)", min_value=1)
    
    submit = st.form_submit_button("Kalıcı Olarak Kaydet ✨")

if submit and isim:
    yeni_satir = pd.DataFrame([{"İsim": isim, "Kategori": kategori, "Miktar": miktar}])
    df = pd.concat([df, yeni_satir], ignore_index=True)
    
    # Tablodaki İLK sayfaya veriyi yaz (isimden bağımsız olması için)
    conn.update(data=df)
    st.success("Harcama kaydedildi! Google Tablo'nu kontrol et.")
    st.balloons()

# --- ANALİZ ---
if not df.empty:
    st.divider()
    st.metric("Toplam Harcama", f"{df['Miktar'].sum()} TL")
    st.bar_chart(df.set_index('Kategori')['Miktar'])
