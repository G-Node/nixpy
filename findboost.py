#!/usr/bin/env python
# coding=utf-8

from __future__ import print_function
from __future__ import division

import os
import re
import sys


class BoostPyLib(object):
    matcher = re.compile(r'libboost_python(?:-py)?(\d{0,2})((?:-\w+[^-])*)\.(?:so|dylib|lib)')

    def __init__(self, path, major, minor, ismt):
        self.filename = path
        self.major = major
        self.minor = minor
        self.threadsafe = ismt

    def match(self, major, minor, threadsafe, ignore_threading=False):
        return self.major == major and self.minor == minor and (ignore_threading or self.threadsafe == threadsafe)

    @property
    def link_directive(self):
        name, ext = os.path.splitext(self.filename)
        if ext == 'lib':
            return "/DEFAULTLIB:" + self.filename
        else:
            return '-l' + name[3:]

    def __str__(self):
        major = str(self.major or '?')
        minor = str(self.minor or '?')
        mt = 'threadsafe' if self.threadsafe else ''
        return "%s [%s.%s] (%s) " % (self.filename, major, minor, mt)

    @classmethod
    def list_in_dir(cls, path):
        return list(filter(lambda x: x is not None, [cls.make_from_path(f) for f in os.listdir(path)]))

    @classmethod
    def make_from_path(cls, path):
        filename = os.path.basename(path)
        m = cls.matcher.match(filename)
        if m is None:
            return m
        ismt = '-mt' in m.group(2)
        major, minor = cls.parse_version(m.group(1))
        return cls(filename, major, minor, ismt)

    @classmethod
    def find_lib_for_current_python(cls, libs):
        v_major, v_minor = sys.version_info[:2]
        match = cls.find_lib_with_version(libs, (v_major, v_minor), unknown_is_match=v_major == 2)
        return match

    @staticmethod
    def find_lib_with_version(available, version, unknown_is_match=False):
        major, minor = version[0], version[1]
        criteria = [(major, minor), (major, None)] + ([(None, None)] if unknown_is_match else [])
        for c in [[c[0], c[1], mt] for c in criteria for mt in [True, False]]:
            res = list(filter(lambda x: x.match(*c), available))
            if len(res) == 1:
                return res[0]
        return None

    @staticmethod
    def parse_version(input):
        major, minor = None, None
        try:
            major = int(input[0])
            minor = int(input[1])
        except (IndexError, ValueError):
            pass
        return major, minor

    @classmethod
    def selftest(cls):
        survey = [
            ('libboost_python.so', (None, None, False)),
            ('libboost_python3.so', (3, None, False)),
            ('libboost_python.dylib', (None, None, False)),
            ('libboost_python3.dylib', (3, None, False)),
            ('libboost_python-py27.so', (2, 7, False)),
            ('libboost_python-py34.so', (3, 4, False)),
            ('libboost_python-py35.so', (3, 5, False)),
            ('libboost_python.lib', (None, None, False)),
            ('libboost_python-mt.dylib', (None, None, True)),
            ('libboost_python-vc120-mt-1_57.lib', (None, None, True)),
            ('/usr/lib/libboost_python.a', None)]

        try:
            ml = max(map(lambda s: len(s[0]), survey)) + 3
            for s, c in survey:
                o = cls.make_from_path(s)
                sys.stderr.write('Checking: ' + s)
                assert(c is not None or o is None)
                assert(o is not None or c is None)
                assert(o is None or o.match(*c))
                sys.stderr.write(u' '*(ml - len(s)) + u'✓\n')
        except AssertionError as e:
            print("Self-test failed:", e, file=sys.stderr)
            return -1
        return 0


if __name__ == '__main__':
    import argparse
    default_path = os.getenv('NIX_LIBDIR', '/usr/local/lib')
    parser = argparse.ArgumentParser('NixPy - find boost python libraries')
    parser.add_argument('--path', default=default_path, help='Path to search libraries in [%s]' % default_path)
    parser.add_argument('--selftest', default=False, action='store_true', help='Perform a self-test')
    args = parser.parse_args()

    v_major, v_minor = sys.version_info[:2]

    print('Python version: [%d.%d]' % (v_major, v_minor), file=sys.stderr)
    if args.selftest:
        ret = BoostPyLib.selftest()
        sys.exit(ret)

    libs = BoostPyLib.list_in_dir(default_path)
    for lib in libs:
        print(' %s [%s]' % (str(lib), lib.link_directive), file=sys.stderr)
        linked = BoostPyLib.find_lib_with_version(libs, (v_major, v_minor), unknown_is_match=v_major == 2)
        if linked is not None:
            print(' match: ' + str(linked), file=sys.stderr)
            print(linked.link_directive)
        else:
            print('No usable boost python lib found! :(', file=sys.stderr)
            sys.exit(-1)
