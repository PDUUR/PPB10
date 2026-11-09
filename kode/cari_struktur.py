import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

ENDPOINT = "https://search.rcsb.org/rcsbsearch/v2/query"
ROOT = Path(__file__).resolve().parent.parent


def main():
    berkas = ROOT / "data" / "wu2021" / "daftar_referensi_protein.csv"
    tabel = pd.read_csv(berkas, dtype=str, keep_default_na=False)
    daftar_akses = sorted(set(tabel["uniprot_referensi"].str.strip()))
    if not daftar_akses or "" in daftar_akses:
        raise SystemExit("Daftar nomor akses kosong atau tidak lengkap.")

    kueri = {
        "query": {
            "type": "terminal",
            "service": "text",
            "parameters": {
                "attribute": (
                    "rcsb_polymer_entity_container_identifiers."
                    "reference_sequence_identifiers."
                    "database_accession"
                ),
                "operator": "in",
                "value": daftar_akses,
            },
        },
        "return_type": "entry",
        "request_options": {
            "results_content_type": ["experimental", "computational"],
            "paginate": {"start": 0, "rows": 1000},
            "sort": [{"sort_by": "rcsb_id", "direction": "asc"}],
        },
    }

    # Mengirim permintaan dan memeriksa respons.
    try:
        respons = requests.post(ENDPOINT, json=kueri, timeout=30)
        respons.raise_for_status()
        if respons.status_code == 204:
            data = {"result_type": "entry", "total_count": 0, "result_set": []}
        else:
            data = respons.json()
        if data["result_type"] != "entry":
            raise ValueError("Jenis hasil bukan rekaman struktur.")
        jumlah = int(data["total_count"])
        daftar_id = [item["identifier"] for item in data.get("result_set", [])]
        if any(not isinstance(item, str) or not item for item in daftar_id):
            raise ValueError("ID struktur kosong atau tidak sesuai.")
        if len(daftar_id) != len(set(daftar_id)):
            raise ValueError("ID struktur berulang.")
        if jumlah != len(daftar_id):
            raise ValueError("Hasil belum lengkap; periksa rows dan paginate.")
    except requests.exceptions.RequestException as galat:
        raise SystemExit(f"Permintaan API gagal: {galat}")
    except (ValueError, KeyError, TypeError) as galat:
        raise SystemExit(f"Respons tidak dapat digunakan: {galat}")

    # Menyimpan respons dan catatan pencarian.
    folder = ROOT / "data" / "wu2021"
    with (folder / "hasil_pencarian_struktur.json").open(
        "w", encoding="utf-8"
    ) as keluaran:
        json.dump(data, keluaran, ensure_ascii=False, indent=2)
    catatan = {
        "waktu_utc": datetime.now(timezone.utc).isoformat(),
        "sumber_doi": "10.3389/fnut.2021.764133",
        "berkas_masukan": "data/wu2021/daftar_referensi_protein.csv",
        "endpoint": ENDPOINT,
        "kueri": kueri,
        "jumlah_nomor_akses_referensi": len(daftar_akses),
        "jumlah_entri_struktur": jumlah,
    }
    with (folder / "catatan_pencarian.json").open(
        "w", encoding="utf-8"
    ) as keluaran:
        json.dump(catatan, keluaran, ensure_ascii=False, indent=2)

    eksperimen = sum(
        len(kode) == 4 or kode.startswith("pdb_") for kode in daftar_id
    )
    alphafold = sum(kode.startswith("AF_") for kode in daftar_id)
    lainnya = jumlah - eksperimen - alphafold
    print("Nomor akses UniProt referensi yang dicari:", len(daftar_akses))
    print("Struktur eksperimen di RCSB PDB:", eksperimen)
    print("Model prediksi AlphaFold:", alphafold)
    if lainnya:
        print("Rekaman jenis lainnya:", lainnya)
    print("Total rekaman struktur/model:", jumlah)
    print("Contoh ID struktur:", ", ".join(daftar_id[:5]) or "tidak ada")
    print("Daftar ID: data/wu2021/hasil_pencarian_struktur.json")
    print("Catatan kueri: data/wu2021/catatan_pencarian.json")


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