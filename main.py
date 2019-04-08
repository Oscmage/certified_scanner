import sys
import os
import pprint

from modulefinder import ModuleFinder


def main(args):
    if len(args) != 2:
        print("Expecting two argument, file path followed by directory")
        return
    file_path = args[0]
    top_directory = args[1]
    if not input_ok(file_path, top_directory):
        return
    file_path = os.path.realpath(file_path)
    dir_path = os.path.dirname(top_directory)
    # print(dir_path)
    # Get all subdirectories and add them to sys.path to not get any missing modules.
    path = get_path(dir_path)
    # print(path)
    finder = ModuleFinder(path)
    finder.run_script(file_path)

    pp = pprint.PrettyPrinter(indent=2)

    # Make a dict of packages that are certified
    cert_package_set = get_certified_packages(finder, dir_path)

    all_good = True
    ok_files = []
    for name, mod in finder.modules.items():
        file_path = mod.__file__
        if file_path:
            last_slash_index = file_path.rfind('/')
            file_dir = file_path[0:last_slash_index]
            if file_dir not in cert_package_set:
                all_good = False
                print(
                    bcolors.get_red_color_string(file_path)
                    + " is imported by a certified module but not certified"
                )
            else:
                ok_files.append(os.path.realpath(file_path))

    not_found_modules = finder.any_missing()
    if len(not_found_modules) != 0:
        all_good = False
        print(
            bcolors.get_red_color_string(
                "The following modules were not found by modulefinder which means you can not trust this result"
            )
        )
        pp.pprint(not_found_modules)

    if ok_files:
        print(bcolors.get_green_color_string("The following files are certified and ok:"))
        pp.pprint(ok_files)

    if all_good:
        print("All clear")


def get_certified_packages(finder, dir_path):
    cert_package_set = set()
    cert_package_set.add(dir_path)

    for name, mod in finder.modules.items():
        file_path = mod.__file__
        if file_path and '__init__.py' in file_path:
            certified = check_if_certified(file_path)
            if certified:
                last_slash_index = file_path.rfind('/')
                package_dir = file_path[0:last_slash_index]
                cert_package_set.add(package_dir)

    return cert_package_set


def input_ok(file_path, top_directory):
    if not os.path.isfile(file_path):
        print("Not a file, pass me something real.")
        return False

    if not file_path.endswith('.py'):
        print("Cmon, keep it real, give me a python file")
        return False

    if not os.path.isdir(top_directory):
        print("Invalid directory")
        return False

    return True


def check_if_certified(file_path):
    with open(file_path) as f:
        for line in f.readlines():
            if 'certified=True' in line.replace(" ", ""):
                return True
    return False


def get_path(file_dir):
    path = sys.path

    for i, j, y in os.walk(file_dir):
        if '__pycache__' not in i:
            path.append(i)

    return path


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    def get_red_color_string(text):
        return bcolors.FAIL + text + bcolors.ENDC

    def get_green_color_string(text):
        return bcolors.OKGREEN + text + bcolors.ENDC


if __name__ == '__main__':
    main(sys.argv[1:])
