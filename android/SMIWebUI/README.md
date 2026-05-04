# SMI Web UI Android App

This is a small Android WebView wrapper for the SMI machine monitor web UI.

## Default Address

The app defaults to:

```text
http://100.87.194.41:8000/
```

That is the `smi-whonot-brain` node's Tailscale address seen during setup. For remote use away from the machine, install Tailscale on the Android device and sign into the same tailnet.

For local shop Wi-Fi, tap **URL** in the app and use:

```text
http://192.168.1.84:8000/
```

## Build

Open this folder in Android Studio:

```text
android/SMIWebUI
```

Then use **Build > Build Bundle(s) / APK(s) > Build APK(s)**.

## Notes

- The app allows plain HTTP because the node web UI currently runs over HTTP.
- The URL is saved on the phone after you change it.
- The dashboard's Reolink Admin button currently points to the PC-side SSH tunnel URL. That works on this PC, but not from a phone unless we add a phone-accessible camera proxy or Tailscale subnet routing.
