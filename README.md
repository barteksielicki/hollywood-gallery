# hollywood-gallery

This is project is for telling people which actor they look alike. The idea is very simple - user sits in front of the computer (which has 
a camera, of course) and when the application will capture the image from the camera's picture then it will show the name and photo 
of the most look alike actor. Then after some time it will try to find the face again and the whole process will continue until user turns 
off the app.

## Face recognition

Our app's main goal is to recognise faces, therefore we need a way to translate an image to other represantation that can be better interpreted by the computer. That's what openface model is used for. It is already trained for translating images to vectors, also it has face recogniotion built in. The workflow of this model is shown on the shema underneath.

![Figure 1: Openface usage]
(https://github.com/barteksielicki/hollywood-gallery/blob/master/images/schema.png)

The first that the model does is it detects the face on the image using dlib or OpenCV. Then OpenCV is used again to transform the image using affine transformation so that face is on the same level as in the rest of the images. Then face is cropped of the picture and embedded to a 128-dimensional vector. This representation is much easier to work with then the whole image. For more info about openface please visit official site - http://cmusatyalab.github.io/openface.

## Technologies and data used

* OpenFace (https://github.com/cmusatyalab/openface)
* vue.js (https://vuejs.org/)
* python (https://www.python.org/)
* pandas (https://pandas.pydata.org/)
* actors dataset from https://data.vision.ee.ethz.ch/cvl/rrothe/imdb-wiki/ (18827 actors, over 300000 photos)
* docker (https://www.docker.com/)

## Architecture

![Architecture](https://github.com/barteksielicki/hollywood-gallery/blob/master/images/architecture.jpg?raw=true "Architecture schema")

The whole project consists of two parts: UI and server. UI is the interface for user, it shows the picture from the camera, sends
requests with image of user to server, displays found actors and statistics about previously found actors. Server finds face on image from request,
embeds it as vector and then finds most look alike actor. After this operations server sends back response with actor's name and image, chich is displayed in UI.

## App workflow

### UI

The UI uses vue.js as a front-end framework. It uses images from users camera that are captured every second and sends these images to server (one image is send per request, one request per second). After sending the request app is waiting for response. The response contains information if the model found the face on this picture and if so then it also has a picture and
name of the actor. Then this information is displayed and statistics are updated - on the right there's a dashboard containing actors from last five responses
and top ten actors that have been returned the most times. After that it waits one second and repeats the whole process. 
Preview of the app is shown below.

![Preview](https://github.com/barteksielicki/hollywood-gallery/blob/master/images/preview.png?raw=true "App preview")

There is preview from the camera (1), image with found face (2) and actor's photo (3) and name (4). There is one more thing on the user's interface - slider (5). It can be used to change the numbers of actors that will be considered when searching for
the most suitable actor. The last thing is the panel on the right. There is the list of last 5 returned actors (6) and list of 10 most frequently appearing actors (7).

### Server

On server part there's app with API with method for exchanging requests/responses with UI. These app has also OpenFace model. Informations about this model can be found on the project's website (http://cmusatyalab.github.io/openface/). 
The model performs following operations:
* finding face on image (OpenCV,dlib) 
* cropping the face
* transforming the image so it's in on the same level as on other pictures
* translating it to vector

Then after the vector is returned we calculate which vector from actors' database is the closest one and Then the app finds the image to which this vector belong to and returns it with the name.


