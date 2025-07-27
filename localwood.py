import os
import web
import RPi.GPIO as GPIO
import time
import socket_setup
import logging

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

auth_token = os.environ.get('AUTH_TOKEN')

if not auth_token:
    logging.warning("Proceeding without authentication")

if not any(os.environ.get(key) for key in ['SOCKET_1_LABEL', 'SOCKET_2_LABEL', 'SOCKET_3_LABEL', 'SOCKET_4_LABEL']):
    raise ValueError("No power sockets enabled, missing envs e.g. SOCKET_1_LABEL")

urls = (
    '/', 'homepage',
    '/sockets', 'sockets'
)
render = web.template.render('templates/')
app = web.application(urls, globals())

def authenticate_user(params):
    if auth_token:
        if not hasattr(params, 'token'):
            raise web.badrequest('Missing URL param "token"')

        if params.token != auth_token:
            raise web.badrequest('Invalid auth token')

class homepage:
    def GET(self):
        authenticate_user(web.input())

        return render.homepage(
            os.environ.get('PAGE_TITLE', "Localwood Socket Control"),
            os.environ.get('PAGE_HEADING', "Socket Control"),
            os.environ.get('SOCKET_1_LABEL'),
            os.environ.get('SOCKET_2_LABEL'),
            os.environ.get('SOCKET_3_LABEL'),
            os.environ.get('SOCKET_4_LABEL')
        )

class sockets:
    def POST(self):
        params = web.input()

        authenticate_user(params)

        if not hasattr(params, 'socket'):
            raise web.badrequest('Missing URL param "socket"')

        if not hasattr(params, 'state'):
            raise web.badrequest('Missing URL param "state"')

        if params.socket == 'all' and params.state == 'on':
            # See: https://energenie4u.co.uk/res/pdfs/ENER314%20UM.pdf
            logging.info("Sending code 1011 all sockets on")
            GPIO.output (13, True)
            GPIO.output (16, False)
            GPIO.output (15, True)
            GPIO.output (11, True)
        elif params.socket == 'all' and params.state == 'off':
            logging.info("Sending code 0011 all sockets off")
            GPIO.output (13, False)
            GPIO.output (16, False)
            GPIO.output (15, True)
            GPIO.output (11, True)
        elif params.socket == '1' and params.state == 'on':
            logging.info("Sending code 1111 socket 1 on")
            GPIO.output (13, True)
            GPIO.output (16, True)
            GPIO.output (15, True)
            GPIO.output (11, True)
        elif params.socket == '1' and params.state == 'off':
            logging.info("Sending code 0111 socket 1 off")
            GPIO.output (13, False)
            GPIO.output (16, True)
            GPIO.output (15, True)
            GPIO.output (11, True)
        elif params.socket == '2' and params.state == 'on':
            logging.info("Sending code 1110 socket 2 on")
            GPIO.output (13, True)
            GPIO.output (16, True)
            GPIO.output (15, True)
            GPIO.output (11, False)
        elif params.socket == '2' and params.state == 'off':
            logging.info("Sending code 0110 socket 2 off")
            GPIO.output (13, False)
            GPIO.output (16, True)
            GPIO.output (15, True)
            GPIO.output (11, False)
        elif params.socket == '3' and params.state == 'on':
            logging.info("Sending code 1101 socket 3 on")
            GPIO.output (13, True)
            GPIO.output (16, True)
            GPIO.output (15, False)
            GPIO.output (11, True)
        elif params.socket == '3' and params.state == 'off':
            logging.info("Sending code 0101 socket 3 off")
            GPIO.output (13, False)
            GPIO.output (16, True)
            GPIO.output (15, False)
            GPIO.output (11, True)
        elif params.socket == '4' and params.state == 'on':
            logging.info("Sending code 1100 socket 4 on")
            GPIO.output (13, True)
            GPIO.output (16, True)
            GPIO.output (15, False)
            GPIO.output (11, False)
        elif params.socket == '4' and params.state == 'off':
            logging.info("Sending code 0100 socket 4 off")
            GPIO.output (13, False)
            GPIO.output (16, True)
            GPIO.output (15, False)
            GPIO.output (11, False)
        else:
            logging.info('Unknown combo socket=%s state=%s', params.socket, params.state)
            raise web.badrequest('Socket or state invalid (expects socket: 1-4 state: on/off)')

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
