if [ -d "fonts" ]; then rm -Rf fonts; fi
if [ -d "source/temp" ]; then rm -Rf source/temp; fi
mkdir "source/temp"
python3 source//fcp_ufo_process.py
gftools builder source/config.yaml