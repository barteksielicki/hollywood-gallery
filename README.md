# hollywood-gallery

This application can tell people which actor they look alike. The idea is very simple - user sits in front of the computer (which has 
a camera, of course) and when the application will capture the image from the camera's picture then it will show the name and photo 
of the most look alike actor. Then after some time it will try to find the face again and the whole process will continue until user turns off the app. Working application can be found under the address: https://hollywoodgallery.mini.pw.edu.pl/.

The project was made on [research workshops classes](https://github.com/pbiecek/CaseStudies2019W) at the Warsaw University of Technology at the Faculty of Mathematics and Information Science by Bartłomiej Sielicki, Patryk Wołosz and Damian Kisieliński.

## Face recognition

Our app's main goal is to recognize faces, therefore we need a way to translate an image to other representation that can be better interpreted by the computer. That's what openface model is used for. It is already trained for translating images to vectors, also it has face recognition built in. The workflow of this model is shown on the schema underneath.

![Figure 1: Openface usage](https://raw.githubusercontent.com/barteksielicki/hollywood-gallery/master/images/schema.png)

The first that the model does is it detects the face on the image using dlib or OpenCV. Then OpenCV is used again to transform the image using affine transformation so that face is on the same level as in the rest of the images. Then face is cropped of the picture and embedded to a 128-dimensional vector. This representation is much easier to work with then the whole image. For more info about openface please visit official site - http://cmusatyalab.github.io/openface. Our application supports only one person in front of the camera.

## Technologies and data used

* OpenFace (https://github.com/cmusatyalab/openface) - version 0.2.0
* vue.js (https://vuejs.org/) - version 2.5
* python (https://www.python.org/) - version 2.7
* pandas (https://pandas.pydata.org/) - version 0.23.4
* actors dataset from https://data.vision.ee.ethz.ch/cvl/rrothe/imdb-wiki/ (18827 actors, over 300000 photos)
* docker (https://www.docker.com/) - version 18.09.0

## Architecture

![Architecture](https://github.com/barteksielicki/hollywood-gallery/blob/master/images/architecture.jpg?raw=true "Architecture schema")

The whole project consists of two parts: UI and server. UI is the interface for user, it shows the picture from the camera, sends
requests with image of user to server and displays found actors. Server finds face on image from request,
embeds it as vector and then finds most look alike actor. After this operations server sends back response with actor's name and image, which is displayed in UI.

## App workflow

### UI

The UI uses vue.js as a front-end framework. It uses images from users camera that are captured every second and sends these images to server (one image is send per request, one request per second). After sending the request app is waiting for response. The response contains information if the model found the face on this picture and if so then it also has a picture and
name of the actor. Then this information is displayed and statistics are updated - on the right there's a dashboard containing actors from last five responses
and top ten actors that have been returned the most times. After that it waits one second and repeats the whole process. 
Preview of the app is shown below.

![Preview](https://github.com/barteksielicki/hollywood-gallery/blob/master/images/screen.png?raw=true "App preview")

On the top of the page there's slider (1) that can be used to change the numbers of actors that will be considered when searching for the most suitable actor. Under the slider there's a button (2) that allows the user to rotate the camera's preview, every click rotates it 90 degrees clockwise. There is preview from the camera (3), image that was sent to server (4) and returned actor's photo (5). The last thing is the panel on the bottom (6) containing some images - those are last five photos that were returned from server with actors' name under them. 
When the server can't recognize face on any image over 10 seconds then the history resets.

### Server

On server part there's app with API with method for exchanging requests/responses with UI. These app has also OpenFace model. Information about this model can be found on the project's website (http://cmusatyalab.github.io/openface/). 
The model performs following operations:
* finding face on image (OpenCV,dlib) 
* cropping the face
* transforming the image so it's in on the same level as on other pictures
* translating it to vector

Then after the vector is returned we calculate which vector from actors' database is the closest one and Then the app finds the image to which this vector belong to and returns it with the name.


