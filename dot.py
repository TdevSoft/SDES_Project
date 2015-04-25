#!/usr/bin/env python

class Dot(object):
    def __init__(self,xy):
        self.x=xy[0]
        self.y=xy[1]

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def set_x(self):
        return self.x

    def set_y(self):
        return self.y

    def __eq__(self,other):
        return(self.get_x()==other.get_x() and self.get_y()==other.get_y())
