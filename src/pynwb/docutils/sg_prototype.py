# -*- coding: utf-8 -*-

"""Top-level package for sg-prototype.

Example usage:
from pynwb.docutils.sg_prototype import  build
build('/Users/nicholasc/projects/pynwb/issues/414/helloworld.py', conda_env='pynwb')

"""

import tempfile
import os
import subprocess
import shutil
from sys import platform as _platform

__author__ = """Nicholas Cain"""
__email__ = 'nicholasc@alleninstitute.org'
__version__ = '0.1.0'

OPEN_DEFAULT = False
TGT_DIR_DEFAULT_SUFFIX = os.path.abspath('_html_sg-prototype')
TGT_DIR_DEFAULT = os.path.abspath(os.path.join('.', TGT_DIR_DEFAULT_SUFFIX))


def assert_firefox():

    try:
        subprocess.check_output(['firefox', '--version'])
        return True
    except Exception as e:
        return False


def check_tgt_dir(tgt_dir):
    if os.path.exists(tgt_dir):
        raise RuntimeError('Target directory %s already exists; specify different directory \
                            (-o or --output) or remove' % tgt_dir)


def build(src_file, tgt_dir=TGT_DIR_DEFAULT, open_html=OPEN_DEFAULT, conda_env=None):

    # Get temporary build dir, and make html using template:
    temp_dir = tempfile.mkdtemp()
    template_loc = 'https://github.com/nicain/sg-template.git'

    err_code = subprocess.call('git clone %s %s' % (template_loc, temp_dir), shell=True)
    assert err_code == 0

    # remove the template example, and replace with user-supplied file
    if src_file is not None:
        os.remove(os.path.join(temp_dir, 'docs', 'gallery', 'helloworld.py'))
        shutil.copy(src_file, os.path.join(temp_dir, 'docs', 'gallery', os.path.basename(src_file)))

    print(os.path.join(temp_dir, 'docs'))
    if conda_env is None:
        err_code = subprocess.call('cd %s && make html' % os.path.join(temp_dir, 'docs'), shell=True)
    else:
        err_code = subprocess.call('source activate %s && \
                                    cd %s && make html' % (conda_env, os.path.join(temp_dir, 'docs')), shell=True)
    assert err_code == 0

    # Move built html to tgt_dir:
    check_tgt_dir(tgt_dir)
    shutil.move(os.path.join(temp_dir, 'docs', '_build', 'html'), tgt_dir)

    # Grab out generated example file:
    if src_file is not None:
        infile_slug = os.path.basename(src_file).split('.')[0]
    else:
        infile_slug = 'helloworld'
    fname_slug = '%s.html' % infile_slug
    output_file = os.path.join(tgt_dir, 'tutorials', fname_slug)
    if not os.path.exists(output_file):
        raise RuntimeError('File generation failed')
    print('Output file generated: %s' % output_file)

    # Open or print file:
    if open_html is True:
        if _platform == "linux" or _platform == "linux2":
            if assert_firefox():
                open_command = 'firefox %s' % output_file
            else:
                raise NotImplementedError
        elif _platform == "darwin":
            open_command = 'open %s' % output_file
        elif _platform == "win32":
            raise NotImplementedError
        elif _platform == "win64":
            raise NotImplementedError
        else:
            raise NotImplementedError
        subprocess.call(open_command, shell=True)

    else:

        pass

    return 0
