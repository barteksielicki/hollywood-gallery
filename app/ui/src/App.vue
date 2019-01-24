<template>
  <div id="app" class="main-app">
    <div class="main-panel" style="width:100%">
      <notifications group="foo" position='top left'/>
      <div>
        <h1>Hollywood gallery</h1>
        <div class="description">
          This site will tell you, which actor you look alike. The idea is very simple - application will capture the
          image from your webcam, and then it will show the name and photo of the most look alike actor.<br>Please make sure there is only one person visible
          in the frame!
        </div>
      </div>
      <div>
        <h1>Settings</h1>
        <div>
          Actors limit: {{ actorsLimit }}<br>
          <input type="range" min="1" max="18827" v-model="actorsLimit" class="slider"><br>
          <button @click="rotate">Rotate camera input</button>
        </div>
      </div>
      <div>
        <h1>Face detector</h1>
        <div class="video-wrapper">
          <img class="placeholder-img" src="https://via.placeholder.com/480x480" v-if="!cameraLoaded">
          <video id="video"
                 width="480"
                 height="480"
                 preload autoplay loop muted
                 v-show="cameraLoaded"
                 :style="{transform: `rotate(${rotation}deg)`}"
          ></video>
        </div>
      </div>
      <div>
        <h1>Face processor</h1>
        <!--<img class="classification-img" id="input-image"-->
             <!--:src="this.base64Image || 'https://via.placeholder.com/240x240'">-->
        <canvas id="frame-canvas" width="240" height="240"></canvas>
        <img class="classification-img" id="output-image"
             :src="this.responseImage || 'https://via.placeholder.com/240x240'">
        <br>
        <p>{{ this.responseName }}</p>
      </div>
      <hr>
      <div class="history">
        <h2>Last 5 actors</h2>
        <div class="history-item" v-for="actor in history">
          <img :src="actor.image"><br>
          <p>{{ actor.name }}</p>
        </div>
      </div>
      <hr>
      <footer>
        <p>
          <small>&copy; 2019 B. Sielicki, P. Wołosz, D. Kisieliński</small><br>
          <a href="https://github.com/barteksielicki/hollywood-gallery">Warsztaty badawcze</a>
        </p>
      </footer>
    </div>
  </div>
</template>

