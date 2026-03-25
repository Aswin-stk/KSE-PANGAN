import streamlit as st
import pandas as pd

# ==========================================
# KONFIGURASI HALAMAN & BRANDING
# ==========================================
st.set_page_config(
    page_title="KSE-PANGAN Banjarmasin", 
    page_icon="🐟", 
    layout="wide"
)

# Sidebar untuk Identitas Tim TRI-ALFA
with st.sidebar:
    st.title("🚀 TRI-ALFA Team")
    st.info("""
    **Proyek:** KSE-PANGAN  
    *(Kalkulasi Substitusi Ekonomi – Pemantauan Alternatif Navigasi Gizi Akurat Nyaman)* 
    **Subtema:** Ketahanan Pangan & Pertanian  
    **Lokasi:** Kota Banjarmasin
    """)
    st.write("---")
    st.caption("Hadir sebagai asisten cerdas untuk membantu Ibu Rumah Tangga dan Pengelola MBG dalam menjaga ketersediaan gizi keluarga dan masyarakat. Kami memberikan solusi belanja hemat dengan mencari sumber protein alternatif yang berkualitas saat harga ayam sedang naik.")

# ==========================================
# 1. DATABASE & URL (GOOGLE SHEETS)
# ==========================================
# Link CSV dari Google Sheets "SiDipan" milikmu
URL_HARGA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQk5Z47-GViLwEwBGDpOOg22RCCCmZ75UUHJJjVuPgWmG1_JLAfOI7lUTnEnQ5os5l9-t0RKApg88S7/pub?gid=0&single=true&output=csv"
URL_GIZI = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQk5Z47-GViLwEwBGDpOOg22RCCCmZ75UUHJJjVuPgWmG1_JLAfOI7lUTnEnQ5os5l9-t0RKApg88S7/pub?gid=1878695965&single=true&output=csv"

# Pemisahan kategori agar navigasi menu lebih cerdas (tidak hanya Tahu/Tempe)
KATEGORI_PROT = {
    'Ayam': 'Hewani', 'Telur': 'Hewani', 'Ikan Bandeng': 'Hewani', 
    'Ikan Kembung': 'Hewani', 'Ikan Tongkol': 'Hewani', 'Ikan Patin': 'Hewani', 
    'Ikan Nila': 'Hewani', 'Ikan Haruan': 'Hewani', 'Tahu': 'Nabati', 'Tempe': 'Nabati'
}

# ==========================================
# 2. FUNGSI PENDUKUNG (HELPERS)
# ==========================================

@st.cache_data(ttl=60)
def load_data(url):
    """Membaca data realtime dari Google Sheets."""
    try:
        return pd.read_csv(url)
    except:
        return None

def hitung_protein(budget, harga_per_kg, bdd, protein_100g):
    """Logika perhitungan protein berdasarkan bagian yang dapat dimakan (BDD)."""
    if harga_per_kg <= 0: return 0
    # Rumus: (Budget/Harga * 1000 * BDD/100) / 100 * Protein_per_100g
    berat_beli_gr = (budget / harga_per_kg) * 1000
    berat_bersih = berat_beli_gr * (bdd / 100)
    total_p = (berat_bersih / 100) * protein_100g
    return round(total_p, 1)

# ==========================================
# 3. PROSES DATA & TAMPILAN DASHBOARD
# ==========================================

df_harga = load_data(URL_HARGA)
df_gizi = load_data(URL_GIZI)

