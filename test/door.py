# -*- coding: utf-8 -*-
import gettext
from sys import exit

gettext.install('lang', './locale', unicode=False)
options = """1.left
2.right
> """

def gold_room():
    print "This room is fill of gold. How much do you take?"

    next= raw_input("> ")
    try:
        how_much = int(next)
    except ValueError:
        dead("Man, learn to type a number.")
    if how_much < 50:
        print "Nice, you're not greedy, you win!"
        exit(0)
    else:
        dead("You greedy bastard!")

def bear_room():
    gettext.translation('lang', './locale', languages=['en']).install(True)
    print _("Hello world!")
    print "There is a bear here."
    print "The bear has a bunch of honey."
    print "The fat bear is in front of another door."
    print "How are you going to move the bear?"
    bear_moved = False
    
    while True:
        next = raw_input("> ")
        if next == "take honey":
            dead("The bear looks at you then slaps your face off.")
        elif next == "taunt bear" and not bear_moved:
            print "The bear has moved from the door. You can go through it now."
        elif next == "taunt bear" and bear_moved:
            dead("The bear gets pissed off and chews your leg off.")
        elif next == "open door":
            gold_room()
        else:
            print "I got no idea what that means."

def dead(why):
    print why
    print "Good job!"
    exit(0)

def start():
    gettext.translation('lang', './locale', languages=['cn']).install(True)
    print _("Hello world!")
    print "You are in a dark room."
    print "There is a door to your right and a door to your left."
    print "Which one do you take?"

    next = raw_input(options)
    if next == "1":
        bear_room()
    elif next == "2":
        cthulhu_room()
    else:
        dead("You stumble around the room until you starve.")
start()
