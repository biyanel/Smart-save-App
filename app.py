import streamlit as st
import pandas as pd

st.set_page_config(page_title="SmartSave AI", page_icon="💰")

st.title("💰 SmartSave AI")
st.caption("Harcamalarını yönet, geleceğe yatırım yap.")

if 'harcamalar' not in st.session_state:
    st.session_state.harcamalar = []

with st.expander("➕ Yeni Harcama Ekle", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        isim = st.text_input("Nereye harcadın?")
        kategori = st.selectbox("Kategori", ["Yemek", "Market", "Ulaşım", "Eğlence", "Yatırım"])
    with col2:
        miktar = st.number_input("Tutar (TL)", min_value=1)
        ekle = st.button("Listeye Ekle")

    if ekle:
        st.session_state.harcamalar.append({"İsim": isim, "Kategori": kategori, "Miktar": miktar})
        st.success("Harcama kaydedildi!")

if st.session_state.harcamalar:
    df = pd.DataFrame(st.session_state.harcamalar)
    st.metric("Toplam Harcama", f"{df['Miktar'].sum()} TL")
    st.bar_chart(df.set_index('Kategori')['Miktar'])
else:
    st.info("Henüz harcama girmedin. Yukarıdan ilk harcamanı ekle!")
