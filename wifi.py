import asyncio
import network
import time

def wifi_create_ap(ssid, password="password"):
    wlan = network.WLAN(network.WLAN.IF_AP)
    wlan.active(True)
    wlan.config(ssid=ssid, password=password)
    print(f"AP active with IP: {wlan.ifconfig()[0]}")
 
def wifi_connect(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    print(f"Connecting to WiFi: {ssid}")
    wlan.connect(ssid, password)
    timeout = 30
    while not wlan.isconnected():
        time.sleep(1)
        timeout -= 1
        if timeout <= 0:
            return False
    print('Connected on IP:', wlan.ifconfig()[0])
    return True
