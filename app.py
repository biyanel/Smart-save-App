# --- EXCEL / CSV İNDİRME BÖLÜMÜ ---
st.divider()
st.subheader("📊 Rapor Al")

if not df.empty:
    # Veriyi CSV formatına çeviriyoruz
    csv = df.to_csv(index=False).encode('utf-8')
    
    col_dl1, col_dl2 = st.columns([1, 2])
    with col_dl1:
        st.download_button(
            label="💾 Excel Olarak İndir (CSV)",
            data=csv,
            file_name=f"Finans_Raporum_{datetime.now().strftime('%d_%m_%Y')}.csv",
            mime="text/csv",
            help="Tüm harcama ve gelir geçmişini indirir."
        )
    with col_dl2:
        st.caption("İndirdiğin dosyayı Excel, Google Tablolar veya Not Defteri ile açabilirsin.")
else:
    st.info("İndirilecek veri bulunamadı. Önce bir işlem girmelisin!")
