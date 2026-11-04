
import streamlit as st
import pandas as pd

from perhitungan import hitung_profile_matching, KRITERIA


# =====================================
# KONFIGURASI APLIKASI
# =====================================

st.set_page_config(
    page_title="SPK Siswa Berprestasi",
    page_icon="🏆",
    layout="wide"
)

NAMA_DATASET_AWAL = "dataset_siswa_1000.csv"

KOLOM_WAJIB = [
    "NIS",
    "Nama",
    "Akademik",
    "Kedisiplinan",
    "Kehadiran",
    "Prestasi_Nonakademik"
]


# =====================================
# FUNGSI VALIDASI DATA
# =====================================

def validasi_data(df):
    df = df.copy()
    df.columns = df.columns.str.strip()

    kolom_hilang = [
        kolom for kolom in KOLOM_WAJIB
        if kolom not in df.columns
    ]

    if kolom_hilang:
        raise ValueError(
            "Kolom tidak ditemukan: " + ", ".join(kolom_hilang)
        )

    df = df[KOLOM_WAJIB].copy()

    if df.isnull().any().any():
        raise ValueError("Dataset memiliki data kosong.")

    kolom_nilai = [
        "Akademik",
        "Kedisiplinan",
        "Kehadiran",
        "Prestasi_Nonakademik"
    ]

    for kolom in kolom_nilai:
        df[kolom] = pd.to_numeric(
            df[kolom],
            errors="coerce"
        )

    if df[kolom_nilai].isnull().any().any():
        raise ValueError("Nilai kriteria harus berupa angka.")

    for kolom in kolom_nilai:
        if not df[kolom].between(1, 5).all():
            raise ValueError(
                f"Nilai {kolom} harus berada antara 1 sampai 5."
            )

    df["NIS"] = df["NIS"].astype(str).str.strip()
    df["Nama"] = df["Nama"].astype(str).str.strip()

    if (df["NIS"] == "").any() or (df["Nama"] == "").any():
        raise ValueError("NIS dan Nama tidak boleh kosong.")

    if df["NIS"].duplicated().any():
        raise ValueError("Terdapat NIS yang duplikat.")

    return df


# =====================================
# MEMUAT DATASET AWAL
# =====================================

if "df_aktif" not in st.session_state:
    try:
        df_awal = pd.read_csv(NAMA_DATASET_AWAL)
        df_awal = validasi_data(df_awal)

        st.session_state["df_aktif"] = df_awal
        st.session_state["sumber_data"] = NAMA_DATASET_AWAL

    except Exception as e:
        st.session_state["df_aktif"] = None
        st.session_state["sumber_data"] = "Belum ada dataset"
        st.session_state["error_dataset"] = str(e)


# =====================================
# JUDUL APLIKASI
# =====================================

st.title("🏆 Sistem Pendukung Keputusan")
st.subheader("Penilaian Siswa Berprestasi")
st.caption("Menggunakan Metode Profile Matching")
st.divider()


# =====================================
# MENU SIDEBAR
# =====================================

st.sidebar.title("Menu Utama")

menu = st.sidebar.radio(
    "Pilih Menu",
    [
        "Dashboard",
        "Input Data Siswa",
        "Data Siswa",
        "Data Kriteria",
        "Perhitungan",
        "Hasil Ranking"
    ]
)

df = st.session_state["df_aktif"]

st.sidebar.divider()
st.sidebar.caption(
    f"Dataset aktif: {st.session_state['sumber_data']}"
)


# =====================================
# MENU INPUT DATA SISWA
# =====================================

