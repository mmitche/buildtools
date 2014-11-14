import logging as log
import sys
import getopt
import os
import subprocess
import shutil

target = ""
arch = ""
platform = ""
workspace = ""
builddir = ""

def Initialize():
    print "Initializing Workspace"
    global workspace
    workspace = os.environ['WORKSPACE']
    if platform == "windows":
        # Jenkins puts quotes in the path, which is wrong. Remove quotes.
        os.environ['PATH'] = os.environ['PATH'].replace('"','')

    return 0

def ParseArgs(argv):
    print "Parsing arguments for compile"
    try:
        opts, args = getopt.getopt(argv, "t:p:a:v", ["target=", "platform=", "arch=", "verbose"])
    except getopt.GetoptError:
        print "ERROR: \n\t usage: python compile.py --target <target> --platform <windows|linux> --arch <arch> [--verbose]"
        return 2

    verbose = False

    acceptedPlatforms = ['windows','linux']

    for opt, arg in opts:
        if opt in ("-t", "--target"):
            global target
            target = arg
        elif opt in ("-p", "--platform"):
            global platform
            if arg.lower() not in acceptedPlatforms:
                print "ERROR: " + arg + "not an accepted platform. Use windows or linux."
                sys.exit(2)
            platform = arg.lower()
        elif opt in ("-a", "--arch"):
            global arch
            arch = arg
        elif opt in ("-v", "--verbose"):
            verbose = True

    if verbose:
        log.basicConfig(format="%(levelname)s: %(message)s", level=log.DEBUG)
        log.info("In verbose mode.")
    else:
        log.basicConfig(format="%(levelname)s: %(message)s")

    if target == "" or platform == "" or arch == "":
        # must specify target, project and arch
        log.error("Must specify target, project and arch")
        return 2

    return 0

def SetupDirectories():
    log.info("Setting up directories for cmake")

    if not os.path.isdir("build"):
        os.mkdir("build")
    os.chdir("build")

    global builddir
    builddir = "build-" + platform

    if platform == "windows":
        builddir = builddir + "-" + arch + "-" + target

    if os.path.isdir(builddir):
        shutil.rmtree(builddir)
    os.mkdir(builddir)
    os.chdir(builddir)

    return 0

def RunCMake():
    # run CMake
    print "\n==================================================\n"

    returncode = 0
    if platform == "windows":
        print "Running: " + workspace + "\ProjectK\NDP\unix\\tools\gen-buildsys-win.bat " + workspace + "\ProjectK\NDP"
        print "\n==================================================\n"
        sys.stdout.flush()
        returncode = subprocess.call([workspace + "\ProjectK\NDP\unix\\tools\gen-buildsys-win.bat", workspace + "\ProjectK\NDP"])
    elif platform == "linux":
        print "Running: " + workspace + "\ProjectK\NDP\unix\\tools\gen-buildsys-clang.sh " + workspace + "\ProjectK\NDP DEBUG"
        print "\n==================================================\n"
        sys.stdout.flush()
        returncode = subprocess.call([workspace + "\ProjectK\NDP\unix\\tools\gen-buildsys-clang.sh", workspace + "\ProjectK\NDP", "DEBUG"])

    if returncode != 0:
        print "ERROR: cmake failed with exit code " + str(returncode)

    return returncode

def RunBuild():
    if platform == "windows":
        return RunMsBuild()
    elif platform == "linux":
        return RunMake()

def RunMsBuild():
    # run MsBuild
    print "\n==================================================\n"
    print "Running: vcvarsall.bat x86 && msbuild ProjectK.sln /p:Configuration=" + target + " /p:Platform=" + arch + " /t:ALL_BUILD"
    print "\n==================================================\n"
    sys.stdout.flush()
    
    returncode = subprocess.call(["vcvarsall.bat","x86","&&","msbuild","ProjectK.sln","/p:Configuration=" + target,"/p:Platform=" + arch])
    
    if returncode != 0:
        print "ERROR: vcvarsall.bat failed with exit code " + str(returncode)
    
    return returncode

def RunMake():
    print "\n==================================================\n"
    print "Running: make"
    print "\n==================================================\n"
    sys.stdout.flush()
    returncode = subprocess.call(["make"])

    if returncode != 0:
        print "ERROR: make failed with exit code " + str(returncode)

    return returncode

def CopyBinaries():
    print "\n==================================================\n"
    print "Stub for copying binaries"
    print "\n==================================================\n"

    return 0

def Cleanup():
    print "\n==================================================\n"
    print "Cleaning Up."
    print "\n==================================================\n"
    
    os.chdir("..")
    shutil.rmtree(builddir)
    os.chdir("..")
    shutil.rmtree("build")
    log.shutdown()
    return 0

def main(argv):
    returncode = ParseArgs(argv)
    if returncode != 0:
        return returncode
    
    returncode += Initialize()
    if returncode != 0:
        return returncode
    
    returncode += SetupDirectories()
    if returncode != 0:
        return returncode
    
    returncode += RunCMake()
    if returncode != 0:
        return returncode
    
    returncode += RunBuild()
    if returncode != 0:
        return returncode
    
    returncode += CopyBinaries()
    if returncode != 0:
        return returncode
    
    # returncode += Cleanup()
    return returncode

if __name__ == "__main__":
    returncode = main(sys.argv[1:])

    Cleanup()

    sys.exit(returncode)

