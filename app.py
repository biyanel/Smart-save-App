import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="SmartSave PRO", page_icon="💎")

# Bağlantı
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("💎 SmartSave PRO")

# Form
with st.form("ekle_form"):
    isim = st.text_input("Harcama")
    miktar = st.number_input("Tutar", min_value=1)
    kaydet = st.form_submit_button("Kaydet ✨")

if kaydet and isim:
    # Basit bir veri çerçevesi oluştur
    yeni_df = pd.DataFrame([{"İsim": isim, "Miktar": miktar}])
    
    # Mevcut veriyi oku ve yenisini ekle
    try:
        mevcut = conn.read()
        son_df = pd.concat([mevcut, yeni_df], ignore_index=True)
    except:
        son_df = yeni_df

    # TABLOYA YAZ (Burada hata veriyorsa bağlantı hala eskidir)
    conn.update(data=son_df)
    st.success("Tebrikler, ilk kalıcı verin kaydedildi!")
    st.balloons()

# Göster
try:
    st.table(conn.read())
except:
    st.info("Henüz veri yok.")
