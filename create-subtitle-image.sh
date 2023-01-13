DEFAULT_SVG=/Applications/Inkscape.app/Contents/Resources/share/inkscape/templates/default.svg
INKSCAPE_PYTHON=/Applications/Inkscape.app/Contents/Resources/bin/python3
SIMPINKSCR_SCRIPT=~/Library/Application\ Support/org.inkscape.Inkscape/config/inkscape/extensions/SimpInkScr/simpinkscr/simple_inkscape_scripting.py
export DYLD_LIBRARY_PATH=/Applications/Inkscape.app/Contents/Resources/lib
export PYTHONPATH=/Applications/Inkscape.app/Contents/Frameworks/Python.framework/Versions/3.10/lib/python3.10/site-packages:/Applications/Inkscape.app/Contents/Resources/share/inkscape/extensions:.

${INKSCAPE_PYTHON} "${SIMPINKSCR_SCRIPT}" --py-source "./create-subtitle-image.py" "${DEFAULT_SVG}" -- "$@"
