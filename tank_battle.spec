# -*- mode: python ; coding: utf-8 -*-
"""
Tank Battle — PyInstaller build specification.
Bundles main.py + src package + assets + maps + icon into a single executable.
"""

import sys
from pathlib import Path

project_root = Path(SPECPATH)

# ---------------------------------------------------------------------------
# Datas: (source, destination_inside_bundle)
# ---------------------------------------------------------------------------
datas = [
    # Assets: images, sounds, fonts
    (str(project_root / "assets"), "assets"),
    # Maps
    (str(project_root / "maps"), "maps"),
]

# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------
a = Analysis(
    [str(project_root / "main.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=[
        "pygame",
        "pygame.mixer",
        "pygame.font",
        "pygame.image",
        "pygame.transform",
        "pygame.draw",
        "pygame.event",
        "pygame.time",
        "pygame.display",
        "pygame.key",
        "pygame.mouse",
        "pygame.rect",
        "pygame.surface",
        "pygame.sprite",
        "pygame.math",
        "pygame.locals",
        "pygame._sdl2",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[str(project_root / "hook_set_cwd.py")],
    excludes=[
        "tkinter",
        "matplotlib",
        "numpy",
        "scipy",
        "PIL",
        "IPython",
        "jupyter",
    ],
    noarchive=False,
    optimize=1,
)

pyz = PYZ(a.pure)

# ---------------------------------------------------------------------------
# EXE — one-file bundle
# ---------------------------------------------------------------------------
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="TankBattle",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # No terminal window (GUI app)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(project_root / "tank_battle.ico"),
)
