## Run test suite:
```bash
cd digital_me/test
pip3 install -r requirements.txt
nosetests-3.4 -sv  --logging-level=WARNING test01_vms.py:VMTestCases.test003_reinstall_vm_0_ubuntu --tc-file=config.ini --tc=main.ztoken:{$zt_token}
```