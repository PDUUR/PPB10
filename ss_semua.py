import subprocess

daftar_perintah = [
    # 1. Environment & Utama
    ("kode\\cek_environment.py", "1_cek_environment.png"),
    ("kode\\cari_protein.py", "2_cari_protein_ft.png"),
    ("kode\\ambil_metadata.py", "3_ambil_metadata_ft.png"),
    ("kode\\ambil_sekuens.py", "4_ambil_sekuens_ft.png"),
    
    # 2. Latihan 1 Chitinase
    ("latihan\\chitinase\\kode\\cari_protein.py", "5_chitinase_cari.png"),
    ("latihan\\chitinase\\kode\\ambil_metadata.py", "6_chitinase_meta.png"),
    ("latihan\\chitinase\\kode\\ambil_sekuens.py", "7_chitinase_seq.png"),
    
    # 3. Latihan 1 Lectin
    ("latihan\\lectin\\kode\\cari_protein.py", "8_lectin_cari.png"),
    ("latihan\\lectin\\kode\\ambil_metadata.py", "9_lectin_meta.png"),
    ("latihan\\lectin\\kode\\ambil_sekuens.py", "10_lectin_seq.png"),
    
    # 4. Latihan 1 Alliinase
    ("latihan\\alliinase\\kode\\cari_protein.py", "11_alliinase_cari.png"),
    ("latihan\\alliinase\\kode\\ambil_metadata.py", "12_alliinase_meta.png"),
    ("latihan\\alliinase\\kode\\ambil_sekuens.py", "13_alliinase_seq.png"),
    
    # 5. Struktur Protein
    ("kode\\siapkan_data.py", "14_siapkan_data.png"),
    ("kode\\cari_struktur.py", "15_cari_struktur.png"),
    ("kode\\unduh_pdb.py", "16_unduh_pdb.png"),
]

for skrip, nama_png in daftar_perintah:
    subprocess.run(["python", "otomatis_ss.py", skrip, nama_png])