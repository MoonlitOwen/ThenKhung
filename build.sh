if [ -d "fonts/" ]; then rm -rf "fonts"; fi
if [ -d "source/temp/" ]; then rm -rf "source/temp"; fi
mkdir "source/temp"
python3 source/fcp_ufo_process.py
gftools builder source/config.yaml
# fontbakery check-googlefonts fonts/ttf/UoqMunThenKhung-Regular.ttf -l WARN --ghmarkdown results.md