import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
# --- GÜVENLİK AYARI ---
DOGRU_PIN = "1234"  # Buraya kendi 4 haneli şifreni yaz!

if 'giris_yapildi' not in st.session_state:
    st.session_state.giris_yapildi = False

if not st.session_state.giris_yapildi:
    st.title("🔐 SmartSave Koruması")
    pin = st.text_input("Giriş için 4 haneli PIN giriniz:", type="password")
    if st.button("Giriş Yap"):
        if pin == DOGRU_PIN:
            st.session_state.giris_yapildi = True
            st.success("Giriş Başarılı!")
            st.rerun()
        else:
            st.error("Hatalı PIN! Tekrar deneyin.")
    st.stop() # Şifre doğru değilse kodun geri kalanını çalıştırma!

# --- BURADAN SONRASI MEVCUT KODLARIN (df yükleme, grafikler vs.) ---

import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# --- GÜVENLİK ---
DOGRU_PIN = "1234" # Burayı güncellemeyi unutma!

if 'giris_yapildi' not in st.session_state:
    st.session_state.giris_yapildi = False

if not st.session_state.giris_yapildi:
    st.set_page_config(page_title="SmartSave Lock", page_icon="🔐")
    st.markdown("<h2 style='text-align: center;'>🔐 SmartSave Güvenlik</h2>", unsafe_allow_html=True)
    col_p1, col_p2, col_p3 = st.columns([1,2,1])
    with col_p2:
        pin = st.text_input("4 Haneli PIN", type="password", placeholder="****")
        if st.button("Kasayı Aç 🔓", use_container_width=True):
            if pin == DOGRU_PIN:
                st.session_state.giris_yapildi = True
                st.rerun()
            else:
                st.error("Hatalı PIN!")
    st.stop()

# --- ANA UYGULAMA AYARLARI ---
st.set_page_config(page_title="SmartSave Premium", page_icon="💎", layout="wide")

# Kategori ve İkon Eşleşmesi
KAT_IKONLARI = {
    "🍔 Yemek": "🍴", "🛒 Market": "🛍️", "🚌 Ulaşım": "🚲", 
    "🎮 Eğlence": "🕹️", "🏠 Kira/Fatura": "🔌", "👕 Giyim": "👟", 
    "📦 Diğer": "🌀", "💵 Maaş": "💰", "📈 Yatırım Karı": "🚀", 
    "🎁 Hediye": "🎀", "🛠️ Ek İş": "🔧", "💰 Diğer": "✨"
}

DATA_FILE = "finans_verileri.csv"
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
    df["Tarih"] = pd.to_datetime(df["Tarih"], dayfirst=True)
else:
    df = pd.DataFrame(columns=["Tarih", "Tür", "İsim", "Kategori", "Miktar"])

# --- SIDEBAR TASARIMI ---
with st.sidebar:
    st.markdown("<h1 style='color: #636EFA;'>💎 SmartSave v5.5</h1>", unsafe_allow_html=True)
    mode = st.toggle("Gece Modu Grafikleri", value=True)
    tema_rengi = "plotly_dark" if mode else "plotly_white"
    kart_bg = "#1E1E1E" if mode else "#FFFFFF"
    yazi_rengi = "white" if mode else "#31333F"
    
    st.divider()
    islem_turu = st.radio("İşlem Türü", ["Gider 🔻", "Gelir 🔺"], horizontal=True)
    
    with st.form(key="islem_formu", clear_on_submit=True):
        isim = st.text_input("Açıklama", placeholder="Örn: Starbucks Kahve")
        kat_listesi = list(KAT_IKONLARI.keys())[:7] if "Gider" in islem_turu else list(KAT_IKONLARI.keys())[7:]
        kategori = st.selectbox("Kategori", kat_listesi)
        miktar = st.number_input("Tutar (TL)", min_value=1, step=10)
        submit = st.form_submit_button("Sisteme Kaydet ✨", use_container_width=True)

if submit and isim:
    tarih = datetime.now().strftime("%d/%m/%Y %H:%M")
    yeni_satir = pd.DataFrame([{"Tarih": tarih, "Tür": "Gider" if "Gider" in islem_turu else "Gelir", "İsim": isim, "Kategori": kategori, "Miktar": miktar}])
    df = pd.concat([df, yeni_satir], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)
    st.toast(f"{isim} başarıyla eklendi!", icon='✅')
    st.rerun()

# --- ÜST ÖZET KARTLARI ---
toplam_gelir = df[df["Tür"] == "Gelir"]["Miktar"].sum()
toplam_gider = df[df["Tür"] == "Gider"]["Miktar"].sum()
net_durum = toplam_gelir - toplam_gider

st.markdown(f"""
    <div style="display: flex; flex-wrap: wrap; gap: 15px; justify-content: space-between; margin-bottom: 25px;">
        <div style="flex: 1; min-width: 200px; background: {kart_bg}; padding: 20px; border-radius: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border-top: 6px solid #00CC96;">
            <p style="color: {yazi_rengi}; font-size: 0.9rem; margin: 0; opacity: 0.7;">Toplam Gelir 🔺</p>
            <h2 style="color: #00CC96; margin: 5px 0;">₺{toplam_gelir:,.0f}</h2>
        </div>
        <div style="flex: 1; min-width: 200px; background: {kart_bg}; padding: 20px; border-radius: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border-top: 6px solid #EF553B;">
            <p style="color: {yazi_rengi}; font-size: 0.9rem; margin: 0; opacity: 0.7;">Toplam Gider 🔻</p>
            <h2 style="color: #EF553B; margin: 5px 0;">₺{toplam_gider:,.0f}</h2>
        </div>
        <div style="flex: 1; min-width: 200px; background: {kart_bg}; padding: 20px; border-radius: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border-top: 6px solid #636EFA;">
            <p style="color: {yazi_rengi}; font-size: 0.9rem; margin: 0; opacity: 0.7;">Kasa Bakiyesi 🏦</p>
            <h2 style="color: #636EFA; margin: 5px 0;">₺{net_durum:,.0f}</h2>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- GRAFİKLER ---
c1, c2 = st.columns(2)
with c1:
    st.markdown("### ⚖️ Gelir-Gider Dengesi")
    fig = go.Figure(data=[
        go.Bar(name='Gelir', x=['Finans'], y=[toplam_gelir], marker_color='#00CC96', text=f"₺{toplam_gelir}", textposition='auto'),
        go.Bar(name='Gider', x=['Finans'], y=[toplam_gider], marker_color='#EF553B', text=f"₺{toplam_gider}", textposition='auto')
    ])
    fig.update_layout(template=tema_rengi, height=350, barmode='group', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.markdown("### 🍕 Gider Dağılımı")
    gider_df = df[df["Tür"] == "Gider"]
    if not gider_df.empty:
        fig_p = px.pie(gider_df, names="Kategori", values="Miktar", hole=0.6, color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_p.update_layout(template=tema_rengi, height=350, margin=dict(t=20, b=20, l=0, r=0), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_p, use_container_width=True)

# --- TABLO VE RAPOR ---
st.divider()
st.markdown("### 📜 Son Hareketler")
st.dataframe(df.iloc[::-1], use_container_width=True, hide_index=True)

csv = df.to_csv(index=False).encode('utf-8')
st.download_button("📥 Full Raporu İndir (.csv)", csv, "finans_raporum.csv", "text/csv", use_container_width=True)
