# --- ÜST ÖZET KARTLARI (YENİLENMİŞ TASARIM) ---
st.markdown(f"""
    <style>
        .main-card-container {{
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            gap: 10px;
            margin-bottom: 20px;
        }}
        .info-card {{
            background-color: {kart_bg};
            padding: 15px;
            border-radius: 12px;
            flex: 1;
            min-width: 100px;
            border-bottom: 4px solid #636EFA;
            text-align: center;
        }}
        .card-label {{
            color: {yazi_rengi};
            font-size: 0.8rem;
            margin-bottom: 5px;
            opacity: 0.8;
        }}
        .card-value {{
            color: {yazi_rengi};
            font-size: 1.2rem;
            font-weight: bold;
            margin: 0;
            white-space: nowrap;
        }}
    </style>
    
    <div class="main-card-container">
        <div class="info-card" style="border-color: #00CC96;">
            <p class="card-label">Toplam Gelir</p>
            <p class="card-value" style="color: #00CC96;">₺{toplam_gelir:,}</p>
        </div>
        <div class="info-card" style="border-color: #EF553B;">
            <p class="card-label">Toplam Gider</p>
            <p class="card-value" style="color: #EF553B;">₺{toplam_gider:,}</p>
        </div>
        <div class="info-card" style="border-color: #636EFA;">
            <p class="card-label">Bakiye</p>
            <p class="card-value" style="color: #636EFA;">₺{net_durum:,}</p>
        </div>
    </div>
""", unsafe_allow_html=True)
