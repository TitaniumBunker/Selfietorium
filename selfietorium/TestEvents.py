# -*- coding: utf-8 -*-
from libselfietorium import Event
import sys
import select
import pygame
import pygame.display

class Publisher(object):
    """A Fake IO object (like a keyboard)... """
    def __init__(self):
        # Set event object
        self.evt_foo = Event.Event()
        self.evt_quit = Event.Event()
        self.evt_testSound = Event.Event()

    def foo(self):
        # Call event object with self as a sender
        self.evt_foo(self)

    def event_logic(self):
        print"Event Logic start"
        while True:
            #print "looping"
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        self.evt_quit(self)
                    elif event.key == pygame.K_p:
                        self.evt_foo(self)

    def run(self):
        i,o,e = select.select([sys.stdin],[],[],0.0001)
        for s in i:
            if s == sys.stdin:
                input = sys.stdin.readline()
                return True
        return False


        """
        Event logic - determining what events to activate based on key presses.
        """
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    self.evt_quit
                elif event.key == pygame.K_p:
                    self.evt_foo











# Event handler may be a function or a instance method etc.
# Every handler must accept two arguments; a sender and an event-specific
# parameter.
def handle_foo(sender, earg):
    print 'foo!'

def handle_quit(sender, earg):
    print 'quit'

if __name__ == '__main__':
    pub = Publisher()
    # Add event handler
    pub.evt_foo += handle_foo
    pub.evt_quit += handle_quit
    # This will cause Publiser.evt_foo event.
    pub.run()
    while True:
        pass
    #pub.foo()