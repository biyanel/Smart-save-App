import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="SmartSave PRO", page_icon="💎")

# Veri dosyası yolu
DATA_FILE = "harcamalar.csv"

# Verileri yükle veya yeni oluştur
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(columns=["İsim", "Kategori", "Miktar"])

st.title("💎 SmartSave PRO")
st.info("Verileriniz güvenle kaydediliyor!")

# --- GİRİŞ FORMU ---
with st.form(key="form"):
    col1, col2 = st.columns(2)
    with col1:
        isim = st.text_input("Harcama Kalemi")
        kategori = st.selectbox("Kategori", ["🍔 Yemek", "🛒 Market", "🚌 Ulaşım", "🎮 Eğlence"])
    with col2:
        miktar = st.number_input("Tutar (TL)", min_value=1)
    
    submit = st.form_submit_button("Hemen Kaydet ✨")

if submit and isim:
    yeni_satir = pd.DataFrame([{"İsim": isim, "Kategori": kategori, "Miktar": miktar}])
    df = pd.concat([df, yeni_satir], ignore_index=True)
    
    # VERİYİ KAYDET (Bulut dosyasına yazar)
    df.to_csv(DATA_FILE, index=False)
    
    st.success(f"'{isim}' kaydedildi!")
    st.balloons()

# --- ÖZET VE LİSTE ---
if not df.empty:
    st.divider()
    st.metric("Toplam Harcama", f"{df['Miktar'].sum()} TL")
    st.dataframe(df, use_container_width=True)
    
    # Verileri indirme butonu (Excel olarak almak istersen)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📊 Verileri İndir", csv, "harcamalarim.csv", "text/csv")
