import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="SmartSave PRO", page_icon="💎", layout="wide")

DATA_FILE = "harcamalar.csv"

# Verileri yükle
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(columns=["İsim", "Kategori", "Miktar"])

st.title("💎 SmartSave PRO")

# --- GİRİŞ FORMU ---
with st.sidebar:
    st.header("➕ Yeni Ekle")
    with st.form(key="form", clear_on_submit=True):
        isim = st.text_input("Harcama Kalemi")
        kategori = st.selectbox("Kategori", ["🍔 Yemek", "🛒 Market", "🚌 Ulaşım", "🎮 Eğlence", "📈 Yatırım", "🏠 Kira/Fatura"])
        miktar = st.number_input("Tutar (TL)", min_value=1)
        submit = st.form_submit_button("Sisteme İşle ✨")

if submit and isim:
    yeni_satir = pd.DataFrame([{"İsim": isim, "Kategori": kategori, "Miktar": miktar}])
    df = pd.concat([df, yeni_satir], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)
    st.toast(f"{isim} başarıyla eklendi!", icon='✅')
    st.rerun()

# --- ANALİZ EKRANI ---
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("📊 Harcama Dağılımı")
    if not df.empty:
        category_totals = df.groupby("Kategori")["Miktar"].sum()
        st.plotly_chart({
            "data": [{"labels": category_totals.index, "values": category_totals.values, "type": "pie", "hole": .5, "marker": {"colors": ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3']}}],
            "layout": {"showlegend": True, "margin": {"t":0, "b":0, "l":0, "r":0}}
        }, use_container_width=True)
    else:
        st.info("Henüz veri yok.")

with col_right:
    st.subheader("💰 Özet")
    st.metric("Toplam Harcama", f"{df['Miktar'].sum()} TL")
    st.metric("İşlem Sayısı", len(df))

st.divider()

# --- SİLME VE TABLO ---
st.subheader("🗑️ Kayıt Yönetimi")
if not df.empty:
    # Daha şık bir görünüm için tabloyu düzenliyoruz
    for index, row in df.iterrows():
        c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
        c1.write(f"**{row['İsim']}**")
        c2.info(row["Kategori"])
        c3.write(f"₺{row['Miktar']}")
        if c4.button("Sil", key=f"del_{index}", help="Bu harcamayı kalıcı olarak siler"):
            df = df.drop(index)
            df.to_csv(DATA_FILE, index=False)
            st.rerun()
else:
    st.write("Liste şu an boş.")

st.sidebar.divider()
csv = df.to_csv(index=False).encode('utf-8')
st.sidebar.download_button("💾 Excel Olarak İndir", csv, "finans_ozetim.csv", "text/csv")
