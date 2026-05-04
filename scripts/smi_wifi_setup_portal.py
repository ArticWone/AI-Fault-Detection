#!/usr/bin/env python3
import html
import json
import os
import subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs


IFACE = os.environ.get("SMI_WIFI_IFACE", "wlx6c4cbce74d9c")
NETPLAN_PATH = os.environ.get("SMI_WIFI_NETPLAN", "/etc/netplan/10-wifi-live.yaml")
HOSTAPD_PID = os.environ.get("SMI_HOSTAPD_PID", "/run/smi-wifi-setup/hostapd.pid")
DNSMASQ_PID = os.environ.get("SMI_DNSMASQ_PID", "/run/smi-wifi-setup/dnsmasq.pid")
PORT = int(os.environ.get("SMI_SETUP_PORT", "80"))


def shell(command):
    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)


def quoted(value):
    return json.dumps(value)


def write_netplan(ssid, password):
    body = f"""network:
  version: 2
  wifis:
    {IFACE}:
      dhcp4: true
      dhcp6: true
      optional: true
      access-points:
        {quoted(ssid)}:
          password: {quoted(password)}
"""
    with open(NETPLAN_PATH, "w", encoding="utf-8") as file:
        file.write(body)
    os.chmod(NETPLAN_PATH, 0o600)


def stop_pid(path):
    try:
        with open(path, "r", encoding="utf-8") as file:
            pid = file.read().strip()
        if pid:
            shell(["kill", pid])
    except FileNotFoundError:
        pass


def apply_wifi(ssid, password):
    write_netplan(ssid, password)
    stop_pid(DNSMASQ_PID)
    stop_pid(HOSTAPD_PID)
    shell(["ip", "addr", "flush", "dev", IFACE])
    shell(["ip", "link", "set", IFACE, "up"])
    subprocess.Popen(["netplan", "apply"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.respond(
            200,
            """<!doctype html>
<html><head><meta name="viewport" content="width=device-width, initial-scale=1">
<title>SMI Node Wi-Fi Setup</title>
<style>
body{font-family:system-ui,sans-serif;background:#eef2f3;color:#172321;margin:0;padding:24px}
main{max-width:420px;margin:auto;background:white;border:1px solid #d8e0de;border-radius:8px;padding:18px}
label{display:block;font-weight:700;margin-top:12px}input{width:100%;min-height:40px;font:inherit;margin-top:5px;padding:8px}
button{width:100%;min-height:44px;margin-top:18px;background:#1e6b7d;color:white;border:0;border-radius:8px;font-weight:800}
p{color:#66736f}
</style></head><body><main>
<h1>SMI Node Wi-Fi Setup</h1>
<p>Enter the Wi-Fi network the node should join. The setup hotspot will turn off after applying.</p>
<form method="post">
<label>Wi-Fi Name</label><input name="ssid" autocomplete="off" required>
<label>Password</label><input name="password" type="password" minlength="8" maxlength="63" required>
<button type="submit">Connect Node</button>
</form></main></body></html>""",
        )

    def do_POST(self):
        length = int(self.headers.get("content-length", "0"))
        data = parse_qs(self.rfile.read(length).decode("utf-8", errors="replace"))
        ssid = data.get("ssid", [""])[0].strip()
        password = data.get("password", [""])[0]
        if not ssid or not (8 <= len(password) <= 63):
            self.respond(400, "Invalid Wi-Fi name or password length.")
            return

        self.respond(
            200,
            f"<html><body><h1>Applying Wi-Fi</h1><p>Connecting to {html.escape(ssid)}. The setup network will disconnect.</p></body></html>",
        )
        apply_wifi(ssid, password)

    def respond(self, status, body):
        encoded = body.encode("utf-8")
        self.send_response(status)
        self.send_header("content-type", "text/html; charset=utf-8")
        self.send_header("content-length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, format, *args):
        return


if __name__ == "__main__":
    ThreadingHTTPServer(("192.168.50.1", PORT), Handler).serve_forever()
