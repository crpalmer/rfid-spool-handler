import asyncio
import network
import time
 
def wifi_connect(wifi):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    ssid = wifi["ssid"]
    password = wifi["password"]
    
    if ssid is not None and ssid != "":
        print(f"Connecting to WiFi: {ssid}")
        wlan.connect(ssid, password)
        timeout = 30
        while timeout > 0:
            if wlan.isconnected():
                print('Connected on IP:', wlan.ifconfig()[0])
                return
            time.sleep(1)
            timeout -= 1

    wlan = network.WLAN(network.WLAN.IF_AP)
    wlan.active(True)
    wlan.config(ssid="rfid-spool-handler", password="password")
    print(f"AP active with IP: {wlan.ifconfig()[0]}")