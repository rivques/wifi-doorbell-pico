import digitalio
import board
import time
import ssl
import wifi
import socketpool
import microcontroller
import adafruit_requests
import alarm

blue_pin = digitalio.DigitalInOut(board.GP14)
green_pin = digitalio.DigitalInOut(board.GP15)
blue_pin.direction = digitalio.Direction.OUTPUT
green_pin.direction = digitalio.Direction.OUTPUT

green_pin.value = True
blue_pin.value = True
#  adafruit quotes URL
target_url = "http://192.168.1.1"

#  connect to SSID
try:
    wifi.radio.connect("ENGR_DOORBELL", "mrmiller")
    pool = socketpool.SocketPool(wifi.radio)
    requests = adafruit_requests.Session(pool, ssl.create_default_context())
except Exception as e:
    print(f"error while connecting: {e}")
    blue_pin.value = False
    microcontroller.reset()

blue_pin.value = False
green_pin.value = False
if alarm.wake_alarm is not None:
    blue_pin.value=True
    print("Fetching text from %s" % target_url)
    try:
        response = requests.get(target_url, timeout=5)
    except Exception as e:
        print(f"error while REQUESTING: {e}")
        blue_pin.value = False
        microcontroller.reset()
    blue_pin.value=False
    green_pin.value = True
    print(f"Got response: {response.text}")
    response.close()
    time.sleep(5)
    green_pin.value = False
    alert_from_alarm_needed = False
print("deep sleeping...")
wifi.radio.stop_station()
alarm.exit_and_deep_sleep_until_alarms(alarm.pin.PinAlarm(pin=board.GP20, value=False, pull=True))