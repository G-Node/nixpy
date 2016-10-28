from __future__ import print_function
from __future__ import division

import os
import re
import sys
from operator import itemgetter


try:
    from commands import getstatusoutput
except ImportError:
    from subprocess import getstatusoutput


class BoostPyLib(object):
    matcher = re.compile(r'^libboost_python(?:-py)?(\d{0,2})((?:-\w+[^-])*)\.(?:so|dylib|lib)$')

    def __init__(self, path, name, major, minor, ismt):
        self.path = path
        self.filename = name
        self.major = major
        self.minor = minor
        self.threadsafe = ismt

    def match(self, major, minor, threadsafe, ignore_threading=False):
        return self.major == major and self.minor == minor and (ignore_threading or self.threadsafe == threadsafe)

    @property
    def library_name(self):
        name, ext = os.path.splitext(self.filename)
        return name if ext == ".lib" else name[3:]

    @property
    def link_directive(self):
        name, ext = os.path.splitext(self.filename)
        if ext == '.lib':
            return ["/DEFAULTLIB:" + self.filename, '/LIBPATH:' + self.path]
        else:
            return ['-l' + name[3:]]

    def __str__(self):
        major = str(self.major or '?')
        minor = str(self.minor or '?')
        mt = 'threadsafe' if self.threadsafe else ''
        return "%s [%s.%s] (%s) " % (self.filename, major, minor, mt)

    @staticmethod
    def library_search_dirs(additional_dirs=None):
        dirs = additional_dirs or []
        cc = os.getenv("CC", "cc")
        cmd = "%s --print-search-dirs | grep ^libraries" % cc
        res, out = getstatusoutput(cmd)
        if res != 0:
            print("WARNING: \"%s\" failed with %d" % (cmd, res), file=sys.stderr)
            return dirs

        start = out.find("=") + 1
        paths = out[start:].split(":")
        ordered_set = {k: idx for idx, k in enumerate(paths)}
        ordered_set.update({d: -1*(len(dirs) - i) for i, d in enumerate(dirs)})
        return list(map(itemgetter(0), (sorted(ordered_set.items(), key=itemgetter(1)))))

    @classmethod
    def list_in_dirs(cls, dirs):
        return list(cls.iterate_libs_in_dirs(dirs))

    @classmethod
    def iterate_libs_in_dirs(cls, dirs):
        for d in dirs:
            if not os.path.isdir(d):
                continue
            for f in os.listdir(d):
                l = cls.make_from_path(f)
                if l is not None:
                    yield l

    @classmethod
    def make_from_path(cls, path):
        filename = os.path.basename(path)
        dirname = os.path.dirname(path)
        m = cls.matcher.match(filename)
        if m is None:
            return m
        ismt = '-mt' in m.group(2)
        major, minor = cls.parse_version(m.group(1))
        return cls(dirname, filename, major, minor, ismt)

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
            if len(res) > 0:
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
            ('libboost_python-py27.so.1.55.0', None),
            ('libboost_python-py34.so', (3, 4, False)),
            ('libboost_python-py35.so', (3, 5, False)),
            ('libboost_python.lib', (None, None, False)),
            ('libboost_python-mt.dylib', (None, None, True)),
            ('libboost_python-vc120-mt-1_57.lib', (None, None, True)),
            ('libboost_python-vc120-mt-1_61.lib', (None, None, True)),
            ('/usr/lib/libboost_python.a', None)]

        try:
            ml = max(map(lambda s: len(s[0]), survey)) + 3
            for s, c in survey:
                o = cls.make_from_path(s)
                sys.stderr.write('Checking: ' + str(o and str(o.match(*c))) + s)
                assert(c is not None or o is None)
                assert(o is not None or c is None)
                assert(o is None or o.match(*c))
                sys.stderr.write(' '*(ml - len(s)) + 'ok\n')
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

    libs = BoostPyLib.list_in_dirs([default_path])
    for lib in libs:
        print(' %s (ld: %s)' % (str(lib), lib.link_directive), file=sys.stderr)
        linked = BoostPyLib.find_lib_with_version(libs, (v_major, v_minor), unknown_is_match=v_major == 2)
        if linked is not None:
            print(' match: ' + str(linked), file=sys.stderr)
            print(' linker command: ' + str(linked.link_directive))
            print(' library name: ' + linked.library_name)
        else:
            print('No usable boost python lib found! :(', file=sys.stderr)
            sys.exit(-1)
