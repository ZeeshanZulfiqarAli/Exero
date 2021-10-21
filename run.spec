# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


from PyInstaller.utils.hooks import collect_submodules, collect_data_files
tf_hidden_imports = collect_submodules('tensorflow_core')
tf_datas = collect_data_files('tensorflow_core', subdir=None, include_py_files=True)

a = Analysis(['run.py'],
             pathex=['D:\\zeeshan work\\fyp gui\\Exero'],
             binaries=[],
             datas= tf_datas + [('src/model', 'model'),('src/defaultSettings.xml', '.'),('src/splashScreen.svg', '.')],
             hiddenimports= tf_hidden_imports + [],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='Exero',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          icon='src/final_fyp_logo_x05_icon.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='Exero')
