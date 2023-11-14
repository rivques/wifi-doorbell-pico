from time import sleep
import wifi
import ipaddress
from adafruit_httpserver import Server, Request, Response
import socketpool
import microcontroller

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
    return Response(request, f"Hello world!", content_type='text/plain')

try:
    server.start(str(ap_addr))
    print("Listening on http://%s:80" % ap_addr.ipv4_address)
#  if the server fails to begin, restart the pico w
except OSError:
    sleep(5)
    print("restarting..")
    microcontroller.reset()

while True:
    try:
        server.poll()
    except Exception as e:
        print(e)
        continue