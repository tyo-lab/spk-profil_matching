
import pandas as pd

# Profil ideal berdasarkan notebook Google Colab
KRITERIA = {
    "Akademik": 5,
    "Kedisiplinan": 5,
    "Kehadiran": 5,
    "Prestasi_Nonakademik": 4
}

CORE_FACTOR = ["Akademik", "Kedisiplinan"]

SECONDARY_FACTOR = [
    "Kehadiran",
    "Prestasi_Nonakademik"
]

BOBOT_CF = 0.60
BOBOT_SF = 0.40

# Pemetaan nilai GAP
PETA_BOBOT = {
    0: 5.0,
    1: 4.5,
    -1: 4.0,
    2: 3.5,
    -2: 3.0,
    3: 2.5,
    -3: 2.0,
    4: 1.5,
    -4: 1.0
}


def hitung_profile_matching(df):
    df = df.copy()

    # Memastikan kolom kriteria tersedia
    kolom_wajib = ["NIS", "Nama"] + list(KRITERIA.keys())

    for kolom in kolom_wajib:
        if kolom not in df.columns:
            raise ValueError(f"Kolom {kolom} tidak ditemukan!")

    # Menghitung GAP
    for kolom, ideal in KRITERIA.items():
        df[f"GAP_{kolom}"] = df[kolom] - ideal

    # Mengubah GAP menjadi bobot
    for kolom in KRITERIA:
        df[f"Bobot_{kolom}"] = (
            df[f"GAP_{kolom}"].map(PETA_BOBOT)
        )

    # Menghitung Core Factor
    kolom_cf = [f"Bobot_{k}" for k in CORE_FACTOR]
    df["NCF"] = df[kolom_cf].mean(axis=1)

    # Menghitung Secondary Factor
    kolom_sf = [f"Bobot_{k}" for k in SECONDARY_FACTOR]
    df["NSF"] = df[kolom_sf].mean(axis=1)

    # Menghitung nilai akhir
    df["Nilai_Akhir"] = (
        BOBOT_CF * df["NCF"] +
        BOBOT_SF * df["NSF"]
    ).round(2)

    # Mengurutkan ranking
    df = df.sort_values(
        by="Nilai_Akhir",
        ascending=False
    ).reset_index(drop=True)

    df.insert(0, "Ranking", range(1, len(df) + 1))

    return df
