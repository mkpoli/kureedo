#!/usr/bin/env python3
"""Package the three built editions with notices, CSS and checksums."""
import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
FAMILIES = {
    'Kureedo Full': 'Japanese base with missing public code points from LXGW WenKai Light 1.530, matched to the Klee Regular base.',
    'Kureedo Kana': 'Available hiragana, katakana, halfwidth kana, punctuation and historical forms.',
    'Kureedo Additions': 'The 26 code points absent from unmodified Klee One. Use directly encoded characters; use Kana for hist/hlig and combining marks on ordinary kana.',
}


def package():
    out = ROOT / 'build/packages'
    out.mkdir(parents=True, exist_ok=True)
    manifest = []
    for family, description in FAMILIES.items():
        stem = family.replace(' ', '') + '-Regular'
        files = {stem + suffix: (ROOT/'fonts'/(stem+suffix)).read_bytes()
                 for suffix in ('.ttf', '.woff2')}
        with TTFont(ROOT/'fonts'/(stem+'.ttf')) as font:
            count = len(font.getBestCmap())
        files['OFL.txt'] = (ROOT/'OFL.txt').read_bytes()
        if family == 'Kureedo Full':
            files['OFL-WenKai.txt'] = (ROOT/'sources/wenkai/OFL.txt').read_bytes()
        files['font.css'] = (f'@font-face {{\n  font-family: "{family}";\n'
            f'  src: url("{stem}.woff2") format("woff2");\n'
            '  font-weight: 400;\n  font-style: normal;\n  font-display: swap;\n}\n').encode()
        files['README.txt'] = (f'{family}\n\n{description}\n{count:,} encoded characters.\n\n'
            f'Install {stem}.ttf for desktop use. For web use, keep font.css and\n'
            f'{stem}.woff2 together, load font.css, and select "{family}".\n'
            'Kana and Additions need a fallback font for other characters.\n'
            'These are development packages built from source, with distinct family names.\n'
            'See OFL.txt and, for Full, OFL-WenKai.txt for license notices.\n').encode()
        files['SHA256SUMS.txt'] = ''.join(f'{hashlib.sha256(data).hexdigest()}  {name}\n'
                                         for name, data in sorted(files.items())).encode()
        archive = out/(stem+'.zip')
        with ZipFile(archive, 'w') as z:
            for name, data in sorted(files.items()):
                info = ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
                info.compress_type = ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                z.writestr(info, data)
        manifest.append({'family':family,'characters':count,'archive':archive.name,
                         'ttf_bytes':len(files[stem+'.ttf']),
                         'woff2_bytes':len(files[stem+'.woff2']),
                         'sha256':hashlib.sha256(archive.read_bytes()).hexdigest()})
        print(f'Packaged {archive.name}: {count:,} characters')
    (out/'editions.json').write_text(json.dumps(manifest,indent=2)+'\n')


if __name__ == '__main__':
    package()
