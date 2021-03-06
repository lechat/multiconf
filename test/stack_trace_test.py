# Copyright (c) 2012 Lars Hupfeldt Nielsen, Hupfeldt IT
# All rights reserved. This work is under a BSD license, see LICENSE.TXT.

# pylint: disable=E0611
from pytest import raises

from .utils.utils import config_error, lineno, replace_ids

from .. import ConfigRoot, ConfigItem, ConfigException, ConfigBuilder
from ..decorators import nested_repeatables, repeat
from ..envs import EnvFactory

ef = EnvFactory()
pp = ef.Env('pp')
prod = ef.Env('prod')


_expected_ex_msg = "An error was detected trying to get attribute '%s' on class 'inner'"
_extra_stderr = """
    - Attributes starting with '_mc' are reserved for internal MultiConf usage. You probably tried to use the
      MultiConf API in a derived class __init__ before calling the parent class __init__"""


def ce(line_num, *lines):
    return config_error(__file__, line_num, *lines)


@nested_repeatables('RepeatableItems')
class project(ConfigRoot):
    pass


@repeat()
class RepeatableItem(ConfigItem):
    pass


_stacktrace_strips_multiconf_code_exp_ex = """There were 3 errors when defining attribute 'a' on object: {
    "__class__": "inner #as: 'xxxx', id: 0000, not-frozen",
    "a #no value for current env": true
}"""

def test_stacktrace_strips_multiconf_code(capsys):
    with raises(ConfigException) as exinfo:
        class root(ConfigRoot):
            pass

        class inner(ConfigItem):
            pass

        with root(prod, ef, a=0):
            with inner():
                with inner() as ii2:
                    errorline = lineno() + 1
                    ii2.setattr('a', qq=3)

    _sout, serr = capsys.readouterr()
    assert serr == ce(errorline,
                      "No such Env or EnvGroup: 'qq'",
                      "Attribute: 'a' did not receive a value for env Env('pp')",
                      "Attribute: 'a' did not receive a value for current env Env('prod')")
    assert replace_ids(exinfo.value.message) == _stacktrace_strips_multiconf_code_exp_ex
    assert len(exinfo.traceback) == 2, "Traceback: " + repr(exinfo.traceback)
    # TODO py.test exinfo.traceback[0].lineno is off by 1!
    assert exinfo.traceback[0].lineno == errorline - 1


def test_stacktrace_from_user_validate_code():
    with raises(Exception) as exinfo:
        class root(ConfigRoot):
            pass

        class inner(ConfigItem):
            def validate(self):
                global validate_errorline
                validate_errorline = lineno() + 1
                raise Exception("In inner validate")

        with root(prod, ef, a=0):
            with inner():
                errorline = lineno() + 1
                inner()

    assert len(exinfo.traceback) > 2

    # TODO py.test exinfo.traceback[0].lineno is off by 1!
    assert exinfo.traceback[0].lineno == errorline - 1
    assert exinfo.traceback[0].path == __file__

    # TODO py.test exinfo.traceback[0].lineno is off by 1!
    assert exinfo.traceback[-1].lineno == validate_errorline - 1
    assert exinfo.traceback[-1].path == __file__


def test_stacktrace_from_user_build_code():
    with raises(Exception) as exinfo:
        class root(ConfigRoot):
            pass

        class inner(ConfigBuilder):
            def build(self):
                global build_errorline
                build_errorline = lineno() + 1
                raise Exception("In inner build")

        with root(prod, ef, a=0):
            with inner():
                errorline = lineno() + 1
                inner()

    assert len(exinfo.traceback) > 2

    # TODO py.test exinfo.traceback[0].lineno is off by 1!
    assert exinfo.traceback[0].lineno == errorline - 1
    assert exinfo.traceback[0].path == __file__

    # TODO py.test exinfo.traceback[0].lineno is off by 1!
    assert exinfo.traceback[-1].lineno == build_errorline - 1
    assert exinfo.traceback[-1].path == __file__
