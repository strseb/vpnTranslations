#! /usr/bin/env python3
# Note: this wont work on python 2.7
# This script must be executed at the root of the repository.

import xml.etree.ElementTree as ET
import os
import shutil
import html
from xml.sax import saxutils as su

ET.register_namespace('', 'urn:oasis:names:tc:xliff:document:1.2')
ET.register_namespace('qt', 'urn:trolltech:names:ts:document:1.0')

VPN_PROJECT_DIR = 'vpn'
OUT_PROJECT_DIR = 'translationFiles'

#LCONVERT = '/usr/lib/qt5/bin/lconvert'
LCONVERT = 'lconvert'

# Make sure the Target ts files are up to date
srcFile = os.path.join(VPN_PROJECT_DIR, 'src', 'src.pro')
os.system(f'lupdate {srcFile} -ts')

for fileName in os.listdir(os.path.join(VPN_PROJECT_DIR, 'translations')):
    if (not fileName.endswith('.ts')):
        continue
    filePath = os.path.join(VPN_PROJECT_DIR, 'translations', fileName)
    # Usual filename: mozillavpn_zh-cn.ts
    locale = fileName.split('_')[1].split('.')[0] # de, zh-cn, etc.
    baseName = fileName.split('_')[0] # mozillavpn
    outPath = os.path.join(OUT_PROJECT_DIR, locale)
    # Create folder for each locale and convert
    # ts file to /{locale}/mozillavpn.xliff
    print(f'Checking {locale}')
    if not os.path.exists(outPath):
        os.mkdir(outPath)

    outFile = os.path.join(outPath, f'{baseName}.xliff')
    if not os.path.exists(outFile):
        # If the file doesn't exist
        print(f'Creating {outFile}')
        os.system(f'{LCONVERT} -i {filePath} -o {outFile}')
    else:
        # Keep current translations
        print(f'Updating {outFile}')
        os.system(f'{LCONVERT} -i {filePath} -i {outFile} -o {outFile}')

    # Now clean up the new xliff file
    tree = ET.parse(outFile)
    root = tree.getroot()

    # Iterate all targetElements and remove empty ones
    for element in root.iter('{urn:oasis:names:tc:xliff:document:1.2}trans-unit'):
        target = element.find('{urn:oasis:names:tc:xliff:document:1.2}target')
        if (not target.text):
            element.remove(target)

#    # Unescape any html in text
#    for element in root.iter('{urn:oasis:names:tc:xliff:document:1.2}source'):
#        t = element.text
#        element.clear()
#        element.tail = su.unescape(t)
#        #print(f'Unescaped : {element.text}')

    # Iterate all targetElements and remove empty ones
    for element in root.iter('{urn:oasis:names:tc:xliff:document:1.2}extracomment'):
        element.tag = 'note'
    tree.write(outFile)