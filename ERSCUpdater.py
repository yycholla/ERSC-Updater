import configparser
from tkinter import Tk
from tkinter.filedialog import askdirectory
import os
import shutil
import urllib.request
import zipfile
import requests

config_dir = os.path.expanduser("~/Documents/My Games/ERSC")
if not os.path.exists(config_dir):
    os.mkdir(config_dir)
repo = "LukeYui/EldenRingSeamlessCoopRelease"

releases = f"https://api.github.com/repos/{repo}/releases/latest"


def get_version():
    """
    Retrieves the latest release version from the GitHub API and returns it without the "BETA" prefix.

    Returns:
        str: The latest release version without the "BETA" prefix.

    Raises:
        requests.exceptions.RequestException: If there was an error while making the GET request to the GitHub API.
    """
    print("Determining latest release")
    tag = requests.get(releases, timeout=1000)
    if tag.status_code == 403:
        print("API request limit reached, can't check latest version")
        return get_installed_version()
    ver = tag.json()["name"]
    ver = ver.lstrip("BETA ")
    return ver


def get_installed_version() -> str:
    try:
        config = configparser.RawConfigParser(allow_no_value=True)
        config.read(f"{config_dir}/ERSCUpdater.ini")
        return config.get("DEFAULT", "erver")
    except configparser.NoOptionError:
        return ""


def version_mismatch(version) -> bool:
    """
    Check if the installed version is different from the latest version obtained from the GitHub API.
    """
    return version != get_installed_version()


def get_erdir() -> str:
    try:
        config = configparser.RawConfigParser(allow_no_value=True)
        config.read(f"{config_dir}/ERSCUpdater.ini")
        return config.get("DEFAULT", "erdir")
    except configparser.NoOptionError:
        Tk().withdraw()
        return askdirectory()


def set_er_config_dir(erdir) -> None:
    config = configparser.RawConfigParser(allow_no_value=True)
    config.read(f"{config_dir}/ERSCUpdater.ini")
    config.set("DEFAULT", "erdir", erdir)
    with open(f"{config_dir}/ERSCUpdater.ini", "w", encoding="utf-8") as config_file:
        config.write(config_file)


def set_er_config_ver(version) -> None:
    config = configparser.RawConfigParser(allow_no_value=True)
    config.read(f"{config_dir}/ERSCUpdater.ini")
    config.set("DEFAULT", "erver", version)
    with open(f"{config_dir}/ERSCUpdater.ini", "w", encoding="utf-8") as config_file:
        config.write(config_file)


def get_config_settings() -> dict:
    try:
        options = {}
        config = configparser.RawConfigParser(allow_no_value=True)
        config.read(f"{config_dir}/ERSCUpdater.ini")
        options["invaders"] = config.get("OPTIONS", "allow_invaders")
        options["skip"] = config.get("OPTIONS", "skip_splash_screens")
        return options
    except configparser.NoOptionError:
        options = {"invaders": "0", "skip": "1"}
        config.set("OPTIONS", "allow_invaders", options["invaders"])
        with open(
            f"{config_dir}/ERSCUpdater.ini", "w", encoding="utf-8"
        ) as config_file:
            config.write(config_file)
        return options
    except configparser.NoSectionError:
        options = {"invaders": "0", "skip": "1"}
        config.add_section("OPTIONS")
        config.set("OPTIONS", "skip_splash_screens", options["skip"])
        with open(
            f"{config_dir}/ERSCUpdater.ini", "w", encoding="utf-8"
        ) as config_file:
            config.write(config_file)
        return options


def main():
    version = get_version()
    erdir = get_erdir()
    set_er_config_dir(erdir)
    file = "ersc.zip"
    download = f"https://github.com/{repo}/releases/download/{version}/{file}"
    if version_mismatch(version):
        urllib.request.urlretrieve(download, "ersc.zip")

        with zipfile.ZipFile("ersc.zip", "r") as zip_ref:
            zip_ref.extractall(f"{erdir}/ersc")
        os.remove(file)

        allfiles = os.listdir(f"{erdir}/ersc")

        for file in allfiles:
            if os.path.isdir(f"{erdir}/{file}"):
                print(file, "exists as dir in destination | deleting")
                shutil.rmtree(f"{erdir}/{file}")
            elif os.path.isfile(f"{erdir}/{file}"):
                print(file, "exists as file in destination | deleting")
                os.remove(f"{erdir}/{file}")

            shutil.move(f"{erdir}/ersc/{file}", f"{erdir}/{file}")
            print("moved", file, "to Elden Ring directory")
            if os.path.isdir(file):
                shutil.rmtree(file)
            elif os.path.isfile(file):
                os.remove(file)

        parser = configparser.RawConfigParser(allow_no_value=True)
        parser.read(f"{erdir}/SeamlessCoop/ersc_settings.ini")
        parser.set("PASSWORD", "cooppassword", "apples123")
        parser.set("GAMEPLAY", "allow_invaders", get_config_settings()["invaders"])
        parser.set("GAMEPLAY", "skip_splash_screens", get_config_settings()["skip"])
        with open(f"{erdir}/SeamlessCoop/ersc_settings.ini", "w") as config_file:
            parser.write(config_file)
        print("Coop Password set to: ", parser.get("PASSWORD", "cooppassword"))
        print(
            f"Config written to {config_dir}/ERSCUpdater.ini if you would like to change any settings."
        )
    print(f"Seamless {version} is the latest | you are up to date")
    set_er_config_ver(version)
    os.chdir(get_erdir())
    start_er = input("Start Elden Ring Seamless Coop?: (y / n / default = y): ")
    if start_er in ["y", "Y", ""]:
        os.startfile("ersc_launcher.exe")
    else:
        print("ERSC Updated")


main()
