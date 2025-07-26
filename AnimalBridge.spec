# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['game_core.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        ('final_animal_blocks.json', '.'),
        ('ranking.json', '.'),  # <-- 이 항목이 있는지 확인!
    ],  # 이렇게 수정해주세요!
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AnimalBridge',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # <-- False를 True로 수정!
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AnimalBridge',
)
