import streamlit as st
import pandas as pd

# Sayfa Ayarları
st.set_page_config(page_title="SmartSave PRO", page_icon="💎", layout="wide")

# Özel CSS ile "Premium" Görünüm
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1f2937; padding: 15px; border-radius: 10px; border: 1px solid #374151; }
    </style>
    """, unsafe_allow_html=True)

st.title("💎 SmartSave PRO: Akıllı Finans")
st.write("Harcamalarını analiz et, geleceğini inşa et.")

if 'harcamalar' not in st.session_state:
    st.session_state.harcamalar = []

# --- GİRİŞ ALANI ---
with st.container():
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        isim = st.text_input("Harcama Kalemi", placeholder="Örn: Burger")
    with col2:
        kategori = st.selectbox("Kategori", ["🍔 Yemek", "🛒 Market", "🚌 Ulaşım", "🎮 Eğlence", "📈 Yatırım"])
    with col3:
        miktar = st.number_input("Tutar (TL)", min_value=1)
        ekle = st.button("Kaydet ✨", use_container_width=True)

if ekle:
    st.session_state.harcamalar.append({"İsim": isim, "Kategori": kategori, "Miktar": miktar})
    st.balloons()

# --- ANALİZ ALANI ---
if st.session_state.harcamalar:
    df = pd.DataFrame(st.session_state.harcamalar)
    
    c1, c2, c3 = st.columns(3)
    toplam = df['Miktar'].sum()
    c1.metric("Toplam Harcama", f"{toplam} TL", delta="-5%", delta_color="inverse")
    
    # Akıllı Yatırım Hesabı
    birikim_potansiyeli = toplam * 0.20
    c2.metric("Birikim Potansiyeli (%20)", f"{birikim_potansiyeli} TL")
    
    gelecek_deger = birikim_potansiyeli * 1.15 # %15 yıllık getiri varsayımı
    c3.metric("1 Yıl Sonraki Değeri", f"{gelecek_deger:.0f} TL")

    st.subheader("📊 Harcama Dağılımı")
    st.bar_chart(df.set_index('Kategori')['Miktar'])
