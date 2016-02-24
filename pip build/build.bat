copy ..\__init__.py  att_iot_client\__init__.py
copy ..\ATT_IOT.py  att_iot_client\ATT_IOT.py
python setup.py sdist
python setup.py sdist upload