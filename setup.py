#!/usr/bin/env python
# -*- coding: utf-8 -*-

#########################################################
# Name: setup.py
# Porpose: script to setup Videomass.
# Compatibility: Python3
# Platform: all
# Writer: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2014-2020 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: Aug.2.2019, Sept.11.2019, Dic.16.2019
# PEP8 compatible
#########################################################

# This file is part of Videomass.

#    Videomass is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    Videomass is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with Videomass.  If not, see <http://www.gnu.org/licenses/>.

#########################################################
"""
 USAGE:

   1) Windows:
      - python3 setup.py py2exe

   2) MacOSX:
      - python3 setup.py py2app --packages==wx

   3) All
      - python3 setup.py sdist bdist_wheel

 * See the INSTALL file in the sources for major details

"""

# ---- Imports ----#
from distutils.core import setup
from setuptools import setup, find_packages
import platform
from glob import glob
import os
import sys
import shutil

# ---- Version Check(s) ----#
if sys.version_info[0] == 3:
    from videomass3.vdms_SYS.msg_info import current_release
    from videomass3.vdms_SYS.msg_info import descriptions_release

    if platform.system() in ['Windows', 'Darwin']:
        EXCLUDE = []
        REQUIRES = ['wxpython>=4.0.3"', 'PyPubSub>=4.0.0']
    else:
        EXCLUDE = []
        REQUIRES = ['PyPubSub>=4.0.0']
else:
    sys.stderr.write(
                    "ERROR: Python3 is required.\n"
                    "Since version 1.6.1 videomass is compatible only "
                    "with Python3.\nYou are using Python version %s\n" % 
                    sys.version[0]
                         )
    sys.exit(1)
try:
    import wx
except ImportError:
    if 'bdist_wheel' not in sys.argv:  # with py2app and py2exe only
        sys.stderr.write("ERROR: 'wx' module is required; "
                         "need wxPython4 (phoenix).\n"
                         "Visit the wxPython web page for more info:\n"
                         "<https://wxpython.org/>\n"
                            )
        sys.exit(1)

# ---- current work directory path ----#
PWD = os.getcwd()

# ---- Get info data ----#
cr = current_release()
RLS_NAME = cr[0]  # release name first letter is Uppercase
PRG_NAME = cr[1]
VERSION = cr[2]
RELEASE = cr[3]
COPYRIGHT = cr[4]
WEBSITE = cr[5]
AUTHOR = cr[6]
EMAIL = cr[7]
COMMENT = cr[8]

dr = descriptions_release()
LICENSE = dr[2]  # short license
DESCRIPTION = dr[0]
LONG_DESCRIPTION = dr[1]

# ---- categorize with ----#
CLASSIFIERS = [
            'Development Status :: 5 - Production/Stable',
            'Operating System :: MacOS',
            'Operating System :: Microsoft :: Windows :: Windows 7',
            'Operating System :: Microsoft :: Windows :: Windows 8',
            'Operating System :: Microsoft :: Windows :: Windows 10',
            'Operating System :: POSIX :: BSD :: FreeBSD',
            'Operating System :: POSIX :: Linux',
            'Environment :: Win32 (MS Windows)',
            'Environment :: X11 Applications :: GTK',
            'Intended Audience :: End Users/Desktop',
            'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
            'Natural Language :: English',
            'Natural Language :: Italian',
            'Operating System :: MacOS :: MacOS X',
            'Operating System :: Microsoft :: Windows',
            'Operating System :: POSIX',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Topic :: Multimedia :: Video :: Conversion',
            'Topic :: Multimedia :: Sound/Audio :: Conversion',
            'Topic :: Utilities',
                ]
# ---------------------------------------------------------------------#


def glob_files(pattern):
    """
    Useful function for globbing that iterate on a pattern marked
    with wildcard and put it in a objects list
    """
    return [f for f in glob(pattern) if os.path.isfile(f)]
# ---------------------------------------------------------------------#


