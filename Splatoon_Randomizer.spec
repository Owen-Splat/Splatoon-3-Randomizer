# -*- mode: python ; coding: utf-8 -*-


block_cipher = None

with open("./version.txt") as f:
    randomizer_version = f.read().strip()

added_files = [
    ( 'Data', 'Data' ),
    ( 'Resources', 'Resources' ),
    ( 'version.txt', '.')
]
a = Analysis(
    ['randomizer.py'],
    pathex=[],
    binaries=[],
    datas = added_files,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Splatoon3_Randomizer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='Resources/icon.ico',
)

app = BUNDLE(
    exe,
    name='Splatoon3_Randomizer.app',
    icon='Resources/icon.icns',
    bundle_identifier=None,
    info_plist={
        'LSBackgroundOnly': False,
        'CFBundleDisplayName': 'Splatoon3_Randomizer',
        'CFBundleName': 'Splat3_Rando', # 15 character maximum
        'CFBundleShortVersionString': randomizer_version,
    }
)