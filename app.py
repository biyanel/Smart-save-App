import streamlit as st
import pandas as pd

# Sayfa Ayarları
st.set_page_config(page_title="SmartSave PRO", page_icon="💎")

st.title("💎 SmartSave PRO")
st.write("Verileriniz geçici olarak oturumda saklanıyor.")

# Şimdilik verileri Session State'de tutalım (Hata almamak için)
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["İsim", "Kategori", "Miktar"])

with st.form("harcama_ekle"):
    isim = st.text_input("Harcama Kalemi")
    miktar = st.number_input("Tutar (TL)", min_value=1)
    submit = st.form_submit_button("Kaydet ✨")

if submit and isim:
    yeni_satir = pd.DataFrame([{"İsim": isim, "Miktar": miktar}])
    st.session_state.data = pd.concat([st.session_state.data, yeni_satir], ignore_index=True)
    st.success(f"{isim} kaydedildi!")
    st.balloons()

# Verileri Göster
if not st.session_state.data.empty:
    st.table(st.session_state.data)
    st.metric("Toplam", f"{st.session_state.data['Miktar'].sum()} TL")
