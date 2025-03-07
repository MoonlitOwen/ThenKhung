if [ -d "fonts/" ]; then rm -rf "fonts"; fi
if [ -d "source/temp/" ]; then rm -rf "source/temp"; fi
mkdir "source/temp"
. venv/bin/activate; python3 source/scripts/extract.py
. venv/bin/activate; python3 source/fcp_ufo_process.py
gftools builder source/config.yaml
# fontbakery check-googlefonts fonts/ttf/UoqMunThenKhung-Regular.ttf -l WARN --ghmarkdown results.md