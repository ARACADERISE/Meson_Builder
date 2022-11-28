import os
import sys
import subprocess

REQUIRED_DIRS = ['builddir', 'compile']
REQUIRED_FILES = ['meson.build']

# Error
def error(msg):
    print(msg)
    sys.exit(1)

class MesonBuilder:
    def __init__(self):
        # False by default assuming user setup meson correctly
        # If one file or the other are missing, the existing one is removed
        self.dirs_needed = False

        # Project name(passed via sys.argv)
        self.project_name = os.path.split(os.getcwd())[1]

        # Language
        self.project_language = None

        # Dependencies
        self.deps = []

        # Executable name
        self.project_exe_name = None

        # File to compile
        self.project_file = None

    def check_dirs(self):
        for i in range(len(REQUIRED_DIRS)):
            if not os.path.isdir(REQUIRED_DIRS[i]) and i == len(REQUIRED_DIRS)-1:
                self.dirs_needed = True

    def parse_args(self):
        if len(sys.argv) == 1 and self.dirs_needed == True:
            exit(f"\u001b[33;1m{REQUIRED_DIRS[0]}\u001b[37;1m and \u001b[33;1m{REQUIRED_DIRS[1]}\u001b[37;1m were not found.\n\tPass -pname project_name, -pfile project_source_file\n")

        if self.dirs_needed == True:
            for i in range(len(sys.argv)):
                if sys.argv[i] == '-pname':
                    i += 1
                    self.project_name = sys.argv[i]
                    continue
                if sys.argv[i] == '-pfile':
                    i += 1
                    self.project_file = sys.argv[i]
                    self.project_exe_name = self.project_file[0:len(self.project_file)-2]
                    continue
                if sys.argv[i] == '-plang':
                    i += 1
                    self.project_language = sys.argv[i]
                    continue

            if self.project_name == None or self.project_exe_name == None:
                exit(f"Expected \u001b[33;1m-pname project_name\u001b[37;1m and \u001b[33;1m-pfile project_source_file\u001b[37;1m\n")

            if self.project_language == None:
                self.project_language = self.project_file[len(self.project_file)-1]

    def init_meson_build_file(self):
        f = open('meson.build', 'w')

        project = f"project('{self.project_name}', '{self.project_language}')"
        exe = f"\nexecutable('demo', '{self.project_file}')\n"

        f.write(project)
        f.write(exe)
        f.close()

    def init_builddir(self):
        os.system('meson setup builddir')
        os.system('cd builddir && ninja')

builder = MesonBuilder()
builder.check_dirs()
builder.parse_args()
builder.init_meson_build_file()
builder.init_builddir()
