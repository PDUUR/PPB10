import json
from pathlib import Path
import requests

ENDPOINT = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PARAMETER = {
    "db": "protein",
    "term": (
        "txid4682[Organism:exp] AND "
        "chitinase[Title] NOT pdb[Filter]"
    ),
    "retmode": "json",
    "retmax": 500,
}
def main():
    try:
        respons = requests.get(ENDPOINT, params=PARAMETER, timeout=30)
        respons.raise_for_status()
        data = respons.json()
    except requests.exceptions.RequestException as galat:
        raise SystemExit(f"Permintaan API gagal: {galat}")
    except ValueError:
        raise SystemExit("Respons API bukan JSON yang dapat dibaca.")

    if "error" in data:
        raise SystemExit(f"NCBI melaporkan galat: {data['error']}")

    hasil = data.get("esearchresult", {})
    if "ERROR" in hasil or hasil.get("errorlist"):
        try:
            raise SystemExit(f"Pencarian bermasalah: {hasil}")
        except (KeyError, TypeError, ValueError):
            raise SystemExit("Struktur respons ESearch tidak sesuai harapan.")

    jumlah = int(hasil["count"])
    daftar_id = hasil["idlist"]

    folder_data = Path(__file__).resolve().parent.parent / "data"
    folder_data.mkdir(exist_ok=True)
    berkas = folder_data / "hasil_esearch.json"
    with berkas.open("w", encoding="utf-8") as keluaran:
        json.dump(data, keluaran, ensure_ascii=False, indent=2)

    print("Basis data:", PARAMETER["db"])
    print("Jumlah hasil pencarian:", jumlah)
    print("Jumlah ID yang diterima:", len(daftar_id))
    print("Daftar ID:")
    for nomor, identitas in enumerate(daftar_id, start=1):
        print(f"{nomor}. {identitas}")
    print("Respons tersimpan: data/hasil_esearch.json")

    if not daftar_id:
        print("Tidak ada rekaman yang sesuai dengan pencarian.")
    if jumlah > len(daftar_id):
        print("Sebagian ID belum diambil karena batas retmax.")

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