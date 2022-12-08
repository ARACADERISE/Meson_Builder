import os
import sys
import subprocess
from pathlib import Path

REQUIRED_DIRS = ['builddir', 'compile']
REQUIRED_FILES = ['meson.build']

# Paths
GCC_INCLUDE_PATH = "/usr/lib/gcc/x86_64-linux-gnu/9/include" if os.path.isdir("/usr/lib/gcc/x86_64-linux-gnu/9/include") else "/lib/gcc/x86_64-linux-gnu/9/include/"
CLANG_INCLUDE_PATH = "/usr/lib/clang/10/include"

if not os.path.isdir(GCC_INCLUDE_PATH):
    print('Making sure gcc is purged, then reinstalling')
    subprocess.run('sudo purge gcc', shell=True, cwd=os.getcwd())
    subprocess.run('sudo apt-get install build-essential', shell=True, cwd=os.getcwd())

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
        self.dep_name = None

        # Executable name
        self.project_exe_name = None

        # File to compile
        self.project_file = None

        # Append header files to standard includes of gcc, or clang
        self.append_gcc_standard_includes = []
        self.append_clang_standard_includes = []

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
                if sys.argv[i] == '-pdeps':
                    i += 1
                    a = sys.argv[i].split(',')
                    self.dep_name = a[0]
                    del a[0]
                    self.deps = a
                    continue
                if sys.argv[i] == '-append_gcc':
                    i += 1
                    self.append_gcc_standard_includes = sys.argv[i]
                    
                    if ',' in self.append_gcc_standard_includes:
                        # If the header files to be moved to the standard includes of gcc, or clang, are separated by commas
                        # we want to make sure we get each header file
                        self.append_gcc_standard_includes = self.append_gcc_standard_includes.split(',')
                    else:
                        # Just make it a list by itself lol
                        self.append_gcc_standard_includes = [self.append_gcc_standard_includes]

                    for i in self.append_gcc_standard_includes:
                        if not '.h' in i:
                            exit(f"{i} is not a header file.")
                        if not os.path.isfile(i):
                            exit(f"The header file {i} does not exist.")
                        else:
                            subprocess.run(f'sudo mv {i} {GCC_INCLUDE_PATH}', shell=True, cwd=os.getcwd())
                            print(f'Moved {i} into /lib/gcc/x86_64-linux-gnu/9/include/')
                            subprocess.run(f'whereis {i}.h', shell=True, cwd=os.getcwd())

                    continue


            if self.project_name == None or self.project_exe_name == None:
                exit(f"Expected \u001b[33;1m-pname project_name\u001b[37;1m and \u001b[33;1m-pfile project_source_file\u001b[37;1m\n")

            if self.project_language == None:
                self.project_language = self.project_file[len(self.project_file)-1]

            if not self.project_name == os.path.split(os.getcwd())[1]:
                exit(f'The path \u001b[33;1m{Path.home()}/{self.project_name}\u001b[37;1m does not exist.\n')
    
    def init_meson_build_file(self):
        if not os.path.isfile('meson.build'):
            f = open('meson.build', 'w')

            project = f"project('{self.project_name}', '{self.project_language}')"
            exe = f"\nexecutable('demo', '{self.project_file}')\n"

            f.write(project)
            if len(self.deps) > 0:
                if len(self.deps) == 1:
                    print(f"{self.dep_name} = [{self.deps[i] for i in range(len(self.deps))}]")
                if len(self.deps) > 1:
                    f.write(f"\n{self.dep_name} = [")
                    for i in range(len(self.deps)):
                        if not i == len(self.deps) - 1:
                            f.write("dependency('"+self.deps[i]+"'),")
                        else:
                            f.write("dependency('"+self.deps[i]+"')")
                    f.write(']\n')
            f.write(exe)
            f.close()

    def init_builddir(self):
        print(self.dep_name, self.deps)
        subprocess.run('meson setup builddir', shell=True, cwd=os.getcwd())
        subprocess.run('cd builddir && ninja', shell=True, cwd=os.getcwd())
        subprocess.run(f"mv builddir/demo {os.getcwd()}/ && rm -rf builddir && ls", shell=True, cwd=os.getcwd())

builder = MesonBuilder()
builder.check_dirs()
builder.parse_args()
builder.init_meson_build_file()
builder.init_builddir()
