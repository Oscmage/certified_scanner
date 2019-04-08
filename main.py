import sys
import os
import pprint

from modulefinder import ModuleFinder


def main(args):

    # Check input.
    ok, file_path, dir_path = input_ok(args)
    if not ok:
        return

    # Get all subdirectories and add them to sys.path to not get any missing modules.
    path = get_path(dir_path)

    # Create modulefinder and run it
    finder = ModuleFinder(path)
    finder.run_script(file_path)

    # Make a dict of packages that are certified
    cert_package_set = get_certified_packages(finder, dir_path)

    check_certified(finder, cert_package_set)


def check_certified(finder, cert_package_set):
    all_good = True
    pp = pprint.PrettyPrinter(indent=2)

    # Check if there were modules that modulefinder could not resolve.
    not_found_modules = finder.any_missing()

    if len(not_found_modules) != 0:
        all_good = False
        print(
            bcolors.get_red_color_string(
                "The following modules were not found by modulefinder which means you can not trust this result"
            )
        )
        pp.pprint(not_found_modules)

    # No matter if we resolved modules above it might be interesting to see which ones were ok and which was not.
    ok_files, not_certified_files = _check_certified(finder, cert_package_set)
    if len(not_certified_files) != 0:
        all_good = False
        print(
            bcolors.get_red_color_string(
                "The following modules are NOT certified but imported by something certified"
            )
        )
        pp.pprint(not_certified_files)

    if ok_files:
        print(bcolors.get_green_color_string("The following files are certified and ok:"))
        pp.pprint(ok_files)

    if all_good:
        print("All good!")


def _check_certified(finder, cert_package_set):
    ok_files = []
    not_certified_files = []
    for name, mod in finder.modules.items():
        file_path = mod.__file__

        # There might be modules that ModuleFinder could not resolve
        if file_path:
            file_dir = get_directory(file_path)
            if file_dir not in cert_package_set:
                # Not certified but imported, append to non_certified_list
                not_certified_files.append(os.path.realpath(file_path))
            else:
                # Append files that are ok files (they are certified)
                ok_files.append(os.path.realpath(file_path))
    return ok_files, not_certified_files


def get_certified_packages(finder, dir_path):
    cert_package_set = set()
    cert_package_set.add(dir_path)

    for name, mod in finder.modules.items():
        file_path = mod.__file__
        if file_path and '__init__.py' in file_path:
            certified = check_if_certified(file_path)
            if certified:
                package_dir = get_directory(file_path)
                cert_package_set.add(package_dir)

    return cert_package_set


def input_ok(args):
    if len(args) != 2:
        print("Expecting two argument, file path followed by directory")
        return False

    file_path = args[0]
    dir_path = args[1]

    if not os.path.isfile(file_path):
        print("Not a file, pass me something real.")
        return False

    if not file_path.endswith('.py'):
        print("Cmon, keep it real, give me a python file")
        return False

    if not os.path.isdir(dir_path):
        print("Invalid directory")
        return False

    file_path = os.path.realpath(file_path)
    dir_path = os.path.dirname(dir_path)

    return True, file_path, dir_path


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


def get_directory(file_path):
    last_slash_index = file_path.rfind('/')
    return file_path[0:last_slash_index]


# TODO(Ugly, change)
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
