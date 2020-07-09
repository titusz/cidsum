# -*- coding: utf-8 -*-
import hashlib
import io
import base58
import base64
from cidsum.pb import unixfs_pb2, merkledag_pb2
from google.protobuf import json_format


DEFAULT_CHUNK_SIZE = 262144


def cidsum(data, v=0) -> str:

    # Ensure we have a readable stream
    if isinstance(data, str):
        stream = open(data, "rb")
    elif not hasattr(data, "read"):
        stream = io.BytesIO(data)
    else:
        stream = data

    # Create Leave Chunk CIDs [(cid, block_size), ...]
    chunk_ids = []
    chunk = stream.read(DEFAULT_CHUNK_SIZE)
    while chunk:

        # Create UnixFS protobuf wrapped data
        ufs_obj = unixfs_wrap(chunk)
        ufs_data = ufs_obj.SerializeToString()

        # Create  PBNode wrapped data
        node_obj = pbnode_wrap(ufs_data)
        node_data = node_obj.SerializeToString()

        cid = cid_hash(node_data)
        chunk_ids.append((cid, len(node_data)))
        chunk = stream.read(DEFAULT_CHUNK_SIZE)

    if len(chunk_ids) == 1:
        return chunk_ids[0][0]

    # Root UnixFS
    ufs_obj = unixfs_pb2.Data()
    ufs_obj.Type = unixfs_pb2.Data.File
    ufs_obj.blocksizes.extend([i[-1] for i in chunk_ids])

    # Root Node
    node_obj = merkledag_pb2.PBNode()
    for cid, blocksize in chunk_ids:
        node_obj.Links.append(link_wrap(cid, blocksize))
    node_obj.Data = ufs_obj.SerializeToString()

    show_obj(node_obj)
    return cid_hash(node_obj.SerializeToString())


def unixfs_wrap(data: bytes) -> unixfs_pb2.Data:
    file_obj = unixfs_pb2.Data()
    file_obj.Type = unixfs_pb2.Data.File
    file_obj.Data = data
    file_obj.filesize = len(data)
    return file_obj


def pbnode_wrap(data: bytes) -> merkledag_pb2.PBNode:
    dag_obj = merkledag_pb2.PBNode()
    dag_obj.Data = data
    return dag_obj


def link_wrap(cid, block_size) -> merkledag_pb2.PBLink:
    cid_hash_digest = base58.b58decode(cid)
    link_obj = merkledag_pb2.PBLink()
    link_obj.Hash = cid_hash_digest
    link_obj.Name = ""
    link_obj.Tsize = block_size
    return link_obj


def cid_hash(data, v=0):
    # Create Multihash of serialized protobuff message
    base_hash = hashlib.sha256(data).digest()

    # Add hash algo and length prefix
    multi_hash = b"\x12" + b"\x20" + base_hash

    # Encode and reeturn as CIDv0 or CIDv1
    if v == 0:
        return base58.b58encode(multi_hash).decode()
    elif v == 1:
        version = 0b00000001 .to_bytes(1, "big")
        dag_pb = 0b01110000 .to_bytes(1, "big")
        digest = version + dag_pb + multi_hash
        return "b" + base64.b32encode(digest).decode("ascii").strip("=").lower()


def show_obj(obj):
    print(json_format.MessageToJson(obj))


if __name__ == "__main__":
    # Some basic tests:
    from cidsum.reference import get_cid

    zero = b"\x00"
    reference = get_cid(zero)
    result = cidsum(zero)
    print("Reference:", reference)
    print("Ours:     ", result)
    assert reference == result

    multichunk = zero * (DEFAULT_CHUNK_SIZE + 10)
    reference = get_cid(multichunk)
    result = cidsum(multichunk)
    print("MC Reference:", reference)
    print("MC Ours:     ", result)
