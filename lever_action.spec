# -*- mode: python ; coding: utf-8 -*-
block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/lever_action/templates', 'templates'),
        ('src/lever_action/static', 'static'),
        ('src/lever_action/services', 'services'),
        ('src/lever_action/storage', 'storage'),
        ('dandy_settings.py', '.'),
        ('settings.json', '.'),
        ('reticle.ico', '.'),
    ],
    hiddenimports=[
        'lever_action',
        'lever_action.services.chat_service',
        'lever_action.storage.history',
        'lever_action.storage.sessions',
        'lever_action.storage.settings',
        'bottle',
        'markdown',
        'pygments',
        'pygments.lexers',
        'pygments.formatters',
        'dotenv',
        'webview',
        'webview.platforms.edgechromium',
        'pythonnet',
        'clr',
        'clr_loader',
    ],
    hookspath=['hooks'],
    hooksconfig={},
    runtime_hooks=['hooks/rthook_pythonnet.py'],
    excludes=[
        'tkinter',
        'PyQt6',
        'PyQt5',
        'PySide6',
        'PySide2',
        'curses',
        'readline',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='lever_action',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements=None,
    icon='reticle.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='lever_action',
)