if menu == "Input Data Siswa":

    st.header("📂 Input Data Siswa")

    st.write(
        "Upload file CSV untuk melakukan perhitungan "
        "Profile Matching secara otomatis."
    )

    template = pd.DataFrame(columns=KOLOM_WAJIB)

    st.download_button(
        label="📥 Download Template CSV",
        data=template.to_csv(index=False).encode("utf-8"),
        file_name="template_data_siswa.csv",
        mime="text/csv"
    )

    uploaded_file = st.file_uploader(
        "Pilih file CSV",
        type=["csv"]
    )

    if uploaded_file is not None:

        try:
            df_upload = pd.read_csv(uploaded_file)
            df_upload = validasi_data(df_upload)

            st.success("Format dataset berhasil diperiksa.")

            st.subheader("Preview Data Siswa")

            st.dataframe(
                df_upload.head(10),
                use_container_width=True,
                hide_index=True
            )

            st.info(f"Jumlah siswa: {len(df_upload)}")

            if st.button(
                "🚀 Proses Profile Matching",
                type="primary"
            ):

                st.session_state["df_aktif"] = df_upload
                st.session_state["sumber_data"] = uploaded_file.name

                st.success("Data berhasil diproses!")

                st.rerun()

        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")

    st.divider()

    st.subheader("Dataset yang Digunakan")

    if df is not None:
        st.info(
            f"Dataset aktif: {st.session_state['sumber_data']}"
        )
        st.write(f"Jumlah siswa: {len(df)}")
    else:
        st.warning("Belum ada dataset yang digunakan.")

    if st.button("Kembali ke Dataset Awal"):

        try:
            df_awal = pd.read_csv(NAMA_DATASET_AWAL)
            df_awal = validasi_data(df_awal)

            st.session_state["df_aktif"] = df_awal
            st.session_state["sumber_data"] = NAMA_DATASET_AWAL

            st.success("Dataset awal berhasil digunakan.")
            st.rerun()

        except Exception as e:
            st.error(f"Gagal memuat dataset awal: {e}")


# =====================================
# MENU LAINNYA
# =====================================

else:

    if df is None:
        st.warning(
            "Dataset belum tersedia. Silakan upload CSV "
            "melalui menu Input Data Siswa."
        )
        st.stop()

    try:
        hasil = hitung_profile_matching(df)

    except Exception as e:
        st.error(f"Kesalahan perhitungan: {e}")
        st.stop()


    # =================================
    # DASHBOARD
    # =================================

    if menu == "Dashboard":

        st.header("Dashboard")

        col1, col2, col3 = st.columns(3)

        col1.metric("Jumlah Siswa", len(df))
        col2.metric("Jumlah Kriteria", len(KRITERIA))
        col3.metric(
            "Nilai Tertinggi",
            hasil["Nilai_Akhir"].max()
        )

        st.divider()

        st.subheader("🏆 10 Siswa Terbaik")

        st.dataframe(
            hasil[
                ["Ranking", "NIS", "Nama", "Nilai_Akhir"]
            ].head(10),
            use_container_width=True,
            hide_index=True
        )

        st.subheader("Grafik Siswa Berprestasi")

        grafik = hasil.head(10).set_index("Nama")

        st.bar_chart(grafik["Nilai_Akhir"])


    # =================================
    # DATA SISWA
    # =================================

    elif menu == "Data Siswa":

        st.header("Data Siswa")

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )


    # =================================
    # DATA KRITERIA
    # =================================

    elif menu == "Data Kriteria":

        st.header("Data Kriteria")

        data_kriteria = pd.DataFrame({
            "Kriteria": list(KRITERIA.keys()),
            "Nilai Ideal": list(KRITERIA.values()),
            "Faktor": [
                "Core Factor",
                "Core Factor",
                "Secondary Factor",
                "Secondary Factor"
            ]
        })

        st.dataframe(
            data_kriteria,
            use_container_width=True,
            hide_index=True
        )

        st.write("Bobot Core Factor: 60%")
        st.write("Bobot Secondary Factor: 40%")


    # =================================
    # PERHITUNGAN
    # =================================

    elif menu == "Perhitungan":

        st.header("Hasil Perhitungan Profile Matching")

        st.dataframe(
            hasil,
            use_container_width=True,
            hide_index=True
        )


    # =================================
    # HASIL RANKING
    # =================================

    elif menu == "Hasil Ranking":

        st.header("🏆 Ranking Siswa Berprestasi")

        st.dataframe(
            hasil[
                [
                    "Ranking",
                    "NIS",
                    "Nama",
                    "NCF",
                    "NSF",
                    "Nilai_Akhir"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

        csv = hasil.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="📥 Download Hasil Ranking",
            data=csv,
            file_name="hasil_ranking_siswa.csv",
            mime="text/csv"
        )
