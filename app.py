import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="SmartSave PRO", page_icon="💎")

st.title("💎 SmartSave PRO")

# Google Sheets Bağlantısı (Basitleştirilmiş)
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Verileri oku - 'ttl' kullanarak önbelleği tazeliyoruz
    df = conn.read(ttl="0") 
except Exception as e:
    st.error("Bağlantı henüz kurulmadı. Lütfen Secrets kısmını kontrol edin.")
    df = pd.DataFrame(columns=["İsim", "Miktar"])

# --- GİRİŞ FORMU ---
with st.form(key="harcama_formu"):
    isim = st.text_input("Harcama Kalemi")
    miktar = st.number_input("Tutar (TL)", min_value=1)
    submit = st.form_submit_button("Hemen Kaydet ✨")

if submit and isim:
    # Yeni satırı mevcut verilere ekle
    yeni_satir = pd.DataFrame([{"İsim": isim, "Miktar": miktar}])
    df = pd.concat([df, yeni_satir], ignore_index=True)
    
    # Tabloya yaz
    conn.update(data=df)
    st.success("Başarıyla Google Tablo'ya eklendi!")
    st.balloons()

# --- VERİLERİ GÖSTER ---
st.divider()
if not df.empty:
    st.subheader("📊 Güncel Harcamaların")
    st.dataframe(df, use_container_width=True)
    st.metric("Toplam Harcama", f"{df['Miktar'].sum()} TL")
