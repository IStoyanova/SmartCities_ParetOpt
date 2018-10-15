#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

"""

import pycity_base.classes.demand.Room as Room


class Test_Room():

    def test_room(self, create_environment):

        room = Room.Room(environment=create_environment)
