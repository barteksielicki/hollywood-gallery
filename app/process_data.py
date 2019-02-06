#!/usr/bin/env python

"""
This script is responsible for initial faces processing.
It requires access to IMDB-WIKI dataset (*.mat file and images directory)
https://data.vision.ee.ethz.ch/cvl/rrothe/imdb-wiki/
"""
import json
import os
import sys

import numpy as np
from tqdm import tqdm
from scipy.io import loadmat

from server.faces import face_to_vec, FaceError
from server.images import path_to_img

# settings
METADATA_FILE = 'data/imdb.mat'
IMAGES_DIRECTORY = 'data/imdb_crop'
OUTPUT_FILE = 'data/faces.jsonl'


# helper functions
def load_metadata(path):
    """
    Loads metadata from *.mat file

    :param path: str
    :return: (list, list)
    """
    meta = loadmat(path)['imdb'][0, 0]
    photos = [
        os.path.join(IMAGES_DIRECTORY, path)
        for path in np.concatenate(meta[2][0])
    ]
    names = np.concatenate(meta[4][0])
    assert len(photos) == len(names)
    return photos, names


def save_face(name, photo, output_file):
    """
    Save face (JSON object containing 128D vector, name and path to original image)
    to output file.

    :param name: str
    :param photo: str
    :param output_file: file
    :return: bool
    """
    img = path_to_img(photo)
    try:
        vector = face_to_vec(img)
    except FaceError:
        return False

    face_data = {
        "name": name,
        "photo": photo,
        "face": vector.tolist()
    }
    output_file.write(json.dumps(face_data) + '\n')
    return True



if __name__ == '__main__':
    """
    Main script responsible for processing whole dataset. It takes no arguments.
    """
    print("Opening metadata file...")
    try:
        photos, names = load_metadata(METADATA_FILE)
    except (IOError, KeyError, IndexError, AssertionError):
        sys.exit("File %s doesn't exist or is corrupted!" % METADATA_FILE)
    total_faces = len(photos)
    print("%d faces found." % total_faces)

    print("Processing...")
    with open(OUTPUT_FILE, "w") as output_file:
        successes = 0
        for i in tqdm(xrange(total_faces)):
            ok = save_face(names[i], photos[i], output_file)
            if ok:
                successes += 1
    print("Done. %d faces processed. %d errors." % (
        successes, total_faces - successes
    ))
