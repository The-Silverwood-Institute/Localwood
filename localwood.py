import web
import RPi.GPIO as GPIO
import time
import socket_setup

urls = (
    '/', 'homepage',
    '/sockets', 'sockets'
)
render = web.template.render('templates/')
app = web.application(urls, globals())

class homepage:
    def GET(self):
        return render.homepage()

class sockets:
    def POST(self):
        params = web.input()

        if not hasattr(params, 'socket'):
            raise web.badrequest('Missing URL param "socket"')

        if not hasattr(params, 'state'):
            raise web.badrequest('Missing URL param "state"')

        if params.socket == '1' and params.state == 'on':
            # See: https://energenie4u.co.uk/res/pdfs/ENER314%20UM.pdf
            print("sending code 1111 socket 1 on")
            GPIO.output (11, True)
            GPIO.output (15, True)
            GPIO.output (16, True)
            GPIO.output (13, True)
        elif params.socket == '1' and params.state == 'off':
            print("sending code 0111 socket 1 off")
            GPIO.output (11, True)
            GPIO.output (15, True)
            GPIO.output (16, True)
            GPIO.output (13, False)
        elif params.socket == '2' and params.state == 'on':
            print("sending code 1110 socket 2 on")
            GPIO.output (11, False)
            GPIO.output (15, True)
            GPIO.output (16, True)
            GPIO.output (13, True)
        elif params.socket == '2' and params.state == 'off':
            print("sending code 0110 socket 2 off")
            GPIO.output (11, False)
            GPIO.output (15, True)
            GPIO.output (16, True)
            GPIO.output (13, False)
        else:
            print('Unknown combo socket={} state={}'.format(params.socket, params.state))
            raise web.badrequest('Socket or state invalid (expects socket: 1-2 state: on/off)')

        # let it settle, encoder requires this
        time.sleep(0.1)
        # Enable the modulator
        GPIO.output (22, True)
        # keep enabled for a period
        time.sleep(1)
        # Disable the modulator
        GPIO.output (22, False)

        return 'Done'

if __name__ == "__main__":
    socket_setup.setup()
    app.run()
