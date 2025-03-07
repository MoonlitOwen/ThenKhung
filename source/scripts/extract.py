import glob
import zipfile
from pathlib import Path

SOURCE = Path("source")
OUTPUT = SOURCE/"temp"

for ufoz in SOURCE.glob("*.ufoz"):
    print ("Extracting...")
    with zipfile.ZipFile(ufoz, 'r') as zip_ref:
        zip_ref.extractall(OUTPUT)