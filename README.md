# M3-Gateway
Python-Backend for M3-Sensors

UartMessageSplitter:
Nimmt die M3-Nachrichten entgegen

M3Decoder:
Prüft syntaktisch und verteilt die Nachrichten in Queues für Discovery oder für Clients

M3MQTTClient:
Nimmt die Nachrichten der Clients und sendet sie an den MQTT-Broker (mit Stammdaten von UI)

WebUI:
Verwaltet die IDs und die dazugehörenden Stammdaten

+-------------------+ (raw) +---------+    +------------+
|UartMessageSplitter|  -->  |M3Decoder| -> |M3MQTTClient| --> MQTT-Broker
+-------------------+       +---------+    +------------+
                                 |                .
                                 | (discovery)    . (rest)
                                 v                v
                              +-----+      +------------+
                              |WebUI| ...> |M3Masterdata|
                              +-----+      +------------+