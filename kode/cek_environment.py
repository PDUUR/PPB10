import sys
import requests
import pandas as pd
import Bio

print("Python:", sys.version.split()[0])
print("Interpreter:", sys.executable)
print("requests:", requests.__version__)
print("pandas:", pd.__version__)
print("Biopython:", Bio.__version__)
print("Seluruh pustaka berhasil diimpor.")

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