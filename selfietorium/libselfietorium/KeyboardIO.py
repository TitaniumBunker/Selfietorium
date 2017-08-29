#!/usr/bin/python
# coding=utf-8

import Event

class KeyboardIO :
    """A class for handling the IO for Selfietorium,  """
    evt_foo = Event.Event()
    
    def foo(self):
        # Do some actions and fire event.
        self.evt_foo()
    