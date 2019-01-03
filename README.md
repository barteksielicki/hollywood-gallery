# hollywood-gallery

This is project is for telling people which actor they look alike. The idea is very simple - user sits in front of the computer (which has 
a camera, of course) and when the application will capture the image from the camera's picture then it will show the name and photo 
of the most look alike actor. Then after some time it will try to find the face again and the whole process will continue until user turns 
off the app.

## Technologies and data used

* OpenFace (https://github.com/cmusatyalab/openface)
* vue.js (https://vuejs.org/)
* python (https://www.python.org/)
* actors dataset from https://data.vision.ee.ethz.ch/cvl/rrothe/imdb-wiki/ (18827 actors, over 300000 photos)

## Architecture

![Architecture](https://github.com/barteksielicki/hollywood-gallery/blob/master/images/architecture.png "Architecture schema")

The whole project consists of two parts: web app (UI) and back-end (server). UI is the interface for user, it recognizes the user's face, sends
requests with image of user to server and displays found actors and statistics about previously found actors. Server finds face on image from request,
embeds it as vector and then finds most look alike actor. After this operations server sends back response with actor's name and image.

## Details

### UI

The web app uses vue.js as a front-end framework. It uses images from users camera that are captured every second and sends these images to server (one image is send per request, one request per second). After sending the request app is waiting for response. The response contains information if the model found the face on this picture and if so then it also has a picture and
name of the actor. Then this information is displayed and statistics are updated - on the right there's a dashboard containing actors from last five responses
and top ten actors that have been returned the most times. After that it waits two seconds and repeats the whole process. 
Preview of the app is shown below.

![Preview](https://github.com/barteksielicki/hollywood-gallery/blob/master/images/preview.png "App preview")

There is preview from the camera (1), image with found face (2) and actor's photo (3). There is one more thing on the user's interface - slider. It can be used to change the numbers of actors that will be considered when searching for
the most suitable actor. 

### Server

On server part there's app with API with method for exchanging requests/responses with UI. These app has also OpenFace model. Informations about this model can be found on the project's website (http://cmusatyalab.github.io/openface/). 
The model performs following operations:
* finding face on image
* cropping the face
* translating it to vector

Then after the vector is returned we calculate which vector from actors' database is the closest one and Then the app finds the image to which this vector belong to and returns it with the name.


