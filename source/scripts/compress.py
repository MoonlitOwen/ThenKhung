import glob
from pathlib import Path
import ufoLib2

SOURCE = Path("source")

for file in SOURCE.glob("*.ufo"):
    print ("Compressing...")
    ufo = ufoLib2.Font.open(file)
    ufo.save(str(file)+"z",structure="zip",overwrite=True)