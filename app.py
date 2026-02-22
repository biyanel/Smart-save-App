import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="SmartSave PRO", page_icon="💎")

# Bağlantıyı kur
conn = st.connection("gsheets", type=GSheetsConnection)

# Veriyi çek (Eğer hata verirse boş bir tablo yarat)
try:
    df = conn.read()
except:
    df = pd.DataFrame(columns=["İsim", "Kategori", "Miktar"])

st.title("💎 SmartSave PRO")

with st.form(key="form"):
    isim = st.text_input("Harcama")
    kat = st.selectbox("Kategori", ["Yemek", "Market", "Ulaşım", "Eğlence", "Yatırım"])
    mik = st.number_input("Tutar", min_value=1)
    btn = st.form_submit_button("Kaydet ✨")

if btn and isim:
    yeni = pd.DataFrame([{"İsim": isim, "Kategori": kat, "Miktar": mik}])
    # Veriyi birleştir
    if df is not None:
        df = pd.concat([df, yeni], ignore_index=True)
    else:
        df = yeni
        
    # VERİYİ YAZ (Hata payını sıfırlamak için en basit komut)
    conn.update(data=df)
    st.success("Kaydedildi!")
    st.balloons()

# Listele
if df is not None and not df.empty:
    st.table(df)
