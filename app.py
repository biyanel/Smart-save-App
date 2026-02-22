import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="SmartSave PRO", page_icon="💎")

DATA_FILE = "harcamalar.csv"

# Verileri yükle
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(columns=["İsim", "Kategori", "Miktar"])

st.title("💎 SmartSave PRO")

# --- GİRİŞ FORMU ---
with st.expander("➕ Yeni Harcama Ekle", expanded=True):
    with st.form(key="form"):
        col1, col2 = st.columns(2)
        with col1:
            isim = st.text_input("Harcama Kalemi")
            kategori = st.selectbox("Kategori", ["🍔 Yemek", "🛒 Market", "🚌 Ulaşım", "🎮 Eğlence", "📈 Yatırım", "🏠 Kira/Fatura"])
        with col2:
            miktar = st.number_input("Tutar (TL)", min_value=1)
        
        submit = st.form_submit_button("Hemen Kaydet ✨")

if submit and isim:
    yeni_satir = pd.DataFrame([{"İsim": isim, "Kategori": kategori, "Miktar": miktar}])
    df = pd.concat([df, yeni_satir], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)
    st.success(f"'{isim}' kaydedildi!")
    st.rerun() # Sayfayı yenile ki grafik güncellensin

# --- ANALİZ VE GRAFİK BÖLÜMÜ ---
if not df.empty:
    st.divider()
    
    # Üst Bilgi Kartları
    col_a, col_b = st.columns(2)
    col_a.metric("Toplam Harcama", f"{df['Miktar'].sum()} TL")
    col_b.metric("İşlem Sayısı", len(df))

    # PASTA GRAFİĞİ
    st.subheader("📊 Harcama Dağılımı")
    # Kategorilere göre grupla ve pasta grafiği çiz
    category_totals = df.groupby("Kategori")["Miktar"].sum()
    st.plotly_chart({
        "data": [{"labels": category_totals.index, "values": category_totals.values, "type": "pie", "hole": .4}],
        "layout": {"title": "Nereye Ne Harcadın?"}
    }, use_container_width=True)
    
    

    # --- SİLME VE LİSTELEME ---
    st.subheader("📜 Harcama Listesi")
    
    # Her satır için bir silme butonu oluştur
    for index, row in df.iterrows():
        cols = st.columns([3, 2, 2, 1])
        cols[0].write(row["İsim"])
        cols[1].write(row["Kategori"])
        cols[2].write(f"{row['Miktar']} TL")
        if cols[3].button("🗑️", key=f"delete_{index}"):
            df = df.drop(index)
            df.to_csv(DATA_FILE, index=False)
            st.warning("Harcama silindi!")
            st.rerun()

    st.divider()
    # Verileri indirme
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("💾 Verileri Excel Olarak Al", csv, "harcamalarim.csv", "text/csv")
else:
    st.info("Henüz harcama girmedin. Hadi başlayalım!")