<script>
  import axios from 'axios'

  const API_URL = 'https://hollywoodgallery.mini.pw.edu.pl'

  export default {
    data () {
      return {
        video: null,
        canvas: null,
        context: null,
        blobImage: null,
        base64Image: null,
        responseImage: null,
        responseName: '',
        cameraLoaded: false,
        actorsLimit: 1000,
        history: [],
        faceNotDetectedCounter: 0,
        rotation: 0
      }
    },
    computed: {
      isReady () {
        return this.cameraLoaded
      }
    },
    mounted () {
      // get camera input
      this.video = document.getElementById('video')

      navigator.mediaDevices.getUserMedia({video: true, audio: false})
        .then(stream => {
          this.video.srcObject = stream
          this.canvas = document.getElementById('frame-canvas')
          this.context = this.canvas.getContext('2d')
          this.cameraLoaded = true
          console.log('Camera loaded')
        })
        .catch(error => {
          console.log('Error loading camera.', error)
        })
    },
    watch: {
      isReady (nowReady, wasReady) {
        if (!wasReady && nowReady) {
          console.log('Capturing loop started...')
          setTimeout(this.captureFrame, 1000)
        }
      },
      blobImage (blob) {
        // render preview
        // const reader = new FileReader()
        // reader.readAsDataURL(blob)
        // // reader.onloadend = () => {
        // //   this.base64Image = reader.result
        // //   console.log('base64 end')
        // // }

        const currentImage = this.responseImage
        const currentName = this.responseName

        // send and retrieve result
        const data = new FormData()
        data.append('photo', blob)
        data.append('limit', this.actorsLimit)
        console.log('making request...')
        axios.post(API_URL + '/process', data, {
          headers: {'Content-Type': 'multipart/form-data'}
        }).then(response => {
          if (response.data.photo) {
            this.responseImage = `${API_URL}/${response.data.photo.replace('data/imdb_crop', 'img')}`
            this.responseName = response.data.name
            this.faceNotDetectedCounter = 0
          } else {
            this.responseImage = null
            this.responseName = ''
            this.showWarn('Cannot detect face', 'Try to bring your face closer to the webcam.')
            if (this.faceNotDetectedCounter++ === 10) {
              this.resetStats()
            }
          }
        }).catch(err => {
          this.responseImage = null
          this.responseName = ''
          this.showError('Error', 'Something went wrong, please contact serwer administrator.')
        }).finally(() => {
          if (currentImage && this.history.length === 5) {
            this.history.pop()
          }
          if (currentImage) {
            this.history.unshift({
              image: currentImage,
              name: currentName
            })
          }
          setTimeout(this.captureFrame, 1000)
        })
      }
    },
    methods: {
      captureFrame () {
        // capture camera frame
        console.log('capturing frame...')
        this.context.translate(120, 120);
        this.context.rotate(this.rotation * Math.PI / 180)
        this.context.translate(-120, -120);
        this.context.drawImage(this.video, 0, 0, 480, 480, 0, 0, 240, 240)
        this.context.translate(120, 120);
        this.context.rotate(-this.rotation * Math.PI / 180)
        this.context.translate(-120, -120);
        this.canvas.toBlob(blob => {
          this.blobImage = blob
        })
      },
      resetStats () {
        console.log('reset')
        this.faceNotDetectedCounter = 0
        this.history.splice(0, this.history.length)
      },
      showWarn (title, message) {
        this.$notify({
          group: 'foo',
          type: 'warn',
          title: title,
          duration: 1000,
          text: message
        })
      },
      showError (title, message) {
        this.$notify({
          group: 'foo',
          type: 'error',
          title: title,
          duration: 1000,
          text: message
        })
      },
      rotate () {
        this.rotation = (this.rotation + 90) % 360
      }

    }
  }
</script>

<style lang="scss">
  #app {
    font-family: 'Avenir', Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-align: center;
    color: #2c3e50;
    margin-top: 20px;
  }

  html {
    height: 100%;
    width: 100%;
  }

  body {
    margin: 0px !important;
    height: 100%;
    width: 100%;
  }

  h1, h2 {
    font-weight: normal;
  }

  ul {
    list-style-type: none;
    padding: 0;
  }

  li {
    display: inline-block;
    margin: 0 10px;
  }

  a {
    color: #42b983;
  }

  img {
    width: 480px;
    height: 360px;
  }

  .main-app {
    display: flex;
    margin: 0px !important;
    height: 100%;
  }

  .vue-notification {
    border-radius: 10px;
  }

  .description {
    width: 90%;
    max-width: 740px;
    margin: 0 auto;
  }

  .placeholder-img, .classification-img {
    width: 240px;
    height: 240px;
  }

  .video-wrapper {
    margin: 0 auto;
    width: 480px;
    height: 480px;
    overflow: hidden;
  }

  video {
    width: 480px;
    height: 480px;
    object-fit: cover;
  }

  .stats {
    border-top: 1px solid #2c3e50;
    margin-top: 20px;
  }

  .stats-list {
    text-align: left;
    margin-left: 5px;
  }

  .slider {
    width: 480px;
  }

  hr {
    margin: 25px 0;
  }

  .history {
    text-align: left;
    padding-left: 5%;
    .history-item {
      display: inline-block;
      width: 15%;


      &:not(:last-child) {
        margin-right: 5%;
      }
    }
    img {
      width: 100%;
      height: auto;
    }
  }

  footer {
    text-align: center;
    a {
      color: black;
      font-size: 1em;
    }
  }
</style>
