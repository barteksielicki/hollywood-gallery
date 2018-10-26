#!/usr/bin/env python

"""
This script is responsible for initial faces processing.
It's intended to be used on more powerful machines (at least 32GB RAM)
"""
import json
import multiprocessing
import os
import sys

from itertools import izip
import numpy as np
from scipy.io import loadmat
from tqdm import tqdm

from images import path_to_img

# settings
METADATA_FILE = 'data/imdb.mat'
IMAGES_DIRECTORY = 'data/imdb_crop'
OUTPUT_FILE = 'data/faces.jsonl'

N_WORKERS = 16
CHUNK_SIZE = 1024


# helper functions
def load_metadata(path):
    """
    :param path: str
    :return: (list, list)
    """
    meta = loadmat(path)['imdb'][0, 0]
    paths = np.concatenate(meta[2][0])
    images = [
        path_to_img(os.path.join(IMAGES_DIRECTORY, path))
        for path in paths
    ]
    names = np.concatenate(meta[4][0])
    assert len(images) == len(names)
    return paths, names, images


def process_face(args_tuple):
    """
    :param args: args_tuple
    :return: dict
    """
    from faces import face_to_vec, FaceError
    path, name, image = args_tuple
    try:
        vector = face_to_vec(image)
    except FaceError:
        return None

    return json.dumps({
        "name": name,
        "photo": path,
        "face": vector.tolist()
    })


# script
if __name__ == '__main__':
    print("Opening metadata file and loading images...")
    try:
        paths, names, images = load_metadata(METADATA_FILE)
    except (IOError, KeyError, IndexError, AssertionError):
        sys.exit("File %s doesn't exist or is corrupted!" % METADATA_FILE)
    total_faces = len(paths)
    print("%d faces found." % total_faces)

    print("Processing...")
    pool = multiprocessing.Pool(N_WORKERS)
    json_lines = [
        face_data for face_data in tqdm(pool.imap_unordered(
            process_face, izip(paths, names, images), chunksize=CHUNK_SIZE
        )) if face_data is not None
    ]
    successes = len(json_lines)
    with open(OUTPUT_FILE, "w") as output_file:
        output_file.writelines(json_lines)
    print("Done. %d faces processed. %d errors." % (
        successes, total_faces - successes
    ))
