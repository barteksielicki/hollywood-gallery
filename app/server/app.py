import json

import tornado.ioloop
import tornado.web

from faces import face_to_vec, FaceError
from images import bytes_to_img
from utils import load_faces, nearest_vector

# settings
PORT = 8000
IMAGES_DIRECTORY = '../data/imdb_crop'
STATIC_APP_DIRECTORY = '../ui'
FACES_FILE = '../data/faces.jsonl'

# initial objects
meta, faces_matrix = load_faces(FACES_FILE)


# handlers
class ProcessImageHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")

    def post(self):
        img_bytes = self.request.files['photo'][0]['body']
        img = bytes_to_img(img_bytes)
        try:
            face_vector = face_to_vec(img)
        except FaceError:
            response = {}
        else:
            actors_limit = self.get_body_argument(
                "limit", default=None, strip=False
            )
            lookup_matrix = faces_matrix
            if actors_limit:
                first_index = meta[meta['actor_id'] >= int(actors_limit)].index[0]
                lookup_matrix = lookup_matrix[:first_index, :]
            _, idx = nearest_vector(lookup_matrix, face_vector)
            response = meta.iloc[idx].to_dict()
            response["photo"] = response["photo"].replace(IMAGES_DIRECTORY, "img")
        self.write(json.dumps(response))


# app
def make_app():
    return tornado.web.Application([
        (r"/process", ProcessImageHandler),
        (r"/img/(.*)", tornado.web.StaticFileHandler, {
            "path": IMAGES_DIRECTORY
        }),
        (r"/(.*)", tornado.web.StaticFileHandler, {
            "path": STATIC_APP_DIRECTORY,
            "default_filename": "index.html"
        })
    ])


# running script
if __name__ == '__main__':
    app = make_app()
    app.listen(PORT)
    print("Listening on port %d..." % PORT)
    tornado.ioloop.IOLoop.current().start()