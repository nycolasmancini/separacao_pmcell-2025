#!/usr/bin/env python3
"""Test the updated items pattern"""
import re

# Original text from the PDF
text = """03185 / FO-01 --> FONE PMCELL / UN / 30 / 4,50 / 135,00
03186 / FO-02 --> FONE PMCELL / UN / 30 / 4,50 / 135,00
03187 / FO-03 --> FONE PMCELL / UN / 30 / 4,50 / 135,00
03188 / FO-04 --> FONE PMCELL / UN / 30 / 4,50 / 135,00
00010 / FO11 --> FONE PMCELL / UN / 100 / 2,80 / 280,00
00005 / FO15 --> FONE PMCELL STEREO / UN / 30 / 7,50 / 225,00
00041 / FO16 --> FONE PMCELL REVESTIDO / UN / 30 / 7,50 / 225,00
01929 / FO19 --> FONE PMCELL FO19 / UN / 50 / 3,00 / 150,00
00039 / FO12 --> FONE PMCELL STEREO / UN / 30 / 6,50 / 195,00
00040 / FO13 --> FONE PMCELL STEREO / UN / 30 / 6,50 / 195,00"""

# Updated pattern
pattern = r'(\d{5})\s*/\s*([^/\n]+)\s*-->\s*([^/\n]+)\s*/\s*UN\s*/\s*(\d+)\s*/\s*([\d,\.]+)\s*/\s*([\d,\.]+)'

print("Testing updated items pattern:")
print("Pattern:", pattern)
print("\nMatches found:")

matches = re.findall(pattern, text)
for i, match in enumerate(matches):
    print(f"Item {i+1}:")
    print(f"  Code: {match[0]}")
    print(f"  Reference: {match[1].strip()}")
    print(f"  Name: {match[2].strip()}")
    print(f"  Quantity: {match[3]}")
    print(f"  Unit Price: {match[4]}")
    print(f"  Total: {match[5]}")
    print()

print(f"Total items found: {len(matches)}")