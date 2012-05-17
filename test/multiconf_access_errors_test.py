#!/usr/bin/python

# Copyright 2012 Lars Hupfeldt Nielsen, Hupfeldt IT
# This code is free for anybody to use

import sys
import os.path
from os.path import join as jp
here = os.path.dirname(__file__)
sys.path.append(jp(here, '../..'))

import unittest
from oktest import ok, test, fail, todo, dummy
from utils import lazy, config_error, lineno

from multiconf import ConfigRoot, ConfigItem, ConfigException
from multiconf.envs import Env, EnvGroup

prod = Env('prod')

def ce(line_num, *lines):
    return config_error(__file__, line_num, *lines)

class ErrorsTest(unittest.TestCase):
    @test("access undefined attribute")
    def _k(self):
        cr = ConfigRoot(prod, [prod])

        try:
            print cr.b
            fail ("Expected exception")
        except ConfigException as ex:
            ok (ex.message) == "ConfigRoot {\n} has no attribute 'b'"

if __name__ == '__main__':
    unittest.main()
