import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# --- GÜVENLİK ---
DOGRU_PIN = "1234"
if 'giris_yapildi' not in st.session_state: st.session_state.giris_yapildi = False
if not st.session_state.giris_yapildi:
    st.set_page_config(page_title="SmartSave Lock", page_icon="🔐")
    col_p1, col_p2, col_p3 = st.columns([1,2,1])
    with col_p2:
        st.markdown("<h2 style='text-align: center;'>🔐 KASA KİLİDİ</h2>", unsafe_allow_html=True)
        pin = st.text_input("", type="password", placeholder="****")
        if st.button("Sistemi Aç", use_container_width=True):
            if pin == DOGRU_PIN:
                st.session_state.giris_yapildi = True
                st.rerun()
    st.stop()

st.set_page_config(page_title="SmartSave v7", page_icon="📱", layout="wide")

# --- VERİ YÜKLEME ---
DATA_FILE = "finans_verileri.csv"
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
    df["Tarih"] = pd.to_datetime(df["Tarih"], dayfirst=True)
else:
    df = pd.DataFrame(columns=["Tarih", "Tür", "İsim", "Kategori", "Miktar"])

# --- SIDEBAR: STRATEJİ MERKEZİ ---
with st.sidebar:
    st.title("📱 iPhone Stratejisi")
    hedef_tutar = st.number_input("iPhone Fiyatı (TL)", min_value=1000, value=75000)
    
    st.divider()
    with st.form("hizli_islem", clear_on_submit=True):
        st.subheader("Hızlı Kayıt")
        tur = st.selectbox("Tür", ["Gider 🔻", "Gelir 🔺"])
        isim = st.text_input("Açıklama")
        kat = st.selectbox("Kategori", ["🍔 Yemek", "🛒 Market", "🚌 Ulaşım", "🎮 Eğlence", "🏠 Kira", "👕 Giyim", "💵 Maaş", "🚀 Yatırım"])
        tutar = st.number_input("Tutar", min_value=1)
        if st.form_submit_button("Ekle"):
            tarih = datetime.now().strftime("%d/%m/%Y %H:%M")
            yeni = pd.DataFrame([{"Tarih": tarih, "Tür": "Gider" if "Gider" in tur else "Gelir", "İsim": isim, "Kategori": kat, "Miktar": tutar}])
            df = pd.concat([df, yeni], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.rerun()

# --- HESAPLAMALAR ---
toplam_gelir = df[df["Tür"] == "Gelir"]["Miktar"].sum()
toplam_gider = df[df["Tür"] == "Gider"]["Miktar"].sum()
net_birikim = toplam_gelir - toplam_gider
yuzde = min((net_birikim / hedef_tutar) * 100, 100) if hedef_tutar > 0 else 0

# --- ANA EKRAN ---
c1, c2 = st.columns([2, 1])

with c1:
    st.subheader("🎯 Hedefe Giden Yol")
    # İlerleme Çubuğu Tasarımı
    st.progress(yuzde / 100)
    st.write(f"Şu an iPhone'un **%{yuzde:.1f}** kadarı senin! (Kalan: {max(hedef_tutar - net_birikim, 0):,} TL)")

    # TAHMİN MOTORU
    st.divider()
    st.subheader("🔮 Gelecek Tahmini")
    if len(df) > 5:
        # Son 30 günlük ortalama birikim hızı
        gunluk_hiz = net_birikim / ( (datetime.now() - df["Tarih"].min()).days + 1)
        if gunluk_hiz > 0:
            kalan_gun = (hedef_tutar - net_birikim) / gunluk_hiz
            kavusma_tarihi = datetime.now() + timedelta(days=kalan_gun)
            st.info(f"💡 Bu hızla gidersen iPhone'una **{kavusma_tarihi.strftime('%d %B %Y')}** tarihinde kavuşacaksın.")
        else:
            st.warning("⚠️ Birikim hızın şu an ekside! Bu gidişle iPhone hayal olabilir, hemen tasarruf et!")
    else:
        st.info("Tahmin yapabilmem için biraz daha harcama girmelisin.")

with c2:
    st.subheader("📉 iPhone Tasarruf Önerisi")
    yemek_gideri = df[df["Kategori"] == "🍔 Yemek"]["Miktar"].sum()
    if yemek_gideri > 0:
        tasarruf = yemek_gideri * 0.2
        st.success(f"🍔 Yemek harcamalarını %20 kısarsan hedefine **{int(tasarruf)} TL** daha hızlı yaklaşırsın!")

# --- GÖRSEL ANALİZ ---
st.divider()
st_col1, st_col2 = st.columns(2)

with st_col1:
    st.write("### 🍕 Giderlerin Röntgene")
    fig_pie = px.sunburst(df[df["Tür"]=="Gider"], path=['Kategori', 'İsim'], values='Miktar', color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig_pie, use_container_width=True)

with st_col2:
    st.write("### 📅 Birikim Grafiği")
    df_sorted = df.sort_values("Tarih")
    df_sorted["Kumulatif"] = df_sorted.apply(lambda x: x["Miktar"] if x["Tür"]=="Gelir" else -x["Miktar"], axis=1).cumsum()
    fig_line = px.area(df_sorted, x="Tarih", y="Kumulatif", title="Paran Nasıl Büyüyor?", color_discrete_sequence=['#636EFA'])
    st.plotly_chart(fig_line, use_container_width=True)



st.divider()
st.subheader("📜 Geçmiş İşlemler")
st.dataframe(df.iloc[::-1], use_container_width=True)
