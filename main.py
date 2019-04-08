import sys
import os


from modulefinder import ModuleFinder


def main(args):
    if len(args) != 1:
        print("Expect one argument, file path")
    file_path = args[0]
    if not input_ok(file_path):
        return
    file_path = os.path.realpath(file_path)

    dir_path = os.path.dirname(file_path)
    # print(dir_path)
    # Get all subdirectories and add them to sys.path to not get any missing modules.
    path = get_path()
    finder = ModuleFinder(path)
    finder.run_script(file_path)

    cert_package_set = set()
    cert_package_set.add(dir_path)
    # Make a dict of packages that are certified
    for name, mod in finder.modules.items():
        file_path = mod.__file__
        if file_path and '__init__.py' in file_path:
            certified = check_if_certified(file_path)
            if certified:
                last_slash_index = file_path.rfind('/')
                package_dir = file_path[0:last_slash_index]
                cert_package_set.add(package_dir)

    all_good = True
    for name, mod in finder.modules.items():
        file_path = mod.__file__
        if file_path:
            last_slash_index = file_path.rfind('/')
            file_dir = file_path[0:last_slash_index]

            if file_dir not in cert_package_set:
                all_good = False
                print(
                    bcolors.get_colored_string(file_path)
                    + " is imported by a certified module but not certified"
                )
    if all_good:
        print("All clear")


def input_ok(file_path):
    if not os.path.isfile(file_path):
        print("Not a file, pass me something real.")
        return False

    if not file_path.endswith('.py'):
        print("Cmon, keep it real, give me a python file")
        return False
    return True


def check_if_certified(file_path):
    with open(file_path) as f:
        for line in f.readlines():
            if 'certified=True' in line.replace(" ", ""):
                return True
    return False


def get_path():
    cwd = os.getcwd()
    path = sys.path

    for i, j, y in os.walk(cwd):
        path.append(i)

    return path


class bcolors:
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def get_colored_string(text):
        return bcolors.FAIL + text + bcolors.ENDC


if __name__ == '__main__':
    main(sys.argv[1:])
