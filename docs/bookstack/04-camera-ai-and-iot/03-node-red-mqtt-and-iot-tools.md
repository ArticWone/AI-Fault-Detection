# Node-RED, MQTT, and IoT Tools

## Installed Tools

- Node-RED `v4.1.8`
- `node-red-contrib-modbus`
- Mosquitto MQTT broker
- `mosquitto_pub` / `mosquitto_sub`
- `mbpoll` for terminal Modbus testing

## Security Posture

Node-RED and MQTT are installed but bound to localhost by default. Use the SMI Web UI Admin panel to temporarily open LAN access when needed.

## Useful Tests

```bash
mosquitto_pub -h 127.0.0.1 -t smi/test -m ok
mosquitto_sub -h 127.0.0.1 -t smi/test
mbpoll -m tcp -a 1 -r 10112 -c 4 192.168.0.1
```

## Windows GUI Tool

QModMaster is a useful Windows GUI Modbus master for manual testing. On the node, `mbpoll` is more useful over SSH.
