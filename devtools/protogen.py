# -*- coding: utf-8 -*-
"""Generate python code for unixfs.proto and  merkledag.proto"""
import os
import subprocess
from pathlib import Path


PROTO_DIR = Path(__file__).parents[1] / Path("cidsum/pb")


def protogen():
    os.chdir(PROTO_DIR)
    subprocess.run("protoc unixfs.proto merkledag.proto --python_out=.")


if __name__ == "__main__":
    protogen()
