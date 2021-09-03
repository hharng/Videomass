#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Name: pyinstaller_setup.py
Porpose: Setup the videomass building with pyinstaller
Compatibility: Python3
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: (c) 2020-2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Sept.02.2021
########################################################

This file is part of Videomass.

    Videomass is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Videomass is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Videomass.  If not, see <http://www.gnu.org/licenses/>.
"""
import os
import sys
import shutil
import platform
import argparse
# import subprocess

this = os.path.realpath(os.path.abspath(__file__))
HERE = os.path.dirname(os.path.dirname(os.path.dirname(this)))
BINARY = os.path.join(HERE, 'bin', 'videomass')
sys.path.insert(0, HERE)
try:
    from videomass3.vdms_sys.msg_info import current_release
except ModuleNotFoundError as error:
    sys.exit(error)


def data(here=HERE):
    """
    Returns a dict object on the Videomass data
    """
    release = current_release()  # Gets data list

    return dict(RLS_NAME=release[0],  # first letter is Uppercase
                PRG_NAME=release[1],  # first letter is lower
                VERSION=release[2],
                RELEASE=release[3],
                COPYRIGHT=release[4],
                WEBSITE=release[5],
                AUTHOR=release[6],
                EMAIL=release[7],
                COMMENT=release[8],
                ART=os.path.join(here, 'videomass3', 'art'),
                LOCALE=os.path.join(here, 'videomass3', 'locale'),
                SHARE=os.path.join(here, 'videomass3', 'share'),
                FFMPEG=os.path.join(here, 'videomass3', 'FFMPEG'),
                NOTICE=os.path.join(here, 'videomass3',
                                    'FFMPEG', 'NOTICE.rtf'),
                AUTH=os.path.join(here, 'AUTHORS'),
                BUGS=os.path.join(here, 'BUGS'),
                CHANGELOG=os.path.join(here, 'CHANGELOG'),
                COPYING=os.path.join(here, 'LICENSE'),
                INSTALL=os.path.join(here, 'INSTALL'),
                README=os.path.join(here, 'README.md'),
                TODO=os.path.join(here, 'TODO'),
                ICNS=os.path.join(here, 'videomass3',
                                  'art', 'videomass.icns'),
                ICO=os.path.join(here, 'videomass3', 'art', 'videomass.ico'),
                )


class MakePyinstallerBuild():
    """
    Wrap the pyinstaller building for Videomass

    """

    def __init__(self, onedf='--onedir'):
        """
        """
        self.onedf = onedf
        typeadd = 'coll' if self.onedf == '--onedir' else 'exe'
        getdata = data()
        datas = (f"--add-data {getdata['ART']}:art "
                 f"--add-data {getdata['LOCALE']}:locale "
                 f"--add-data {getdata['SHARE']}:share "
                 f"--add-data {getdata['FFMPEG']}:FFMPEG "
                 f"--add-data {getdata['AUTH']}:DOC "
                 f"--add-data {getdata['BUGS']}:DOC "
                 f"--add-data {getdata['CHANGELOG']}:DOC "
                 f"--add-data {getdata['COPYING']}:DOC "
                 f"--add-data {getdata['INSTALL']}:DOC "
                 f"--add-data {getdata['README']}:DOC "
                 f"--add-data {getdata['TODO']}:DOC videomass "
                 )

        self.linuxspec = (f"--name {getdata['PRG_NAME']} {onedf} --windowed "
                          f"--noconsole --exclude-module youtube_dl {datas} "
                          f"videomass ")

        self.darwinspec = (f"--name {getdata['RLS_NAME']} {onedf} --windowed "
                           f"--noconsole --icon {getdata['ICNS']} "
                           f"--osx-bundle-identifier com.jeanslack.videomass "
                           # f"--codesign-identity IDENTITY "
                           # f"--osx-entitlements-file FILENAME "
                           f"--exclude-module youtube_dl "
                           f"--add-data {datas}  videomass "
                           )

        self.additional_darwinspec = (f"""app = BUNDLE({typeadd},
             name='{getdata['RLS_NAME']}.app',
             icon='{getdata['ICNS']}',
             bundle_identifier='com.jeanslack.videomass',
             info_plist={{# 'LSEnvironment': '$0',
                    'NSPrincipalClass': 'NSApplication',
                    'NSAppleScriptEnabled': False,
                    'CFBundleName': '{getdata['RLS_NAME']}',
                    'CFBundleDisplayName': '{getdata['RLS_NAME']}',
                    'CFBundleGetInfoString': "Making {getdata['RLS_NAME']}",
                    'CFBundleIdentifier': "com.jeanslack.videomass",
                    'CFBundleVersion': '{getdata['VERSION']}',
                    'CFBundleShortVersionString': '{getdata['VERSION']}',
                    'NSHumanReadableCopyright':
                                        'Copyright {getdata['COPYRIGHT']}, '
                                        'Gianluca Pernigotto, '
                                        'All Rights Reserved',}})
