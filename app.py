import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="SmartSave PRO v2", page_icon="💎", layout="wide")

DATA_FILE = "harcamalar.csv"

# Verileri yükle
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(columns=["Tarih", "İsim", "Kategori", "Miktar"])

st.title("💎 SmartSave PRO: Akıllı Bütçe Yönetimi")

# --- YAN PANEL (BÜTÇE AYARI) ---
with st.sidebar:
    st.header("⚙️ Ayarlar")
    butce_limiti = st.number_input("Aylık Harcama Hedefin (TL)", min_value=100, value=5000, step=100)
    
    st.divider()
    st.header("➕ Yeni Harcama")
    with st.form(key="form", clear_on_submit=True):
        isim = st.text_input("Harcama Kalemi")
        kategori = st.selectbox("Kategori", ["🍔 Yemek", "🛒 Market", "🚌 Ulaşım", "🎮 Eğlence", "📈 Yatırım", "🏠 Kira/Fatura", "👕 Giyim"])
        miktar = st.number_input("Tutar (TL)", min_value=1)
        submit = st.form_submit_button("Sisteme İşle ✨")

if submit and isim:
    tarih = datetime.now().strftime("%d/%m/%Y %H:%M")
    yeni_satir = pd.DataFrame([{"Tarih": tarih, "İsim": isim, "Kategori": kategori, "Miktar": miktar}])
    df = pd.concat([df, yeni_satir], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)
    st.toast("Kayıt Başarılı!", icon='✅')
    st.rerun()

# --- BÜTÇE TAKİP GÖSTERGESİ (PROGRESS BAR) ---
toplam_harcama = df['Miktar'].sum()
oran = min(toplam_harcama / butce_limiti, 1.0)

st.subheader("🏁 Bütçe Durumu")
col_metric, col_bar = st.columns([1, 3])

with col_metric:
    st.metric("Kalan Limit", f"{max(butce_limiti - toplam_harcama, 0)} TL")

with col_bar:
    bar_rengi = "green" if oran < 0.7 else "orange" if oran < 0.9 else "red"
    st.progress(oran)
    st.write(f"Bütçenin %{int(oran*100)}'ini kullandın. (Hedef: {butce_limiti} TL)")



# --- ANALİZ VE LİSTE ---
st.divider()
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("📊 Harcama Dağılımı")
    if not df.empty:
        category_totals = df.groupby("Kategori")["Miktar"].sum()
        st.plotly_chart({
            "data": [{"labels": category_totals.index, "values": category_totals.values, "type": "pie", "hole": .5}],
            "layout": {"margin": dict(t=0, b=0, l=0, r=0)}
        }, use_container_width=True)

with col_right:
    st.subheader("📜 Son İşlemler")
    if not df.empty:
        # Tabloyu tersten göster (en yeni en üstte)
        st.dataframe(df.iloc[::-1], use_container_width=True, hide_index=True)
    else:
        st.info("Henüz işlem yok.")

# --- KAYIT YÖNETİMİ ---
with st.expander("🗑️ Kayıtları Düzenle/Sil"):
    for index, row in df.iterrows():
        c1, c2, c3, c4 = st.columns([2, 3, 2, 1])
        c1.caption(row["Tarih"])
        c2.write(row["İsim"])
        c3.write(f"{row['Miktar']} TL")
        if c4.button("Sil", key=f"del_{index}"):
            df = df.drop(index)
            df.to_csv(DATA_FILE, index=False)
            st.rerun()
