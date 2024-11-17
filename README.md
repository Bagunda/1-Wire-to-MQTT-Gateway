# 1-Wire-to-MQTT-Gateway
Шлюз для датчиков температуры 1-Wire DS18B20 в MQTT для Home Assistant с Autodiscovery

Программа на Python 3, запускается в Линуксе.
В коде программы надо прописать МАК-адреса датчиков.
Все указанные датчики температуры добавятся в Home Assistant по технологии MQTT Autodiscovery автоматически.
Программа сканирует каждые 30 секунд папку, выявляет папки с МАК адресами датчиков температуры класса "28-*".
Потом считывает температуру из этих датчиков.
И если температура считалась, то в MQTT выставляем статус этому датчику "онлайн" и посылаем значение температуры.
Другим выставляем статус "офлайн".

Автозапуск программы после ребута:
```
[Unit]
Description=Scan 1-Wire folder and send to MQTT Temperature and availability data. And MQTT autodiscovery
After=network.target

[Service]
Type=idle
ExecStart=/usr/bin/python3 /root/bag_1wire/bag_1wire.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```
systemctl daemon-reload
systemctl enable bag_1wire_mqtt_GW.service
systemctl start bag_1wire_mqtt_GW.service
```