def AppendPackageFiles(data, baseicons, baselocale):
    """
    Add all icons and all locale files to data list
    """
    # get all icons and icons docs
    for art in os.listdir('art/icons'):
        if art not in ['videomass_wizard.png', 'videomass.png']:
            tmp = "art/icons/" + art
            if os.path.exists(tmp):
                pathdoc = '%s/%s' % (baseicons, art)
                data.append((pathdoc, glob_files('%s/*.md' % tmp)))
                data.append((pathdoc, glob_files('%s/*.txt' % tmp)))
            for size in ['18x18', '24x24', '32x32', '48x48']:
                if os.path.exists(tmp + '/' + size):
                    path = tmp + '/' + size
                    pathsize = '%s/%s/%s' % (baseicons, art, size)
                    data.append((pathsize, glob_files('%s/*.png' % path)))

    # Get the locale files
    for loc_dir in os.listdir("locale"):
        if loc_dir not in ['videomass.pot', 'README', 'make_pot.sh']:
            tmp = "locale/" + loc_dir + "/LC_MESSAGES"
            if os.path.isdir(tmp):
                tmp2 = tmp + "/videomass.mo"
                if os.path.exists(tmp2):
                    data.append((baselocale + tmp, [tmp2]))
    return data
# ---------------------------------------------------------------------#


def SOURCE_BUILD():
    """
    Source/Build distributions

    """
    DATA_FILES = [ # even path must be relative-path
                  ('share/videomass/config/presets', 
                   glob_files('share/presets/*.prst')),
                   ('share/videomass/config', ['share/videomass.conf',
                                               'share/videomassWin32.conf',
                                               'share/README']),
                   ('share/videomass/icons', 
                    glob_files('art/icons/*.png')),
                   ('share/applications', ['art/videomass.icns',
                                           'art/videomass.ico',
                                           'art/videomass.desktop']),
                   ('share/pixmaps', ['art/icons/videomass.png']),
                   ('share/videomass', ['AUTHORS', 'BUGS',
                                        'CHANGELOG', 'INSTALL',
                                        'COPYING', 'TODO', 'README.md']),
                   ]
    # get the package data
    DATA_FILES = AppendPackageFiles(DATA_FILES,
                                    'share/videomass/icons', 
                                    'share/',
                                    )
    setup(name=PRG_NAME,
          version=VERSION,
          description=DESCRIPTION,
          long_description=open('README.md').read(),
          long_description_content_type='text/markdown',
          author=AUTHOR,
          author_email=EMAIL,
          url=WEBSITE,
          license=LICENSE,
          platforms=["All"],
          packages=find_packages(exclude=EXCLUDE),
          scripts=['bin/videomass'],
          data_files=DATA_FILES,
          classifiers=CLASSIFIERS,
          install_requires=REQUIRES,
          )
# ---------------------------------------------------------------------#


