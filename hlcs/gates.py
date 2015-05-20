'''
Created on 08/nov/2014

@author: spax
'''

import sys

from gatecontrol.gatecontrol import Gate, STATE_CLOSED, STATE_OPEN
from hlcs.modem import AtlantisModem


STATE_RING = {'id' : 2, 'description' : 'ring'}

class HpccExternal(Gate):
    
    def __init__(self, modem=None):
        if modem is None:
            self.modem = AtlantisModem()
        else:
            self.modem = modem
        
    def get_available_states(self):
        return (STATE_CLOSED, STATE_OPEN, STATE_RING)
    
    def open_gate(self, request):
        self.controller = self.modem.get_controller()
        self.controller.setup(request)
        self.controller.start()
        
    def get_state(self, request=None):
        if request is None:
            return STATE_CLOSED
        elif request.is_ok():
            return STATE_OPEN
        elif request.is_pending():
            return STATE_RING
        else:
            return STATE_CLOSED

        
        
class HpccInternal(Gate):
    
    def __init__(self):
        try:
            from hlcs.gpio import magnet_input, send_open_pulse
            self.magnet_input = magnet_input
            self.send_open_pulse = send_open_pulse
        except Exception as e:
            print ('ERROR: could not setup %s: %s' % (HpccInternal.__name__, str(e)))
            sys.exit(1)
    
    def get_state(self, request=None):
        is_open = self.magnet_input()
        return STATE_OPEN if is_open else STATE_CLOSED
    
    def open_gate(self, request=None):
        if request is not None:
            if request.user.is_staff:
                self.send_open_pulse()
                self.state = STATE_OPEN
                request.done()
            else:
                request.fail('Access denied')


