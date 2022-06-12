#!/usr/bin/env python3

# MIT License Copyright (C) 2022 Hiroshi Shimamoto
# generate userdata for cloud-init

import sys
import os
import subprocess
from argparse import ArgumentParser

def userdata_ubuntu(param):
    pkgs = ""
    if len(param['packages']) > 0:
        pkgs = "packages:\n" + "\n".join(list(map(lambda x: "  - "+x, param['packages'])))
    user = "\n".join(list(map(lambda x: "  "+x,
        [
            "- name: " + param['username'],
            "  ssh-authorized-keys:",
            "    - " + param['userpubkey'],
            "  sudo: [ 'ALL=(ALL) NOPASSWD:ALL' ]",
            "  groups: [ adm, cdrom, sudo, dip, plugdev ]",
            "  shell: /bin/bash",
        ]
    )))
    yml = f"""#cloud-config
timezone: {param['timezone']}
package_upgrade: true
{pkgs}
users:
{user}
"""
    return yml

def default_param():
    param = {
        'timezone': "Asia/Tokyo",
        'packages': [],
        'username': os.getenv("USER"),
    }
    return param

def development(param):
    param['packages'].extend(["build-essential", "python3-pip"])
    return param

def main():
    print(sys.argv)
    param = default_param()
    parser = ArgumentParser(description="gen-userdata")
    parser.add_argument('--packages', action='append')
    parser.add_argument('--pubkey', default="")
    parser.add_argument('--privkey', default="")
    parser.add_argument('--set', action='append')
    args = parser.parse_args()
    print(args)
    # parse
    if not args.packages is None:
        for a in args.packages:
            param['packages'].extend(a.split(','))
    # privkey to pubkey
    if os.path.exists(args.privkey):
        # generate public key from private key
        s = subprocess.run(["ssh-keygen", "-y", "-f", args.privkey], stdout=subprocess.PIPE)
        param['userpubkey'] = s.stdout.decode().strip()
    elif os.path.exists(args.pubkey):
        with open(args.pubkey) as f:
            param['userpubkey'] = f.read().strip()
    # devel flag
    if not args.set is None:
        for s in args.set:
            if s == "devel":
                param = development(param)
    ud = userdata_ubuntu(param)
    print(ud)

if __name__ == '__main__':
    main()
