#!/usr/bin/python3
# -*- coding: utf-8 -*-
from requests import get, post
import json

def clip(value, lower, upper):
    return lower if value < lower else upper if value > upper else value

class Wled():
    """
    Interface with WLED light strip controller boards via JSON API.

    Parameters:
        host: IP address or hostname of the WLED controller
    """

    host = None

    def __init__(self, host):
        self.host = host
        
        self.effects = self.get_effects()

        self._name = None
        self._state = None
        self._brightness = None
        self._transition = None
        self._effect = None
        self._color = None

    def get_all(self):
        """Get all JSON objects for WLED controller"""
        request = get("http://"+self.host+"/json")
        return json.loads(request.text)

    def get_info(self):
        """Get info about the WLED controller"""
        request = get("http:/"+self.host+"/json/info")
        return json.loads(request.text)

    def get_state(self):
        """Get the current state of the WLED controller"""
        request = get("http://"+self.host+"/json/state")
        return json.loads(request.text)

    def get_effects(self):
        """
        Get the list of available effects.

        Returns:
            list of effects available to the WLED controller
        """
        
        request = get("http://"+self.host+"/json/eff")
        return json.loads(request.text)

    def set_state(self, state):
        """
        Send a state update command to change the state of the WLED controller

        Parameters:
            state: object to be converted to JSON during POST to WLED controller

        Returns:
            Request response object from Requests module
        """
        request = post("http://"+self.host+"/json/state", data=json.dumps(state))
        return request

    def is_valid(self):
        """Return True if host is a valid WLED controller"""
        try:
            data = self.get_all()
            if data["info"]["brand"] == "WLED":
                return True
            else:
                return False
        except:
            return False


    def update(self):
        """
        Update parameters for the WLED controller
        """

        data = self.get_all()
        self._state = data["state"]["on"]
        self._brightness = data["state"]["bri"]
        self._transition = data["state"]["transition"]
        self._effects = data["effects"]
        self._name = data["info"]["name"]
        self._color = data["state"]["seg"][0]["col"][0]
        self._effect = self._effects[data["state"]["seg"][0]["fx"]]


    def turn_off(self):
        """Send a payload to the WLED controller to turn the lights off"""
        state = {"on": False}
        response = self.set_state(state)
        response_json = json.loads(response.text)
        self._state = response_json["state"]["on"]

        if self._state == False:
            return True
        else:
            return False

    def turn_on(self):
        """Send a payload to the WLED controller to turn the lights on"""
        state = {"on": True}
        response = self.set_state(state)
        response_json = json.loads(response.text)
        self._state = response_json["state"]["on"]

        if self._state == True:
            return True
        else:
            return False

    def is_on(self):
        """Return True if WLED strip is on. False if WLED strip is off."""

        return self._state

    def set_brightness(self, brightness):
        """
        Set the brightness to 0 through 255

        Parameters:
            brightness: int of 0 through 255 for 0% - 100% brightness
        """
        state = {"bri": clip(int(brightness), 0 , 255)}
        return self.set_state(state)

    def get_brightness(self):
        """
        Get current brightness (0-255)
        
        Returns:
            integer of current brightness represented as 0 through 255
        """

        return int(self.get_state()["bri"])

    def get_transition(self):
        """
        Get current transition duration. One unit equals 100ms, so a value of 4
        retults in a transition of 400ms. This is the time between 
        colors/brightness levels.

        returns:
            integer of transition duration
        """

        return int(self.get_state()["transition"])

    def set_transition(self, transition):
        """
        Sets transition time betwen color/brightness levels. One unit equals
        100ms, so a value of 4 results in a transition of 400ms.

        Parameters:
            transition: transition duration divided by 100ms
        """

        state = {"transition": int(transition)}
        return self.set_state(state)

    def set_effect(self, effect):
        """
        Sets the effect for the entire strip.

        Parameters:
            effect: index of effect to use from the get_effect() method
        """
        state = {"seg": [{"fx": int(effect)}]}
        return self.set_state(state)

    def set_effect_by_name(self, effect_name):
        """
        Sets the effect by name

        Parameters:
            effect_name: name of the effect from the get_effects() method
        """

        effects = self.get_effects()
        if effect_name in effects:
            effect_index = effects.index(effect_name)
        else:
            raise ValueError("{effect_name} not found in effects")

        return self.set_effect(effect_index)

    def get_effect(self):
        """
        Get the current effect of the WLED strip.

        Returns:
            Effect index of current effect
        """

        return self.get_state()["seg"][0]["fx"]

    def get_effect_name(self):
        """
        Get the name of the current effect

        Returns:
            Effect name of the current effect
        """

        wled_all = self.get_all()

        effects = wled_all["effects"]
        cur_effect = wled_all["state"]["seg"][0]["fx"]
        return effects[cur_effect]

    def set_color(self, color):
        """
        Sets the strip primary color. Does not support secondary/tertiary colors

        Parameters:
            color: List of RGB or RGBW values
        """

        state = {"seg": [{"col": [color, [0,0,0], [0,0,0]]}]}
        return self.set_state(state)

    def get_color(self):
        """
        Gets the strip's primary color.

        Returns:
            List of RGB/RGBW values representing color values 0-255
        """
        return self.get_state()["seg"][0]["col"][0]


    @property
    def brightness(self):
        return self._brightness
    
    @brightness.setter
    def brightness(self, bri):
        self.set_brightness(bri)
        self._brightness = bri

    @property
    def transition(self):
        return self._transition

    @transition.setter
    def transition(self, tran):
        self.set_transition(tran)
        self._transition = tran

    @property
    def effects(self):
        return self._effects

    @effects.setter
    def effects(self, eff):
        self._effects = eff
    
    @property
    def name(self):
        return self._name
    
    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, new_color):
        self.set_color(new_color)
        self._color = new_color

    @property
    def effect(self):
        return self._effect
    
    @effect.setter
    def effect(self, new_effect):
        self.set_effect_by_name(new_effect)
        self._effect = new_effect
    
    @property
    def state(self):
        return self._state
    