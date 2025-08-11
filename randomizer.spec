# -*- mode: python ; coding: utf-8 -*-

with open("./version.txt") as f:
    randomizer_version = f.read().strip()

a = Analysis(
    ['randomizer.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('RandomizerCore/Data/parameters.yml', 'RandomizerCore/Data'),
        ('RandomizerUI/Resources/adjectives.txt', 'RandomizerUI/Resources'),
        ('RandomizerUI/Resources/changelog.txt', 'RandomizerUI/Resources'),
        ('RandomizerUI/Resources/characters.txt', 'RandomizerUI/Resources'),
        ('RandomizerUI/Resources/icon.icns', 'RandomizerUI/Resources'),
        ('RandomizerUI/Resources/icon.ico', 'RandomizerUI/Resources'),
        ('version.txt', '.')
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None
)
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    name='Splatoon 3 Randomizer',
    debug=False,
    strip=False,
    upx=True,
    runtime_tmpdir=None,
    console=False,
    icon="RandomizerUI/Resources/icon.ico"
)

app = BUNDLE(exe,
    name='Splatoon 3 Randomizer.app',
    icon="RandomizerUI/Resources/icon.icns",
    bundle_identifier=None,
    info_plist={
        "LSBackgroundOnly": False,
        "CFBundleDisplayName": "Splatoon 3 Randomizer",
        "CFBundleName": "S3 Randomizer",
        "CFBundleShortVersionString": randomizer_version
    })