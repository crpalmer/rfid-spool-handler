import asyncio
import network
import time
 
def wifi_connect(wifi):
    hostname = wifi.get("hostname", "")
    if hostname != "":
        network.hostname(hostname)
        
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    ssid = wifi.get("ssid", "")
    password = wifi.get("password", "")
    
    if ssid != "":
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
    wlan.config(ssid="rfid-spool-handler", security=0	)
    print(f"AP active with IP: {wlan.ifconfig()[0]}")