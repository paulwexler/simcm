# create README.md
#
# usage> bash make_readme.sh
#
# Start with readme.txt up to and including DESCRIPTION.
sed -n -e '1,/^### DESCRIPTION/p' readme.txt > README.md

# Replace @VERSION@ with the version extracted from simcm.py
VERSION=`grep __version__ simcm.py |cut -d"'" -f2`
sed -i -e "s/@VERSION@/$VERSION/" README.md

# Append the pydoc documentation between DESCRIPTION and CLASSES.
PAGER=`which cat` pydoc ./simcm.py \
    | sed -e 's/^    //' \
          -e '1,/^DESCRIPTION/d' \
          -e '/^CLASSES/,$d' \
    >> README.md

# Append readme.txt from EXAMPLE on.
sed -n -e '/^### EXAMPLE/,$p' readme.txt >> README.md

# Append CLASSES sub-title
echo '### CLASSES' >> README.md

# Append a code block start.
echo '```' >> README.md

# Append the class documentation up to but not including the Data descriptors.
PAGER=`which cat` pydoc ./simcm.py \
    | sed -e '1,/^CLASSES/d' \
          -e '/^ *|  Data /,/^ *class /{/^ *class /p;d}' \
    >> README.md

# Append a code block end.
echo '```' >> README.md