""")
        self.winspec = (f"--name {getdata['RLS_NAME']} {onedf} --windowed "
                        f"--noconsole --icon {getdata['ICO']} "
                        f"--exclude-module youtube_dl {datas} videomass "
                        )
    # --------------------------------------------------------#

    def check(self, binary=BINARY, here=HERE):
        """
        Checks the required files
        """
        if not os.path.exists(os.path.join(here, 'videomass')):  # binary
            if os.path.isfile(binary):
                try:
                    shutil.copyfile(binary, os.path.join(here, 'videomass'))
                except FileNotFoundError as err:
                    sys.exit(err)
            else:
                sys.exit("ERROR: no 'bin/videomass' file found on videomass "
                         "base sources directory.")
    # --------------------------------------------------------#

    def clean_buildingdir(self, here=HERE):
        """
        asks the user if they want to clean-up building directories.

        """

        clean = input('Want you remove "dist" and "build" folders '
                      'before building? (y/n) ')
        if clean in ('y', 'Y'):
            if os.path.exists(os.path.join(here, 'dist')):
                try:
                    shutil.rmtree(os.path.join(here, 'dist'))
                except OSError as err:
                    sys.exit("ERROR: %s" % (err.strerror))

            if os.path.exists(os.path.join(here, 'build')):
                try:
                    shutil.rmtree(os.path.join(here, 'build'))
                except OSError as err:
                    sys.exit("ERROR: %s" % (err.strerror))
    # ---------------------------------------------------------#

    def genspec(self, here=HERE):
        """
        Generate a videomass.spec file for the specified platform.
        Support for the following platforms is expected:

            [Windows, Darwin, Linux]

        The videomass.spec file will be saved in the root directory
        of the videomass sources. To running videomass.spec is required
        ``pyinstaller``.

        To use videomass.spec type:

            `pyinstaller videomass.spec`

        or use this script with option -s to start the building by
        an existing videomass.spec file.
        """

        if platform.system() == 'Windows':
            options = self.winspec
            specfile = os.path.join(here, 'Videomass.spec')

        elif platform.system() == 'Darwin':
            options = self.darwinspec
            specfile = os.path.join(here, 'Videomass.spec')

        elif platform.system() == 'Linux':
            options = self.linuxspec
            specfile = os.path.join(here, 'videomass.spec')

        else:
            sys.exit("Unsupported platform. You create a spec file "
                     "using this command:\n"
                     "   pyi-makespec options videomass.py\n")

        # FIXME replace os.system with subprocess

        # cmd = subprocess.run(['pyi-makespec', '%s' % options, 'videomass'])
        # if not cmd.returncode == 0:
            # sys.exit('ERROR: -------------')

        os.system("pyi-makespec %s videomass" % options)

        if platform.system() == 'Darwin':
            with open(specfile, 'a', encoding='utf8') as specf:
                specf.write('%s' % self.additional_darwinspec)
    # --------------------------------------------------------#

    def run_pyinst(self, here=HERE):
        """
        wrap `pyinstaller videomass.spec`

        """
        if platform.system() == 'Windows':
            specfile = os.path.join(here, 'Videomass.spec')

        elif platform.system() == 'Darwin':
            specfile = os.path.join(here, 'Videomass.spec')

        elif platform.system() == 'Linux':
            specfile = os.path.join(here, 'videomass.spec')

        print(here, '\n', specfile)
        return

        # FIXME replace os.system with subprocess
        if os.path.exists(specfile) and os.path.isfile(specfile):
            os.system("pyinstaller --clean %s" % specfile)
            print("\npyinstaller_setup.py: Build finished.\n")
        else:
            sys.exit("ERROR: no such file %s" % specfile)
    # --------------------------------------------------------#


def make_portable(here=HERE, ):
    """
    Optionally, you can create a portable_data folder for Videomass
    stand-alone executable to keep all application data inside
    the program folder.
    Note:
       with `--onedir` option, the 'portable_data' directory should
       be inside the videomass directory.

        with `--onefile` option, the 'portable_data' directory should
        be next to the videomass directory.
    """
    portable = input('Do you want to keep all application data inside '
                     'the program folder? (makes stand-alone executable '
                     'fully portable and stealth) (y/n) ')
    if portable in ('y', 'Y'):
        portabledir = 'portable_data'
    else:
        return

    def makedir(datashare):
        """
        make portable_data folder
        """
        if not os.path.exists(datashare):
            try:
                os.mkdir(datashare)
            except OSError as err:
                sys.exit('ERROR: %s' % err)
            else:
                sys.exit('\nSUCCESS: "portable_data" folder is created\n')
        else:
            sys.exit('INFO: "portable_data" folder already exists')

    if platform.system() == 'Windows':
        if self.onedf == '--onefile':
            datashare = os.path.join(here, 'dist', portabledir)
        else:
            datashare = os.path.join(here, 'dist', 'Videomass',
                                     'videomass3', portabledir)

    elif platform.system() == 'Darwin':
        if self.onedf == '--onefile':
            datashare = os.path.join(here, 'dist', portabledir)
        else:
            datashare = os.path.join(here, 'dist', 'Videomass.app',
                                     'MacOS', portabledir)
    else:
        if self.onedf == '--onefile':
            datashare = os.path.join(here, 'dist', portabledir)
        else:
            datashare = os.path.join(here, 'dist', 'videomass', portabledir)

    makedir(datashare)
# --------------------------------------------------------#


def onefile_onedir():
    """
    Pyinstaller offer two options to generate stand-alone executables.
    The `--onedir` option is the default.
    """
    onedf = input('\nChoose from the following options:\n'
                  '[1] Create a one-folder bundle containing an '
                  'executable (default)\n'
                  '[2] Create a one-file bundled executable\n'
                  '(1/2) ')
    if onedf == '1':
        onedf = '--onedir'
    elif onedf == '2':
        onedf = '--onefile'
    else:
        onedf = '--onedir'

    return onedf
# --------------------------------------------------------#


def main(here=HERE):
    """
    Users inputs parser (positional/optional arguments)
    """
    parser = argparse.ArgumentParser(
        description='Wrap the pyinstaller setup for Videomass',)
    parser.add_argument(
        '-g', '--gen_spec',
        help="Generate a videomass.spec file to start building with.",
        action="store_true",
    )
    parser.add_argument(
        '-gb', '--genspec_build',
        help="Generate a videomass.spec file and start directly "
        "with building.",
        action="store_true",
    )
    parser.add_argument(
        '-s', '--start_build',
        help="Start the building by an existing videomass.spec file.",
        action="store_true",
    )
    args = parser.parse_args()

    if args.gen_spec:
        onedf = onefile_onedir()
        wrap = MakePyinstallerBuild(onedf)
        wrap.check()
        wrap.genspec()

    elif args.genspec_build:
        onedf = onefile_onedir()
        wrap = MakePyinstallerBuild(onedf)
        wrap.check()
        wrap.clean_buildingdir()
        wrap.genspec()
        wrap.run_pyinst()
        make_portable()

    elif args.start_build:
        wrap = MakePyinstallerBuild(None)
        wrap.check()
        wrap.clean_buildingdir()
        wrap.run_pyinst(os.path.join(here, 'videomass.spec'))
        make_portable()

    else:
        print("\nType 'pyinstaller_setup.py -h' for help.\n")
        return


if __name__ == '__main__':
    main()
