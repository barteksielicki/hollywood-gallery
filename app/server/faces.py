import openface

# settings
FACE_PREDICTOR_PATH = '/root/openface/models/dlib/shape_predictor_68_face_landmarks.dat'
MODEL_PATH = '/root/openface/models/openface/nn4.small2.v1.t7'
IMG_DIM = 96


# exceptions
class FaceError(Exception):
    pass


# initial objects - neural network initialization
align = openface.AlignDlib(FACE_PREDICTOR_PATH)
net = openface.TorchNeuralNet(MODEL_PATH)


# api
def face_to_vec(image):
    """
    Core function. It takes image object, and using openface
    returns representation of face found in image on a 128-dimensional unit hypersphere.
    """
    bounding_box = align.getLargestFaceBoundingBox(image)
    if bounding_box is None:
        # bounding_box is None, when no visible face was found in image
        # otherwise it's bounding_box enclosing found face.
        raise FaceError("There is no face in the image")
    face = align.align(
        IMG_DIM, image, bounding_box,
        landmarkIndices=openface.AlignDlib.OUTER_EYES_AND_NOSE
    )
    if face is None:
        # face is None when landmark indices could not be aligned properly.
        # it might happen when face / photo is deformed or misshapen
        raise FaceError("Face cannot be aligned properly")

    # if everything is ok we run neural network to get face embedding.
    return net.forward(face)
