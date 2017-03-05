# -*- coding: utf-8 -*-
import atexit
import os
import shutil
import sys
import tempfile

from validator import Validator


_TMP_DIR = tempfile.mkdtemp()
atexit.register(shutil.rmtree, _TMP_DIR)


if sys.platform.startswith('win'):
    def rsymlink(src, dst, symdirs=()):
        shutil.copytree(src, dst)
else:
    def rsymlink(src, dst, symdirs=()):
        """Recursively links a tree from `src` to `dst`."""

        files = [f for f in os.listdir(src)
                 if os.path.isfile(os.path.join(src, f))]
        dirs = [d for d in os.listdir(src)
                if os.path.isdir(os.path.join(src, d))]
        for f in files:
            os.symlink(os.path.join(src, f), os.path.join(dst, f))
        for d in dirs:
            if d in symdirs:
                os.symlink(os.path.join(src, d), os.path.join(dst, d))
            else:
                os.mkdir(os.path.join(dst, d))
                rsymlink(os.path.join(src, d), os.path.join(dst, d))


def cleandir(dir_):
    for item in os.listdir(dir_):
        item_path = os.path.join(dir_, item)
        if os.path.isfile(item_path):
            os.remove(item_path)
        elif os.path.islink(item_path):
            os.remove(item_path)
        elif os.path.isdir(item_path):
            shutil.rmtree(item_path)


class Tsc(Validator):
    __filetype__ = 'typescript'

    checker = 'tsc'
    args = ''
    regex = r"""
            (.*?)\(
            (?P<lnum>\d+),
            (?P<col>\d+)\):
            \s
            (?P<error>error\sTS\d+):
            \s
            (?P<text>.*)
            """

    def cmd(self, fname):
        app_path = self.filename
        while app_path:
            app_path = os.path.dirname(app_path)
            if os.path.basename(app_path) == 'app':
                break

        if app_path:
            app_root = os.path.dirname(app_path)
            sym_root = os.path.dirname(app_root)

            # create a symlink app area
            cleandir(_TMP_DIR)
            rsymlink(sym_root, _TMP_DIR, symdirs=['node_modules'])

            link_dir = os.path.join(_TMP_DIR,
                                    app_root.replace(sym_root + os.sep, ''))
            args = ' '.join(
                arg for arg in [self.cmd_args, '-p', link_dir] if arg
            )

            # use fname as a stand-in for self.filename if it exists
            new_fname = os.path.join(
                _TMP_DIR,
                self.filename.replace(sym_root + os.sep, '')
            )
            os.remove(new_fname)
            cmd = ['sh', '-c', 'cp {} {} && {} {}'.format(
                fname, new_fname, self.binary, args
            )]

        else:
            args = [arg for arg in [self.cmd_args, fname] if arg]
            cmd = [self.binary] + args

        return cmd
