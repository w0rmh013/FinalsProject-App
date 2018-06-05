from cx_Freeze import setup, Executable

build_options = {'packages': ['idna', 'paramiko', 'ecdsa', 'scp']}

setup(name='user_locker_service', version='0.2', description='Background service for download and upload',
      options={'build_exe': build_options}, executables=[Executable('user_locker_service.py')])
