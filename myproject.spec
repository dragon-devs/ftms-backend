# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['manage.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['django.contrib.admin.apps',
    	'django.contrib.auth.apps',
    	'django.contrib.contenttypes.apps',
    	'django.contrib.sessions.apps',
    	'django.contrib.messages.apps',
    	'django.contrib.staticfiles.apps',
    	'corsheaders.apps',
    	'rest_framework.apps',
    	'ftms.apps.FtmsConfig',
    	'tournament.apps',
    	'knockout.apps',
    	'group_stages.apps'],
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
    name='myproject',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)


