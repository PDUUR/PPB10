import json
from pathlib import Path

import pandas as pd
import requests

ENDPOINT = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
FOLDER_UTAMA = Path(__file__).resolve().parent.parent
FOLDER_DATA = FOLDER_UTAMA / "data"
FOLDER_HASIL = FOLDER_UTAMA / "hasil"

def main():
    berkas_id = FOLDER_DATA / "hasil_esearch.json"
    try:
        with berkas_id.open(encoding="utf-8") as masukan:
            pencarian = json.load(masukan)
            daftar_id = pencarian["esearchresult"]["idlist"]
    except (OSError, ValueError, KeyError, TypeError):
        raise SystemExit(
            "Hasil ESearch belum tersedia atau tidak sesuai. "
            "Jalankan cari_protein.py terlebih dahulu."
        )
    if not isinstance(daftar_id, list) or not daftar_id:
        raise SystemExit("Daftar ID kosong atau tidak sesuai. Periksa hasil ESearch.")
    if not all(isinstance(uid, str) and uid.isdigit() for uid in daftar_id):
        raise SystemExit("Daftar ID harus berisi ID numerik dari ESearch.")
    parameter = {
        "db": "protein",
        "id": ",".join(daftar_id),
        "retmode": "json",
    }
    try:
        respons = requests.get(ENDPOINT, params=parameter, timeout=30)
        respons.raise_for_status()
        data = respons.json()
    except requests.exceptions.RequestException as galat:
        raise SystemExit(f"Permintaan API gagal: {galat}")
    except ValueError:
        raise SystemExit("Respons API bukan JSON yang dapat dibaca.")

    hasil = data.get("result", {})
    if "error" in data or set(hasil.get("uids", ())) != set(daftar_id):
        raise SystemExit("Metadata yang diterima tidak mencakup seluruh ID.")
    daftar_metadata = []
    for uid in daftar_id:
        try:
            rekaman = hasil[uid]
            daftar_metadata.append({
                "id_ncbi": uid,
                "nomor_aksesi": rekaman["accessionversion"],
                "nama_protein": rekaman["title"],
                "organisme": rekaman["organism"],
                "panjang_aa": int(rekaman["slen"]),
            })
        except (KeyError, TypeError, ValueError):
            raise SystemExit(f"Metadata untuk ID {uid} tidak lengkap.")

    df = pd.DataFrame(daftar_metadata)
    FOLDER_DATA.mkdir(exist_ok=True)
    FOLDER_HASIL.mkdir(exist_ok=True)

    with (FOLDER_DATA / "hasil_esummary.json").open("w", encoding="utf-8") as keluaran:
        json.dump(data, keluaran, ensure_ascii=False, indent=2)

    df.to_csv(FOLDER_HASIL / "metadata_protein.csv", index=False, encoding="utf-8")

    print("Jumlah metadata:", len(df))
    kolom_tampilan = ["nomor_aksesi", "organisme", "panjang_aa"]
    print(df[kolom_tampilan].to_string(index=False))
    print("Respons tersimpan: data/hasil_esummary.json")
    print("Tabel tersimpan: hasil/metadata_protein.csv")

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