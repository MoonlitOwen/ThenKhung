#!/usr/bin/env python3

import glob
from pathlib import Path
import re
import shutil
import codecs
import ufoLib2
import yaml # pyyaml installed by gftools

SOURCE = Path("source/temp")

# Processing invalid UFO generation from Font Creator version 15.0.0.2974

for UFO in SOURCE.glob("*.ufo"):

	# Clearing BOM encoding in older versions of FCP. 
    for file in UFO.rglob("*.*"):
        try:
            with open(str(file), 'rb') as f:
                content = f.read()
            
            if content.startswith(codecs.BOM_UTF8):
                content = content[len(codecs.BOM_UTF8):]
                with open(file, 'wb') as f:
                    f.write(content)
            else:
                pass
        except Exception as e:
            print(f"An error occurred: {e}")



	# Older FCP does not add the encodingID properly
    fontInfo = UFO / "fontinfo.plist"

    plist = open(fontInfo, 'r')
    content = plist.read()
    content_new = re.sub(
		'<key>platformID</key>\\n\\s+<integer>3</integer>', 
		'<key>platformID</key><integer>3</integer><key>encodingID</key><integer>1</integer>', 
		content
	)
    plist.close()

    with open (fontInfo, 'w') as plistWriter:
        plistWriter.write (content_new)

	# Correcting invalid feature file data in older FCP output
    features = UFO / "features.fea"

    fea = open(features, 'r')
    content = fea.read()

    content_new = re.sub(
		r"@\\", 
		"@", 
		content
	)
    fea.close()

    with open (features, 'w') as feaWriter:
        feaWriter.write(content_new)

# ------------------------------------

VERSION = None

# read version from config.yaml
with open(SOURCE / ".." / "config.yaml") as f:
    config = yaml.safe_load(f)
    version_str = f"{config['version']:.3f}"
    version_minor, version_major = version_str.split(".")
    VERSION = (int(version_minor), int(version_major))

# ------------------------------------

    # Now that the UFO is normalized, we can modify it more easily with ufoLib2
    print ("Adding some name records")
    font = ufoLib2.Font.open(UFO)

    # Setting useTypoMetrics flag
    if 7 in font.info.openTypeOS2Selection:
        font.info.openTypeOS2Selection.remove(7)

    # Setting version number override
    print(f"Overriding version to {VERSION[0]}.{VERSION[1]:03d}")
    font.info.versionMajor = VERSION[0]
    font.info.versionMinor = VERSION[1]

    name_records = []

    for record in font.info.openTypeNameRecords:
        #FCP creates a NID 16 for the localized name, but not a NID1
        if record.get("nameID") == 16:
            new_record = {
                "nameID": 1,
                "platformID": record.get("platformID"),
                "encodingID": record.get("encodingID"),
                "languageID": record.get("languageID"),
                "string": record.get("string"),
            }
            name_records.append(new_record)
        elif record.get("nameID") == 17:
            pass
        else:
            name_records.append(record) 
    font.info.openTypeNameRecords = name_records

# ------------------------------------
# Add meta table
    print ("Adding meta table")

    metaTable = {
        "dlng": ["zh", "Hant", "zh-Hant", "nan", "hak", "yue", "nan-Latn", "nan-Latn-pehoeji", "nan-Latn-tailo", "Bopo", "Hanb"],
        "slng": ["zh", "Hans", "Hant", "zh-Hans", "zh-Hant", "nan", "hak", "yue", "Bopo", "Hanb", "zh-Latn", "zh-Latn-pinyin", "nan-Latn", "nan-Latn-pehoeji", "nan-Latn-tailo", "Latn", "Cyrl", "Grek"]
    }

    font.lib["public.openTypeMeta"] = metaTable

# ------------------------------------

    # Add the BASE table

    base_table_content = """
table BASE {
HorizAxis.BaseTagList   icfb    icft    ideo    romn;
HorizAxis.BaseScriptList  
    DFLT    ideo  	-97   857  -120     0,
    hani    ideo   	-97   857  -120     0,
    kana    ideo   	-97   857  -120     0,
    hang    ideo   	-97   857  -120     0,
    latn    romn   	-97   857  -120     0;

VertAxis.BaseTagList    icfb    icft    ideo    romn;
VertAxis.BaseScriptList
    DFLT    ideo    26   974     0   120,
    hani    ideo    26   974     0   120,
    kana    ideo    26   974     0   120,
    hang    ideo    26   974     0   120,
    latn    romn    26   974     0   120;
} BASE;
"""

    features = font.features.text if font.features.text else ""
    if "table BASE" in features:
        pass
    else:
        print("Adding BASE table to features.fea")
        features += f"\n\n{base_table_content}\n"
        font.features.text = features

    font.save(UFO,overwrite=True)