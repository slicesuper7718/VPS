#!/usr/bin/env python3
import os
import subprocess
import shutil

CRD_SSH_Code = "DISPLAY= /opt/google/chrome-remote-desktop/start-host --code="4/0AVGzR1DGLbIrdjIbqqU2Z8hUdbpL8Ms26RciuXMHVfMM2zNLxnIHj9XeSa3ovhO0kW9x2A" --redirect-url="https://remotedesktop.google.com/_/oauthredirect" --name=$(hostname)"
username = "sabir7718"
password = "root"      # <-- new user's password set to 'root' as you requested
Pin = 771828          # Chrome Remote Desktop PIN (unchanged)
Autostart = False     # autostart removed

def user_exists(user):
    return subprocess.run(['id', '-u', user], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0

def apt_update_once():
    print("Running apt update...")
    subprocess.run(['sudo', 'apt', 'update'], check=False)

def install_package(pkg):
    check = subprocess.run(['dpkg', '-s', pkg], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if check.returncode != 0:
        print(f"Installing {pkg}...")
        subprocess.run(['sudo', 'apt', 'install', '-y', pkg], check=False)
    else:
        print(f"{pkg} is already installed, skipping.")

def create_or_update_user(user, pwd):
    if not user_exists(user):
        print(f"Creating user '{user}' and adding to sudo...")
        subprocess.run(['sudo', 'useradd', '-m', user], check=False)
        subprocess.run(['sudo', 'adduser', user, 'sudo'], check=False)
    else:
        print(f"User '{user}' already exists; will update password and ensure sudo membership.")
        # ensure sudo membership (safe even if already a member)
        subprocess.run(['sudo', 'usermod', '-aG', 'sudo', user], check=False)

    # Set/update the user's password to the specified value (here: 'root')
    print(f"Setting password for user '{user}' ...")
    subprocess.run(['sudo', 'chpasswd'], input=f"{user}:{pwd}".encode(), check=False)
    # ensure default shell is bash
    subprocess.run(['sudo', 'sed', '-i', 's#/bin/sh#/bin/bash#g', '/etc/passwd'], check=False)

def install_firefox():
    if shutil.which("firefox"):
        print("firefox binary found, skipping firefox install.")
        return
    print("Installing Firefox to /opt ...")
    cmd = (
        'cd /opt && sudo wget -O firefox-latest.tar.xz '
        '"https://download.mozilla.org/?product=firefox-latest&os=linux64&lang=en-US&type=tar.xz" '
        '&& sudo tar -xf firefox-latest.tar.xz && sudo rm firefox-latest.tar.xz '
        '&& sudo ln -sf /opt/firefox/firefox /usr/local/bin/firefox'
    )
    subprocess.run(cmd, shell=True, check=False)

def install_xfce():
    print("Ensuring XFCE and related packages are installed...")
    os.environ["DEBIAN_FRONTEND"] = "noninteractive"
    install_package("xfce4")
    install_package("desktop-base")
    install_package("xfce4-terminal")
    subprocess.run(['sudo', 'bash', '-c',
                    'echo "exec /etc/X11/Xsession /usr/bin/xfce4-session" > /etc/chrome-remote-desktop-session'],
                   check=False)
    subprocess.run(['sudo', 'apt', 'remove', '--assume-yes', 'gnome-terminal'], check=False)
    install_package("xscreensaver")
    subprocess.run(['sudo', 'service', 'lightdm', 'stop'], check=False)
    install_package("dbus-x11")
    subprocess.run(['sudo', 'service', 'dbus', 'start'], check=False)

def install_crd():
    check = subprocess.run(['dpkg', '-s', 'chrome-remote-desktop'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if check.returncode != 0:
        print("Installing Chrome Remote Desktop package...")
        subprocess.run(['wget', 'https://dl.google.com/linux/direct/chrome-remote-desktop_current_amd64.deb'], check=False)
        subprocess.run(['sudo', 'dpkg', '--install', 'chrome-remote-desktop_current_amd64.deb'], check=False)
        subprocess.run(['sudo', 'apt', 'install', '--assume-yes', '--fix-broken'], check=False)
    else:
        print("Chrome Remote Desktop already installed, skipping.")

def install_qbittorrent():
    install_package("qbittorrent")

def setup_crd(user, auth_code):
    print("Adding user to chrome-remote-desktop group and configuring CRD auth/pin...")
    subprocess.run(['sudo', 'adduser', user, 'chrome-remote-desktop'], check=False)
    if not auth_code:
        print("No CRD auth code provided; skipping CRD registration step.")
        return
    command = f"{auth_code} --pin={Pin}"
    subprocess.run(['sudo', 'su', '-', user, '-c', command], check=False)
    subprocess.run(['sudo', 'service', 'chrome-remote-desktop', 'start'], check=False)

def main():
    apt_update_once()
    create_or_update_user(username, password)
    install_crd()
    install_xfce()
    install_firefox()
    install_qbittorrent()
    setup_crd(username, CRD_SSH_Code)

    print("BY SABIR7718")
    print("\n\n")
    print(f"Log in PIN : {Pin}")
    print(f"User Name : {username}")
    print(f"User Pass : {password}")
    print("\nImportant: This script DOES NOT change the system 'root' account password. It only sets the new user's password to 'root' as you requested.")
    print("Security note: using 'root' as a regular user's password is insecure — change later if this is just temporary.")

if __name__ == "__main__":
    main()