from io import StringIO
from pathlib import Path

import pandas as pd
import requests
from Bio import SeqIO

ENDPOINT = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
FOLDER_UTAMA = Path(__file__).resolve().parent.parent
FOLDER_DATA = FOLDER_UTAMA / "data"
FOLDER_SEKUENS = FOLDER_DATA / "sekuens"
FOLDER_HASIL = FOLDER_UTAMA / "hasil"

def periksa_sekuens(rekaman, metadata):
    daftar_aksesi = metadata["nomor_aksesi"].tolist()
    sekuens_per_aksesi = {}
    for item in rekaman:
        cocok = [bagian for bagian in item.id.split("/") if bagian in daftar_aksesi]
        if len(cocok) == 1:
            item.description = item.description.replace(item.id, cocok[0], 1)
            item.id = cocok[0]
        sekuens_per_aksesi[item.id] = item

    if len(rekaman) != len(sekuens_per_aksesi):
        raise ValueError("Respons FASTA memuat nomor aksesi berulang.")
    if set(sekuens_per_aksesi) != set(daftar_aksesi):
        raise ValueError("Nomor aksesi FASTA tidak sesuai dengan metadata.")

    pemeriksaan = []
    urutan_rekaman = []
    for baris in metadata.itertuples(index=False):
        item = sekuens_per_aksesi[baris.nomor_aksesi]
        panjang = len(item.seq)
        if panjang == 0 or panjang != baris.panjang_aa:
            raise ValueError(f"Panjang sekuens {item.id} tidak sesuai metadata.")
        pemeriksaan.append({
            "nomor_aksesi": item.id,
            "panjang_metadata": baris.panjang_aa,
            "panjang_fasta": panjang,
            "status": "sesuai",
        })
        urutan_rekaman.append(item)

    return urutan_rekaman, pd.DataFrame(pemeriksaan)

def main():
    try:
        metadata = pd.read_csv(FOLDER_HASIL / "metadata_protein.csv")
        metadata = metadata[["nomor_aksesi", "panjang_aa"]].copy()
        if metadata.empty or metadata.isna().any().any():
            raise ValueError("Metadata kosong atau mengandung nilai kosong.")
        if metadata["nomor_aksesi"].duplicated().any():
            raise ValueError("Nomor aksesi metadata berulang.")
        panjang = pd.to_numeric(metadata["panjang_aa"], errors="raise")
        if (panjang <= 0).any() or (panjang % 1 != 0).any():
            raise ValueError("Panjang protein harus berupa bilangan bulat positif.")
        metadata["panjang_aa"] = panjang.astype(int)
    except (OSError, ValueError, KeyError, TypeError) as galat:
        raise SystemExit(f"Periksa metadata atau jalankan ambil_metadata.py: {galat}")

    parameter = {
        "db": "protein",
        "id": ",".join(metadata["nomor_aksesi"]),
        "rettype": "fasta",
        "retmode": "text",
    }

    try:
        respons = requests.get(ENDPOINT, params=parameter, timeout=30)
        respons.raise_for_status()
        rekaman = list(SeqIO.parse(StringIO(respons.text), "fasta"))
        rekaman, pemeriksaan = periksa_sekuens(rekaman, metadata)
    except requests.exceptions.RequestException as galat:
        raise SystemExit(f"Permintaan API gagal: {galat}")
    except ValueError as galat:
        raise SystemExit(f"Sekuen belum disimpan: {galat}")

    FOLDER_SEKUENS.mkdir(parents=True, exist_ok=True)
    for item in rekaman:
        nama_fasta = FOLDER_SEKUENS / f"{item.id}.fasta"
        with nama_fasta.open("w", encoding="utf-8") as keluaran:
            SeqIO.write([item], keluaran, "fasta")
        print(f"Tersimpan: data/sekuens/{nama_fasta.name}")

    pemeriksaan.to_csv(FOLDER_HASIL / "pemeriksaan_sekuens.csv", index=False, encoding="utf-8")
    print("Jumlah berkas FASTA:", len(rekaman))
    print(pemeriksaan.to_string(index=False))
    print("Pemeriksaan tersimpan: hasil/pemeriksaan_sekuens.csv")

if __name__ == "__main__":
    main()
    
from datetime import datetime
from pathlib import Path

print()
print("Nama        : M Faturrahman Almukhlisin")
print("NIM         : G04012510425")
print("Kode        : BIFPB632")
print("Folder      : ", Path.cwd())
print("Waktu       : ", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
print(
    "Pernyataan Integritas Akademik: Saya menyatakan bahwa "
    "seluruh pekerjaan dan bukti eksekusi dalam tugas ini "
    "merupakan hasil pengerjaan saya sendiri. Saya tidak "
    "menggunakan tangkapan layar milik pihak lain dan tidak "
    "melakukan pemalsuan bukti eksekusi. Apabila terbukti "
    "melanggar pernyataan ini, saya bersedia menerima sanksi "
    "akademik berupa penganuliran nilai praktikum."
)