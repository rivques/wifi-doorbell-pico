from time import sleep
import wifi
import ipaddress
from adafruit_httpserver import Server, Request, Response
import socketpool
import microcontroller
import digitalio
import board

blue_pin = digitalio.DigitalInOut(board.GP14)
green_pin = digitalio.DigitalInOut(board.GP15)
blue_pin.direction = digitalio.Direction.OUTPUT
green_pin.direction = digitalio.Direction.OUTPUT

blue_pin.value = True

ap_addr = ipaddress.IPv4Address("192.168.1.1")
ap_netmask = ipaddress.IPv4Address("255.255.255.0")
ap_gateway = ipaddress.IPv4Address("192.168.1.1")
if not wifi.radio.ap_active:
    print("starting ap...")
    wifi.radio.start_ap("ENGR_DOORBELL", "mrmiller")
else:
    print("ap already up")
wifi.radio.set_ipv4_address_ap(ipv4= ap_addr, gateway = ap_gateway, netmask= ap_netmask)
pool = socketpool.SocketPool(wifi.radio)
server = Server(pool, "/static", debug=True)

@server.route("/")
def base(request: Request):  # pylint: disable=unused-argument
    #  serve the HTML f string
    #  with content type text/html
    for _ in range(5):
        green_pin.value = True
        sleep(0.2)
        green_pin.value = False
        sleep(0.2)
    for _ in range(5):
        green_pin.value = True
        blue_pin.value = True
        sleep(0.1)
        green_pin.value = False
        blue_pin.value = False
        sleep(0.1)
    return Response(request, f"Doorbell triggered!", content_type='text/plain')

try:
    server.start(str(ap_addr))
    print(f"Listening on http://{ap_addr}:80")
#  if the server fails to begin, restart the pico w
except OSError:
    sleep(5)
    print("restarting..")
    microcontroller.reset()
blue_pin.value = False
while True:
    try:
        server.poll()
    except Exception as e:
        print(e)
        continue