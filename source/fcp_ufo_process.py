#!/usr/bin/env python3

import glob
from pathlib import Path
import re
import shutil
import codecs
import ufoLib2

SOURCE = Path("source/")

# Processing invalid UFO generation from Font Creator version 15.0.0.2974

for source in SOURCE.glob("*.ufo"):
    UFO = Path(shutil.copytree(str(source),str(source).replace("source/","source/temp/"),dirs_exist_ok=True))

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
		'<key>platformID</key>\\n\\s+<integer>3</integer>\\n\\s+<key>encodingID</key>\\n\\s+<integer>.*</integer>', 
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

    # Now on to modify the UFO some

    font = ufoLib2.Font.open(UFO)
    print ("Removing NID16/17 from UFO source") #This is added by FCP incorrectly. 
    name_records = font.info.openTypeNameRecords
    updated_name_records = [
        record for record in name_records if record.get("nameID") not in [16, 17]
    ]
    font.info.openTypeNameRecords = updated_name_records

    base_table_content = """
table BASE {
HorizAxis.BaseTagList   icfb    icft    ideo    romn;
HorizAxis.BaseScriptList  
    DFLT    ideo  	-97   851  -123     0,
    hani    ideo   	-97   851  -123     0,
    kana    ideo   	-97   851  -123     0,
    hang    ideo   	-97   851  -123     0,
    latn    romn   	-97   851  -123     0;

VertAxis.BaseTagList    icfb    icft    ideo    romn;
VertAxis.BaseScriptList
    DFLT    ideo    26   974     0   123,
    hani    ideo    26   974     0   123,
    kana    ideo    26   974     0   123,
    hang    ideo    26   974     0   123,
    latn    romn    26   974     0   123;
} BASE;
"""

    features = font.features.text if font.features.text else ""
    if "table BASE" in features:
        pass
    else:
        print("Adding BASE table to features.fea.")
        features += f"\n\n{base_table_content}\n"
        font.features.text = features

    font.save(UFO,overwrite=True)