if df_harga is not None and df_gizi is not None:
    # Pre-processing Angka
    kolom_angka = ['Ayam', 'Telur', 'Ikan Bandeng', 'Ikan Kembung', 'Ikan Tongkol', 
                   'Ikan Patin', 'Ikan Nila', 'Ikan Haruan', 'Tahu', 'Tempe']
    for col in kolom_angka:
        if col in df_harga.columns:
            df_harga[col] = pd.to_numeric(df_harga[col], errors='coerce')

    st.title("🐟 KSE-PANGAN")
    st.markdown("### Aplikasi Monitor Inflasi Pangan dan Navigasi Substitusi Protein untuk Optimalisasi Program Makan Bergizi Gratis (MBG) di Banjarmasin")
    with st.sidebar:
        st.write("---")
        tgl_update_data = df_harga['Tanggal'].iloc[-1]
        
        # Kartu Status Data (Dinamis)
        st.markdown(f"""
        <div style="background-color:#1e293b; border-radius:8px; padding:12px; margin-top:15px; border: 1px solid #334155;">
            <div style="font-size:11px; color:#94a3b8; text-transform:uppercase; letter-spacing:0.5px;">📅 Data Terakhir:</div>
            <div style="font-size:20px; font-weight:bold; color:#ffffff; margin-top:2px;">{tgl_update_data}</div>
            <div style="margin-top:5px; font-size:11px; font-weight:bold; color:#10b981;">● UPDATE HARIAN</div>
        </div>
    """, unsafe_allow_html=True)
        st.caption("Status: Sinkronisasi Data Berhasil ✅")

    st.write("---") # Garis pemisah agar rapi

    # --- BAGIAN 1: GRAFIK TREN HARGA ---
    st.subheader("📈 Tren Harga Pangan Strategis")
    komoditas_trend = ['Ayam', 'Telur', 'Ikan Bandeng', 'Ikan Kembung', 'Ikan Tongkol']
    pilihan_grafik = st.multiselect("Pilih Komoditas:", options=komoditas_trend, default=['Ayam', 'Ikan Kembung'])
    
    if pilihan_grafik:
        df_plot = df_harga.set_index('Tanggal')[pilihan_grafik]
        st.line_chart(df_plot)

    st.write("---")
    
    # Deteksi Harga Terbaru & EWS
    df_harga['Tanggal'] = pd.to_datetime(df_harga['Tanggal'])
    data_terbaru = df_harga.iloc[-1]
    harga_ayam_skrg = data_terbaru['Ayam']
    rata_rata_ayam = df_harga[df_harga['Tanggal'].dt.year == 2025]['Ayam'].mean()
    batas_aman = rata_rata_ayam * 1.10 # Threshold 10%

    if harga_ayam_skrg > batas_aman:
        # Hitung persentase kenaikan
        kenaikan_persen = ((harga_ayam_skrg - rata_rata_ayam) / rata_rata_ayam) * 100
        selisih_harga = harga_ayam_skrg - rata_rata_ayam

        # Tampilan EWS yang lebih Informatif
        st.markdown(f"""
            <div style="background-color:#451a1a; border: 1px solid #ff4b4b; padding:15px; border-radius:10px; margin-bottom:20px;">
                <div style="display: flex; align-items: center;">
                    <span style="font-size:30px; margin-right:15px;">🚨</span>
                    <div>
                        <b style="color:#ff4b4b; font-size:16px;">EARLY WARNING SYSTEM (EWS)</b><br>
                        <span style="color:#f8d7da; font-size:14px;">
                            Harga Ayam saat ini <b>Rp {harga_ayam_skrg:,.0f}</b>, naik <b>{kenaikan_persen:.1f}%</b> 
                            di atas rata-rata normal (Rp {rata_rata_ayam:,.0f}).
                        </span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Tambahkan metrik kecil untuk memperkuat data
        m1, m2, m3 = st.columns(3)
        m1.metric("Harga Saat Ini", f"Rp {harga_ayam_skrg:,.0f}", f"+{kenaikan_persen:.1f}%", delta_color="inverse")
        m2.metric("Batas Aman (T)", f"Rp {batas_aman:,.0f}")
        m3.metric("Selisih Inflasi", f"Rp {selisih_harga:,.0f}", delta_color="inverse")
        
        # KALKULATOR & LOGIKA EWS ---
        st.write("---")
        st.subheader("💰 Kalkulator Navigasi Gizi Cerdas")
        budget_user = st.number_input("Masukkan Budget Belanja Lauk (Rp):", min_value=5000, value=25000, step=1000)

    # Pengolahan List Rekomendasi
    list_hewani = []
    list_nabati = []
    
    for _, row in df_gizi.iterrows():
        nama = row['Komoditas']
        if nama in data_terbaru:
            h_saat_ini = data_terbaru[nama]
            p_hasil = hitung_protein(budget_user, h_saat_ini, row['BDD'], row['Protein'])
            
            item_info = {
                'nama': nama, 'ikon': row['Ikon'], 
                'protein': p_hasil, 'harga': h_saat_ini,
                'gambar': row['Gambar'] # Mengambil link Pinterest dari Sheets
            }
            
            if KATEGORI_PROT.get(nama) == 'Hewani':
                list_hewani.append(item_info)
            else:
                list_nabati.append(item_info)

    # Sorting
    list_hewani = sorted(list_hewani, key=lambda x: x['protein'], reverse=True)
    list_nabati = sorted(list_nabati, key=lambda x: x['protein'], reverse=True)

    # --- TAMPILAN REKOMENDASI ESTETIK ---

    # 1. Baris Protein Hewani
    st.write("---") # Garis pemisah transisi
    st.markdown("##### <br>Berdasarkan harga pasar terbaru, ini pilihan lauk sehat dan hemat untuk Anda:", unsafe_allow_html=True)
    st.markdown("""
            <div style="background: linear-gradient(90deg, #dc2626, #f87171); padding:15px; border-radius:12px; margin-top:20px; margin-bottom:20px; text-align:center; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);">
                <span style="font-size:30px; vertical-align:middle; margin-right:10px;">🥩</span>
                <span style="color:white; font-size:26px; font-weight:bold;">Protein Hewani Utama</span>
                <p style="color:white; font-size:14px; margin:0; font-weight:normal;">Prioritas Tinggi untuk Pertumbuhan & Gizi MBG</p>
            </div>
        """, unsafe_allow_html=True)

    cols_h = st.columns(3)
    for idx, item in enumerate(list_hewani[:3]):
        with cols_h[idx]:
            st.image(item['gambar'], use_container_width=True) 
            st.success(f"**{item['ikon']} {item['nama']}**")
            st.metric("Total Protein", f"{item['protein']} gr")
            st.caption(f"Harga: Rp {item['harga']:,.0f}/kg")

    # 2. Baris Protein Nabati
    st.markdown("""
            <div style="background: linear-gradient(90deg, #ea580c, #fb923c); padding:15px; border-radius:12px; margin-top:20px; margin-bottom:20px; text-align:center; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);">
                <span style="font-size:30px; vertical-align:middle; margin-right:10px;">🍱</span>
                <span style="color:white; font-size:26px; font-weight:bold;">Protein Nabati (Pendamping)</span>
                <p style="color:white; font-size:14px; margin:0; font-weight:normal;">Opsi Efisiensi Anggaran & Diversifikasi Serat</p>
            </div>
        """, unsafe_allow_html=True)

    cols_n = st.columns(2)
    for idx, item in enumerate(list_nabati[:2]):
        with cols_n[idx]:
            st.image(item['gambar'], use_container_width=True)
            st.info(f"**{item['ikon']} {item['nama']}**")
            st.metric("Total Protein", f"{item['protein']} gr")
            st.caption(f"Harga: Rp {item['harga']:,.0f}/kg")

    # 3. Fitur Lihat Opsi Lainnya
    st.write("")
    with st.expander("🔍 Lihat Opsi Alternatif Lainnya"):
        gabungan_sisa = list_hewani[3:] + list_nabati[2:]
        gabungan_sisa = sorted(gabungan_sisa, key=lambda x: x['protein'], reverse=True)
        if gabungan_sisa:
            cols_alt = st.columns(3)
            for idx, item in enumerate(gabungan_sisa):
                with cols_alt[idx % 3]:
                    st.image(item['gambar'], use_container_width=True)
                    st.write(f"**{item['ikon']} {item['nama']}**")
                    st.write(f"Protein: {item['protein']} gr")
        else:
            st.write("Semua opsi sudah ditampilkan.")

    with st.expander("📊 Lihat Tabel Perbandingan Lengkap"):
        df_tabel = pd.DataFrame(list_hewani + list_nabati)
        df_tabel['protein'] = df_tabel['protein'].apply(lambda x: f"{x:.1f} gr")
        df_tabel['harga'] = df_tabel['harga'].apply(lambda x: f"Rp {x:,.0f}")
        df_tabel = df_tabel.rename(columns={
            'ikon': '',
            'nama': 'Nama Komoditas',
            'protein': 'Total Protein (gr)',
            'harga': 'Harga Saat Ini'
        })
        st.table(df_tabel[['', 'Nama Komoditas', 'Total Protein (gr)', 'Harga Saat Ini']])

st.write("---")
st.caption("© 2026 Tim TRI-ALFA (KSE ULM) | Data Source: Badan Pangan Nasional & Survey Lokal Banjarmasin.")
