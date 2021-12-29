#!/usr/bin/env python3

# RECOMMENDATIONS
#
# 1. Backup your state file


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    import json
    import urllib.request

    import sys
    import logging
    from optparse import OptionParser
    import os.path
    import shutil

    logging.basicConfig(level=logging.DEBUG)


    def set_working_directory():
        import os
        new_wd = os.path.dirname(sys.argv[0])
        os.chdir(new_wd)
        logging.debug(new_wd)


    set_working_directory()

    STATE_FILE = "download_latest.state"
    # PROJECT_URL = "signalapp/Signal-Desktop"

    usage = "usage: download_latest.py [options] PROJECT_URL ARTIFACT_NAME ARCHIVE_FORMAT"
    parser = OptionParser(usage)
    parser.add_option("-n", "--name", default="", dest="subfolder", help="name of local subfolder")
    parser.add_option("--log", default="DEBUG", dest="loglevel", help="loglevel")

    (options, args) = parser.parse_args()

    if len(args) != 3:
        print("Incorrect number of arguments!")
        print(usage)
        exit()

    PROJECT_URL = args[0]
    logging.debug(PROJECT_URL)
    ARTIFACT_NAME = args[1]
    logging.debug(ARTIFACT_NAME)
    ARCHIVE_FORMAT = args[2]
    logging.debug(ARCHIVE_FORMAT)

    # logging.basicConfig(level=options.loglevel)

    SUBFOLDER = PROJECT_URL.split("/")
    logging.debug(f"SUBFOLDER={SUBFOLDER}")

    if len(SUBFOLDER) != 2:
        print("Invalid project url {}: wrong number of slashes (1 expected)!")
        exit()

    SUBFOLDER = SUBFOLDER[1]

    if options.subfolder != "":
        SUBFOLDER = options.subfolder

    logging.debug(SUBFOLDER)

    # load state file
    if os.path.isfile(STATE_FILE):
        with open(STATE_FILE) as f:
            STATE = json.loads("\n".join(f.readlines()))
    else:
        STATE = {}

    # read json api object from github

    # logging.debug(urllib.request.urlopen("https://api.github.com/repos/{}/releases/latest".format(PROJECT_URL)).read())

    json_response = json.loads(
        urllib.request.urlopen("https://api.github.com/repos/{}/releases/latest".format(PROJECT_URL)).read())

    logging.debug(json_response['name'])

    remote_version = json_response['name']
    if SUBFOLDER in STATE:
        local_version = STATE[SUBFOLDER]
        if local_version == remote_version:
            print("remote version ({}) equals local version ({}). Nothing to do, quitting!".format(remote_version,
                                                                                                   local_version))
            exit()

    if ARTIFACT_NAME not in json_response:
        print("Artifact name not in json response. Check please!")
        exit()

    artifact_url = json_response[ARTIFACT_NAME]
    local_pkg, headers = urllib.request.urlretrieve(artifact_url)
    logging.debug(f"local_pkg = {local_pkg}")

    # remove old version
    if os.path.isdir(SUBFOLDER):
        shutil.rmtree(SUBFOLDER)

    # does not detect nested folders FIXME
    match ARCHIVE_FORMAT:
        case "zip":
            import zipfile
            with zipfile.ZipFile(local_pkg) as z:
                z.extract_all(SUBFOLDER)

        case "tgz":
            import subprocess
            import os

            os.mkdir(SUBFOLDER)
            os.chdir(SUBFOLDER)
            rv = subprocess.call(["tar", "xf", local_pkg])
            os.chdir("..")

        case _:
            print(f"archive format {ARCHIVE_FORMAT} not known. Exiting!")
            exit()

    STATE[SUBFOLDER] = remote_version

    logging.debug(f"remote={remote_version};state={STATE[SUBFOLDER]}")

    with open(STATE_FILE, 'w') as f:
        f.write(json.dumps(STATE))

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
