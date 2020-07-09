# -*- coding: utf-8 -*-
"""Generate and output reference IPFS CIDs.

Note this requires ipfs cli to be install and on path.
"""
from subprocess import PIPE, Popen, DEVNULL


def get_cid(data: bytes):
    p = Popen(
        ["ipfs", "add", "--only-hash"],
        stdin=PIPE,
        stdout=PIPE,
        stderr=DEVNULL,
        shell=False,
    )
    p.stdin.write(data)
    p.stdin.close()

    result = b""
    output = p.stdout.read()
    while output:
        result += output
        output = p.stdout.read()

    cid = result.decode("ascii").split()[-1].strip()
    return cid


if __name__ == "__main__":
    zero = b"\x00"
    cid = get_cid(zero)
    print("CID for zero byte:", cid)
    assert cid == "QmS9JArPwa55ePgDnyg6TzX24mYTS1b1vLqWNebyVotKxQ"
    cid = get_cid("Hello World\n".encode("utf-8"))
    print("CID for Hello World", cid)
