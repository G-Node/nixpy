import os
import sys
import re
from subprocess import check_output, call, CalledProcessError
from difflib import Differ
import requests
import json

red_begin = "\033[91m"
red_end = "\033[0m"
bold_begin = "\033[1m"
bold_end = red_end

gitroot = check_output(["git", "rev-parse",
                        "--show-toplevel"]).decode().strip()


def die(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)


def check_git_status():
    ret = call(["git", "diff-index", "--quiet", "HEAD", "--"])
    if ret > 0:
        print("{}There are unstaged changes in the working tree.{}\n"
              "Are you sure you want to continue?".format(
                  red_begin, red_end
              ))
        wait_for_ret()


def chdir():
    scriptpath = sys.argv[0]
    scriptdir = os.path.dirname(scriptpath) or "."
    os.chdir(scriptdir)


def parse_version_string(ver):
    try:
        ver = tuple(map(int, ver.split(".")))
        if len(ver) != 3:
            raise ValueError
        return ver
    except ValueError:
        die("Invalid version string. Please provide a version of the form "
            "X.Y.Z (all integers).")


def wait_for_ret():
    try:
        input("Hit return to continue or ^C to cancel ...")
    except KeyboardInterrupt:
        die("\nCancelled")


def diff_lines(old, new):
    d = Differ()
    diff = list(d.compare(old, new))
    for line in diff[:]:
        if line.startswith(" "):
            diff.remove(line)

    return diff


def update_readme():
    branch = check_output(["git", "rev-parse",
                           "--abbrev-ref", "HEAD"]).decode().strip()
    print("Current branch is '{}'".format(branch))
    wait_for_ret()

    readmefn = os.path.join(gitroot, "README.rst")

    with open(readmefn) as oldreadme:
        oldrmtext = oldreadme.readlines()

    newrmtext = []
    for line in oldrmtext:
        if "travis-ci.org" in line or "coveralls.io" in line:
            line = line.replace("master", branch)
        newrmtext.append(line)

    diff = diff_lines(oldrmtext, newrmtext)

    if not diff:
        print("No changes required in README.")
        wait_for_ret()
        return False

    print("".join(diff))
    print("{}The above changes will be written to README.rst{}".format(
        red_begin, red_end
    ))
    wait_for_ret()
    with open(readmefn, "w") as readme:
        readme.writelines(newrmtext)
    return True


def update_info(newver):

    infofn = os.path.join(gitroot, "nixio/info.py")
    with open(infofn) as infofile:
        oldinfo = infofile.readlines()

    newinfo = []
    for line in oldinfo:
        if line.startswith("VERSION"):
            line = re.sub("'[1-9\.a-z]+'", "'" + newver + "'", line)
        newinfo.append(line)

    diff = diff_lines(oldinfo, newinfo)

    if len(diff) == 0:
        print("No changes required in info.py")
        wait_for_ret()
        return False

    print("".join(diff))
    print("{}The above changes will be written to info.py{}".format(
        red_begin, red_end
    ))
    wait_for_ret()
    with open(infofn, "w") as infofile:
        infofile.writelines(newinfo)
    return True


def update_ci_confs(newver):
    change = False
    nixbranch = ".".join(newver.split(".")[:-1])
    travisfn = os.path.join(gitroot, ".travis.yml")
    with open(travisfn) as travisconf:
        oldconf = travisconf.readlines()

    newconf = []
    for line in oldconf:
        if "NIX_BRANCH" in line:
            line = re.sub("1\.[0-9\.]+[0-9\.a-z]+(dev){0,1}", nixbranch, line)
            line = line.replace("master", nixbranch)
        newconf.append(line)

    diff = diff_lines(oldconf, newconf)

    if len(diff) == 0:
        print("No changes required in .travis.yml")
        wait_for_ret()
    else:
        print("".join(diff))
        print("{}The above changes will be written to .travis.yml{}".format(
            red_begin, red_end
        ))
        wait_for_ret()
        with open(travisfn, "w") as travisconf:
            travisconf.writelines(newconf)
        change = True

    # Appveyor is currently not building NIX so let's not bother changing

    # appveyorfn = os.path.join(gitroot, "appveyor.yml")
    # with open(appveyorfn) as avconf:
    #     oldconf = avconf.readlines()

    # newconf = []
    # for line in oldconf:
    #     if "NIX_VERSION" in line:
    #         line = re.sub("'[1-9\.a-z]+'", "'" + newver + "'", line)
    #     newconf.append(line)

    # diff = diff_lines(oldconf, newconf)

    # if len(diff) == 0:
    #     print("No changes required in appveyor.yml")
    #     wait_for_ret()
    # else:
    #     print("".join(diff))
    #     print("{}The above changes will be written to appveyor.yml{}".format(
    #         red_begin, red_end
    #     ))
    #     wait_for_ret()
    #     with open(appveyorfn, "w") as avconf:
    #         avconf.writelines(newconf)
    #     change = True

    return change


def tag_head(newverstr):
    try:
        tagrev = check_output(["git", "rev-parse", newverstr])
        headrev = check_output(["git", "rev-parse", "HEAD"])
        if tagrev != headrev:
            die("Tag or object named {} already exists "
                "and is not current HEAD.".format(newverstr))
        tagexists = True
    except CalledProcessError:
        tagexists = False

    if tagexists:
        print("HEAD already tagged with {}".format(newverstr))
        return

    print("{}Tagging current commit with '{}'{}".format(
        red_begin, newverstr, red_end))
    print("[{}$ git tag {}{}]".format(red_begin, newverstr, red_end))
    wait_for_ret()
    ret = call(["git", "tag", newverstr])
    if ret > 0:
        die("Error during 'git tag' operation.")


def print_appveyor_urls():
    print("Hit return to print the URLs for the latest wheels on Appveyor.")
    print("If the build is still running, you can wait until it's finished.")
    wait_for_ret()

    apiurl = "https://ci.appveyor.com/api/"
    account = "gicmo"
    project_name = "nixpy"

    url = os.path.join(apiurl, "projects", account, project_name)
    r = requests.get(url)

    projects = json.loads(r.text)
    build = projects["build"]
    for job in build["jobs"]:
        if job["status"] == "success":
            artifacts_url = os.path.join(apiurl, "buildjobs", job["jobId"],
                                         "artifacts")
            r = requests.get(artifacts_url)
            artifacts = json.loads(r.text)
            print(job["name"])
            for a in artifacts:
                print(os.path.join(apiurl, "buildjobs", job["jobId"],
                                   "artifacts", a["fileName"]))


def main():
    check_git_status()

    chdir()

    if len(sys.argv) < 2:
        die("Specify version (X.Y.Z)")

    newverstr = sys.argv[1]
    parse_version_string(newverstr)

    prepline = "Preparing new release: {}".format(newverstr)
    banner = "="*len(prepline) + "\n" + prepline + "\n" + "="*len(prepline)
    banner = bold_begin + banner + bold_end
    print(banner)

    chg = update_readme() | update_info(newverstr) | update_ci_confs(newverstr)
    if chg:
        print("Files have changed. Commit these changes and rerun the script.")
        sys.exit(0)

    check_git_status()  # might have been external changes (?) check again

    tag_head(newverstr)

    print("Creating archive...")
    os.chdir(gitroot)
    ret = call(["python", "setup.py", "sdist"])

    if ret > 0:
        die("Error creating package")

    print("{}Package ready. See 'dist' directory under project root.{}".format(
        bold_begin, bold_end
    ))

    print_appveyor_urls()


if __name__ == "__main__":
    main()
