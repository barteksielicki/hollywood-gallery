import json

import numpy as np
import pandas as pd


def load_faces(path):
    meta = []
    faces_matrix = []
    with open(path, "r") as f:
        for line in f:
            data = json.loads(line)
            face = data.pop("face")
            meta.append(data)
            faces_matrix.append(face)
    return pd.DataFrame(meta), np.array(faces_matrix)


def nearest_vector(X, y):
    diff = X - y
    dists = np.square(np.einsum('ij,ij->i', diff, diff))
    idx = np.argmin(dists)
    return X[idx], idx
