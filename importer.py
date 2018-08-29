import configparser
import os
import shutil
import sys
from shutil import rmtree
from subprocess import Popen, PIPE
from time import sleep
from fcntl import fcntl, F_GETFL, F_SETFL
from textwrap import dedent

config = configparser.ConfigParser()
config.read("config.ini")


def print_help_and_exit():
    help_text = dedent("""
    Usage: python3 importer.py <task> [<student>] [<exercise>]

    TASKS:

    help        Prints this.
    import      Imports students solution and tests for the exercise into "working". Requires student and exercise!
    update      Updates tests from tests repository. Will not update tests already in "working".
    clean       Cleans the "working" directory, existing student sources and tests.
    test        Runs tests in "working" directory.

    Feel free to make pull requests and create issues: github.com/jkymmel/student_code_importer
    """)[1:]
    print(help_text)
    exit(0)


def update_tests():
    if os.path.isdir("tests"):
        print("Found existing local tests reporitory, pulling...")
        p = Popen(["git", "--git-dir=tests/.git", "pull", "origin", "master"],
                  stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=False)
        flags = fcntl(p.stdout, F_GETFL)
        fcntl(p.stdout, F_SETFL, flags | os.O_NONBLOCK)
        while True:
            try:
                out = os.read(p.stdout.fileno(), 1024)
                if out != b'':
                    print(out)
            except OSError:
                print("Pull complete!")
                break
    else:
        print("No local tests repository found, cloning...")
        p = Popen(["git", "clone", config["TESTS"]["REPOSITORY"], "tests"],
                  stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=False)
        flags = fcntl(p.stdout, F_GETFL)
        fcntl(p.stdout, F_SETFL, flags | os.O_NONBLOCK)
        while True:
            try:
                out = os.read(p.stdout.fileno(), 1024)
                if out != b'':
                    print(out)
            except OSError:
                print("Cloning complete!")
                break


def import_solution_and_tests():
    try:
        student = sys.argv[2]
        exercise = sys.argv[3]
    except IndexError:
        print_help_and_exit()
        student = None
        exercise = None

    if not os.path.isdir("tests"):
        print("Tests are missing, retrieving tests...")
        update_tests()
        print("Tests retrieved!")

    print("Retrieving sources of " + student + "...")
    get_students_repository(student)
    print("Student's sources retrieved!")

    if os.path.isdir("working"):
        print("Cleaning old \"working\" directory...")
        rmtree("working")
        os.makedirs("working")
        print("Cleaned \"working\"!")

    sleep(1)  # HACKS!
    if not os.path.isdir("tests/" + exercise):
        print("Tests for " + exercise + " not found!")
        exit(0)
    if not os.path.isdir("student_sources/" + exercise):
        print("Student's solution for " + exercise + " not found!")
        exit(0)

    print("Copying student's solution for " + exercise + "...")
    shutil.copytree("student_sources/" + exercise, "working/src")
    print("Student's solution for " + exercise + " copied!")
    print("Copying tests for " + exercise + "...")
    shutil.copytree("tests/" + exercise, "working/tests")
    print("Tests for " + exercise + " copied!")
    print("\nFINISHED!")
    print("\nCheck \"working\" directory!")


def clean():
    if os.path.isdir("student_sources"):
        print("Removing student's sources...")
        rmtree("student_sources")
        print("Student's sources removed!")
    if os.path.isdir("tests"):
        print("Removing tests...")
        rmtree("tests")
        print("Tests removed!")
    if os.path.isdir("working"):
        print("Removing \"working\" directory...")
        rmtree("working")
        print("\"working\" removed!")
    print("\nCLEANED!")


def run_tests():
    task = Popen(["pytest", "working/"])
    task.wait()


def get_students_repository(student):
    if os.path.isdir("student_sources"):
        print("Removing old student's sources...")
        rmtree("student_sources")
        print("Old sources removed!")
    print("Cloning new sources...")
    p = Popen(["git", "clone", str(config["STUDENTS"]["REPOSITORY"]).replace("$STUDENT$", student), "student_sources"],
              stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=False)
    flags = fcntl(p.stdout, F_GETFL)
    fcntl(p.stdout, F_SETFL, flags | os.O_NONBLOCK)
    while True:
        try:
            out = os.read(p.stdout.fileno(), 1024)
            if out != b'':
                print(out)
        except OSError:
            print("Cloning complete!")
            break


if __name__ == '__main__':
    try:
        task = sys.argv[1]
    except IndexError:
        task = None

    if task == "update":
        update_tests()
    elif task == "import":
        import_solution_and_tests()
    elif task == "clean":
        clean()
    elif task == "test":
        run_tests()
    else:
        print_help_and_exit()