def MacOS():
    """
    build videomass.app

    """
    PATH_ICON = '%s/art/videomass.icns' % PWD
    RESOURCES = "%s/MacOsxSetup/FFMPEG_BIN" % PWD

    # places data ..path must be relative-path
    data = [('share/presets', glob_files('share/presets/*.prst')),
            ('share', ['share/videomass.conf']),
            ('art/icons', glob_files('art/icons/*.png')),
            ('', ['AUTHORS', 'BUGS',
                  'CHANGELOG', 'INSTALL',
                  'COPYING', 'TODO', 'README.md']), ]
    # get package data
    DATA_FILES = AppendPackageFiles(data, 'art/icons/', '')

    OPTIONS = {'argv_emulation': False,
               'excludes': EXCLUDE, #list,
               'includes': ['wx', ],
               'resources': RESOURCES,
               'iconfile': PATH_ICON,
               'site_packages': True,
               'optimize': '2',
               'plist': {
                   # 'LSEnvironment': '$0',
                   'NSPrincipalClass': 'NSApplication',
                   'NSAppleScriptEnabled': False,
                   'CFBundleName': RLS_NAME,
                   'CFBundleDisplayName': RLS_NAME,
                   'CFBundleGetInfoString': "Making Videomass",
                   'CFBundleIdentifier': "com.jeanslack.videomass",
                   'CFBundleVersion': "%s" % VERSION,
                   'CFBundleShortVersionString': "%s" % VERSION,
                   'NSHumanReadableCopyright': "Copyright %s, "
                                            "Gianluca Pernigotto, "
                                            "All Rights Reserved" % COPYRIGHT,
                                            }}

    if not os.path.exists('%s/bin/Videomass.py' % PWD):
        shutil.copyfile('%s/bin/videomass' % PWD,
                        '%s/bin/Videomass.py' % PWD
                        )
    # --------------- setup: --------------------#
    setup(app=['bin/Videomass.py'],
          packages=find_packages(exclude=EXCLUDE),
          include=['python', 'wx', ],
          name=RLS_NAME,
          version=VERSION,
          options={'py2app': OPTIONS},
          description=DESCRIPTION,
          long_description=LONG_DESCRIPTION,
          classifiers=CLASSIFIERS,
          author=AUTHOR,
          author_email=EMAIL,
          url=WEBSITE,
          license=LICENSE,
          data_files=DATA_FILES,
          platforms=['MacOS X'],
          setup_requires=["py2app"],
          )
# ---------------------------------------------------------------------#


def WIN32():
    """
    build videomass.exe

    """
    import py2exe

    if not os.path.exists('%s/bin/Videomass.py' % PWD):
        shutil.copyfile('%s/bin/videomass' % PWD,
                        '%s/bin/Videomass.py' % PWD
                        )

    data = [('share/presets', glob_files('share/presets/*.prst')),
            ('share', glob_files('share/*.conf')),
            ('art/icons', glob_files('art/icons/*.png')),
            ('', ['art/videomass.ico']),
            ('', ['AUTHORS', 'BUGS',
                  'CHANGELOG', 'INSTALL',
                  'COPYING', 'TODO', 'README.md',
                  'Win32Setup/NOTICE.rtf']),
            ('FFMPEG_BIN', glob_files('Win32Setup/FFMPEG_BIN/*')),
            ]
    # get the package data
    DATA_FILES = AppendPackageFiles(data, 'art/icons/', '')

    includes = ["wx.lib.pubsub.*", "wx.lib.pubsub.core.*",
                "wx.lib.pubsub.core.kwargs.*"
                ]
    excludes = [EXCLUDE, '_gtkagg', '_tkagg', 'bsddb', 'curses',
                'email', 'pywin.debugger', 'pywin.debugger.dbgcon',
                'pywin.dialogs', 'tcl', 'Tkconstants', 'Tkinter'
                ]
    packages = find_packages(exclude=EXCLUDE)
    dll_excludes = ['libgdk-win32-2.0-0.dll', 'libgobject-2.0-0.dll',
                    'tcl84.dll', 'tk84.dll'
                    ]
    # --------------- Setup: --------------------#
    setup(options={"py2exe": {"compressed": 2,
                              "optimize": 2,
                              "includes": includes,
                              "excludes": excludes,
                              "packages": packages,
                              "dll_excludes": dll_excludes,
                              "bundle_files": 3,
                              "dist_dir": "dist",
                              "xref": False,
                              "skip_archive": False,
                              "ascii": False,
                              "custom_boot_script": '',
                              }},
          console=[],
          windows=['bin/Videomass.py'],
          data_files=DATA_FILES,
          icon_resources=[(1, "art/videomass.ico")],
          name=RLS_NAME,
          version=VERSION,
          description=DESCRIPTION,
          author=AUTHOR,
          )
# ---------------------------------------------------------------------#

if __name__ == '__main__':
    
    if platform.system() == 'Windows' and 'py2exe' in sys.argv:
        WIN32()
    elif platform.system() == 'Darwin' and 'py2app' in sys.argv:
        MacOS()
    else:
        SOURCE_BUILD()
