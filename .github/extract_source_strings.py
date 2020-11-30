#! /usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# This script must be executed at the root of the repository.

from lxml import etree, objectify
from translate.misc.xml_helpers import reindent
import os

VPN_PROJECT_DIR = "vpn"
OUT_PROJECT_DIR = "translationFiles"

srcFile = os.path.join(VPN_PROJECT_DIR, "src", "src.pro")
os.system(f"lupdate {srcFile} -ts")

filePath = os.path.join(VPN_PROJECT_DIR, "translations", "mozillavpn_en.ts")
outFile = os.path.join(OUT_PROJECT_DIR, "en", "mozillavpn.xliff")

# Update English XLIFF file
print(f"Updating {outFile}")
os.system(f"lconvert -if ts -i {filePath} -of xlf -o {outFile}")

# Clean up the new XLIFF file
NS = {"x": "urn:oasis:names:tc:xliff:document:1.2"}
tree = etree.parse(outFile)
root = tree.getroot()
objectify.deannotate(root, cleanup_namespaces=True)

# Remove empty targets
for target in root.xpath("//x:target", namespaces=NS):
    if target is not None:
        target.getparent().remove(target)

# Change QT <extracomment> elements into <notes>
for extracomment in root.xpath("//x:extracomment", namespaces=NS):
    extracomment.tag = "note"

# Remove all <context-group> elements
for context_group in root.xpath("//x:context-group", namespaces=NS):
    context_group.getparent().remove(context_group)

# Replace the existing locale file with the new XML content
with open(outFile, "w") as fp:
    # Fix identation of XML file
    reindent(root)
    xliff_content = etree.tostring(
        tree, encoding="UTF-8", xml_declaration=True, pretty_print=True
    )
    fp.write(xliff_content.decode("utf-8"))
