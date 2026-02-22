import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="SmartSave PRO", page_icon="💎", layout="wide")

# Google Sheets Bağlantısı
conn = st.connection("gsheets", type=GSheetsConnection)

# Verileri oku (Eğer tablo boşsa hata vermemesi için try-except)
try:
    df = conn.read()
except:
    df = pd.DataFrame(columns=["İsim", "Kategori", "Miktar"])

st.title("💎 SmartSave PRO: Kalıcı Hafıza")

# --- GİRİŞ FORMU ---
with st.form(key="harcama_formu"):
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        isim = st.text_input("Harcama Kalemi")
    with col2:
        kategori = st.selectbox("Kategori", ["🍔 Yemek", "🛒 Market", "🚌 Ulaşım", "🎮 Eğlence", "📈 Yatırım"])
    with col3:
        miktar = st.number_input("Tutar (TL)", min_value=1)
    
    submit = st.form_submit_button("Kalıcı Olarak Kaydet ✨")

if submit:
    yeni_satir = pd.DataFrame([{"İsim": isim, "Kategori": kategori, "Miktar": miktar}])
    df = pd.concat([df, yeni_satir], ignore_index=True)
    conn.update(worksheet="Sayfa1", data=df) # Google Tablo'ndaki sayfa adı 'Sayfa1' değilse değiştir
    st.success("Harcama Google Tablo'ya işlendi!")
    st.balloons()

# --- GÖRSELLEŞTİRME ---
if not df.empty:
    st.divider()
    st.metric("Toplam Birikmiş Harcama", f"{df['Miktar'].sum()} TL")
    st.bar_chart(df.set_index('Kategori')['Miktar'])
