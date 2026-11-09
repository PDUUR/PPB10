import csv
import json
import re
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "wu2021"
NS = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def baca_xlsx(path):
    with ZipFile(path) as arsip:
        strings = []
        if "xl/sharedStrings.xml" in arsip.namelist():
            root = ET.fromstring(arsip.read("xl/sharedStrings.xml"))
            strings = ["".join(t.itertext()) for t in root.findall("s:si", NS)]
        root = ET.fromstring(arsip.read("xl/worksheets/sheet1.xml"))
        rows = []
        for row in root.findall(".//s:row", NS):
            values = {}
            for cell in row:
                col = re.sub(r"\d", "", cell.attrib["r"])
                value = cell.find("s:v", NS)
                text = value.text if value is not None else "".join(cell.itertext())
                if cell.get("t") == "s":
                    text = strings[int(text)]
                values[col] = text
            rows.append(values)
        return rows[1:]


def simpan_csv(path, rows, columns):
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def main():
    anotasi = {r["A"]: r for r in baca_xlsx(DATA / "Table_2.XLSX")}
    protein = baca_xlsx(DATA / "Table_7.XLSX")
    dipilih = [r for r in protein if r.get("K") in {"up", "down"}]
    pemetaan, kelompok_terpetakan = [], set()
    for row in dipilih:
        for protein_id in row["A"].split(";"):
            gene_id = re.sub(r"\.p\d+$", "", protein_id)
            swiss = anotasi.get(gene_id, {}).get("E", "-")
            if swiss in {"", "-"}:
                continue
            fields = swiss.split("|", 3)
            if len(fields) != 4 or not fields[0]:
                raise ValueError(f"Anotasi Swiss-Prot tidak sesuai: {gene_id}")
            deskripsi = fields[3]
            spesies = re.search(r"OS=(.*?)(?= GN=| PE=| SV=|$)", deskripsi)
            if not spesies:
                raise ValueError(f"Organisme referensi tidak terbaca: {gene_id}")
            pemetaan.append({
                "kelompok_protein": row["A"],
                "id_penelitian": gene_id,
                "arah_perubahan": row["K"],
                "uniprot_referensi": fields[0],
                "nama_protein_referensi": deskripsi.split(" OS=", 1)[0],
                "organisme_referensi": spesies.group(1),
            })
            kelompok_terpetakan.add(row["A"])

    referensi = []
    for accession in sorted({r["uniprot_referensi"] for r in pemetaan}):
        members = [r for r in pemetaan if r["uniprot_referensi"] == accession]
        referensi.append({
            "uniprot_referensi": accession,
            "nama_protein_referensi": members[0]["nama_protein_referensi"],
            "organisme_referensi": members[0]["organisme_referensi"],
            "id_penelitian": ";".join(sorted({r["id_penelitian"] for r in members})),
        })
    simpan_csv(DATA / "pemetaan_protein.csv", pemetaan, list(pemetaan[0]))
    simpan_csv(DATA / "daftar_referensi_protein.csv", referensi, list(referensi[0]))
    ringkasan = {
        "doi": "10.3389/fnut.2021.764133",
        "aturan_pemilihan": "Label Significant pada Table 7 adalah up atau down",
        "label_table7": dict(Counter(r.get("K", "") for r in protein)),
        "kelompok_dipilih": len(dipilih),
        "kelompok_dengan_anotasi_swissprot": len(kelompok_terpetakan),
        "baris_pemetaan": len(pemetaan),
        "nomor_akses_referensi_unik": len(referensi),
        "catatan": "Artikel melaporkan 162 up dan 26 down; tabel memuat 163 up dan 26 down. "
        "Nomor akses referensi bukan bukti identitas sekuens protein sampel.",
    }
    (DATA / "ringkasan_persiapan.json").write_text(
        json.dumps(ringkasan, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("Daftar nomor akses UniProt referensi siap.")
    print("Jumlah nomor akses unik:", len(referensi))
    print("Daftar pencarian: data/wu2021/daftar_referensi_protein.csv")
    print("Catatan pemetaan: data/wu2021/pemetaan_protein.csv")
    print("Ringkasan sumber: data/wu2021/ringkasan_persiapan.json")


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