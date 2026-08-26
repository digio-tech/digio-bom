#!/usr/bin/env python3
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POM = ROOT / "pom.xml"
README = ROOT / "README.md"
NS = "{http://maven.apache.org/POM/4.0.0}"
NAME_COL = 80

tree = ET.parse(POM)
root = tree.getroot()

version_el = root.find(f"{NS}version")
if version_el is None or not version_el.text:
    sys.exit("Could not read <version> from pom.xml")
version = version_el.text.strip()

deps = []
for dep in root.iter(f"{NS}dependency"):
    g = dep.findtext(f"{NS}groupId", "").strip()
    a = dep.findtext(f"{NS}artifactId", "").strip()
    v = dep.findtext(f"{NS}version", "").strip()
    if g and a and v:
        deps.append((g, a, v))

lines = []
for g, a, v in deps:
    name = f"{g}:{a}"
    pad = max(1, NAME_COL - len(name))
    lines.append(f"    {name}{' ' * pad}{v}")
dep_block = "\n".join(lines)

content = README.read_text()
content = re.sub(r"^Bom version - .*$", f"Bom version - {version}", content, count=1, flags=re.M)

fenced = re.compile(r"(```\n)(.*?)(\n```)", re.DOTALL)
if not fenced.search(content):
    sys.exit("Could not find fenced ``` block in README.md")
content = fenced.sub(lambda m: f"{m.group(1)}{dep_block}{m.group(3)}", content, count=1)

README.write_text(content)
print(f"README.md updated: Bom version - {version}, {len(deps)} dependencies")
