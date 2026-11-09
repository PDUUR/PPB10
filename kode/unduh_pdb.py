import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "wu2021"
FOLDER_PDB = DATA / "struktur_pdb"
LAPORAN = ROOT / "hasil" / "laporan_unduhan_pdb.csv"


def url_pdb(identitas, sesi):
    if re.fullmatch(r"[0-9][A-Za-z0-9]{3}", identitas):
        return "eksperimen", "RCSB PDB", (
            f"https://files.rcsb.org/download/{identitas}.pdb"
        )
    cocok = re.fullmatch(r"AF_AF([A-Z0-9]+)F([0-9]+)", identitas)
    if cocok:
        akses, fragmen = cocok.groups()
        respons = sesi.get(
            f"https://alphafold.ebi.ac.uk/api/prediction/{akses}",
            timeout=30,
        )
        respons.raise_for_status()
        for model in respons.json():
            if model.get("entryId") == f"AF-{akses}-F{fragmen}":
                url = model.get("pdbUrl")
                if url:
                    return "prediksi", "AlphaFold DB", url
        raise ValueError("Model atau tautan PDB tidak tersedia di AlphaFold DB.")
    raise ValueError("Jenis ID belum didukung program unduhan ini.")


def memuat_atom(teks):
    return any(
        baris.startswith(("ATOM  ", "HETATM"))
        for baris in teks.splitlines()
    )


def main():
    berkas = DATA / "hasil_pencarian_struktur.json"
    with berkas.open(encoding="utf-8") as sumber:
        hasil = json.load(sumber)
    daftar_id = sorted({r["identifier"] for r in hasil["result_set"]})
    if len(daftar_id) != int(hasil["total_count"]):
        raise SystemExit("Daftar ID belum lengkap; jalankan pencarian kembali.")
    if any(not re.fullmatch(r"[A-Za-z0-9_]+", r) for r in daftar_id):
        raise SystemExit("ID struktur tidak sesuai.")

    FOLDER_PDB.mkdir(parents=True, exist_ok=True)
    LAPORAN.parent.mkdir(parents=True, exist_ok=True)
    sebelumnya = {}
    if LAPORAN.exists():
        with LAPORAN.open(encoding="utf-8-sig", newline="") as sumber:
            sebelumnya = {r["id_struktur"]: r for r in csv.DictReader(sumber)}

    kolom = [
        "id_struktur", "jenis_struktur", "sumber", "url",
        "nama_berkas", "status", "keterangan", "waktu_utc",
    ]
    berhasil = gagal = 0
    tersedia_eksperimen = tersedia_alphafold = 0
    jumlah_eksperimen = sum(
        re.fullmatch(r"[0-9][A-Za-z0-9]{3}", kode) is not None
        for kode in daftar_id
    )
    jumlah_alphafold = sum(kode.startswith("AF_") for kode in daftar_id)
    print("Jumlah ID yang diproses:", len(daftar_id), flush=True)
    print("Struktur eksperimen yang diproses:", jumlah_eksperimen, flush=True)
    print("Model AlphaFold yang diproses:", jumlah_alphafold, flush=True)

    with requests.Session() as sesi, LAPORAN.open(
        "w", encoding="utf-8-sig", newline=""
    ) as keluaran:
        penulis = csv.DictWriter(keluaran, fieldnames=kolom)
        penulis.writeheader()
        for nomor, identitas in enumerate(daftar_id, 1):
            tujuan = FOLDER_PDB / f"{identitas}.pdb"
            catatan = dict.fromkeys(kolom, "")
            catatan.update(id_struktur=identitas, nama_berkas=tujuan.name)
            try:
                if tujuan.exists() and memuat_atom(tujuan.read_text(errors="replace")):
                    lama = sebelumnya.get(identitas, {})
                    for k in ("jenis_struktur", "sumber", "url"):
                        catatan[k] = lama.get(k, "")
                    catatan["status"] = "sudah_ada"
                else:
                    jenis, sumber, url = url_pdb(identitas, sesi)
                    catatan.update(jenis_struktur=jenis, sumber=sumber, url=url)
                    respons = sesi.get(url, timeout=45)
                    respons.raise_for_status()
                    if not memuat_atom(respons.text):
                        raise ValueError("Respons tidak memuat koordinat atom PDB.")
                    sementara = tujuan.with_suffix(".pdb.part")
                    sementara.write_bytes(respons.content)
                    sementara.replace(tujuan)
                    catatan["status"] = "berhasil"
                berhasil += 1
                if re.fullmatch(r"[0-9][A-Za-z0-9]{3}", identitas):
                    tersedia_eksperimen += 1
                elif identitas.startswith("AF_"):
                    tersedia_alphafold += 1
            except (requests.RequestException, ValueError, OSError) as galat:
                status = "gagal"
                if (
                    isinstance(galat, requests.HTTPError)
                    and galat.response is not None
                    and galat.response.status_code == 404
                ):
                    status = "tidak_tersedia"
                catatan.update(status=status, keterangan=str(galat))
                gagal += 1
            catatan["waktu_utc"] = datetime.now(timezone.utc).isoformat()
            penulis.writerow(catatan)
            keluaran.flush()
            if nomor % 25 == 0 or nomor == len(daftar_id):
                print(f"Diproses: {nomor}/{len(daftar_id)}", flush=True)

    print("Struktur eksperimen tersedia (.pdb):", tersedia_eksperimen)
    print("Model AlphaFold tersedia (.pdb):", tersedia_alphafold)
    print("Total berkas PDB tersedia:", berhasil)
    print("Tidak tersedia atau gagal:", gagal)
    print("Folder: data/wu2021/struktur_pdb")
    print("Laporan: hasil/laporan_unduhan_pdb.csv")
    if gagal:
        print("Periksa status dan keterangan pada laporan unduhan.")


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