<template>
  <div id="app" class="main-app">
    <div class="main-panel" style="width:100%">
      <notifications group="foo" position='top left'/>
      <div>
        <h1>Hollywood gallery</h1>
        <div class="description">
          This site will tell you, which actor you look alike. The idea is very simple - application will capture the
          image from your webcam, and then it will show the name and photo of the most look alike actor.
        </div>
      </div>
      <div>
        <h1>Face detector</h1>
        <img class="placeholder-img" src="https://via.placeholder.com/480x360" v-if="!cameraLoaded">
        <video id="video" width="480" height="360" preload autoplay loop muted v-show="cameraLoaded"></video>
      </div>
      <div>
        <h1>Face processor</h1>
        <img class="classification-img" id="input-image"
             :src="this.base64Image || 'https://via.placeholder.com/480x360'">
        <img class="classification-img" id="output-image"
             :src="this.responseImage || 'https://via.placeholder.com/480x360'">
      </div>
      <div>
        <h1>Settings</h1>
        <div>
          Actors limit: {{ actorsLimit }}<br>
          <input type="range" min="1" max="18826" v-model="actorsLimit" class="slider">
        </div>
      </div>
      <hr>
      <div class="history">
        <img v-for="image in history" :src="image">
      </div>
    </div>
  </div>
</template>

<script>
  import axios from 'axios'

  const API_URL = 'http://192.168.137.31'

  export default {
    data () {
      return {
        video: null,
        canvas: null,
        context: null,
        blobImage: null,
        base64Image: null,
        responseImage: null,
        cameraLoaded: false,
        actorsLimit: 1000,
        history: [],
        faceNotDetectedCounter: 0,
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
          this.canvas = document.createElement('canvas')
          this.canvas.width = this.video.width
          this.canvas.height = this.video.height
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
        const reader = new FileReader()
        reader.readAsDataURL(blob)
        reader.onloadend = () => {
          this.base64Image = reader.result
        }

        const currentImage = this.responseImage

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
            this.faceNotDetectedCounter = 0
          } else {
            this.responseImage = null
            this.showWarn('Cannot detect face', 'Try to bring your face closer to the webcam.')
            if (this.faceNotDetectedCounter++ === 10) {
              this.resetStats()
            }
          }
        }).catch(err => {
          this.responseImage = null
          this.showError('Error', 'Something went wrong, please contact serwer administrator.')
        }).finally(() => {
          if (currentImage && this.history.length === 5) {
            this.history.pop()
          }
          if (currentImage) {
            this.history.unshift(currentImage)
          }
          setTimeout(this.captureFrame, 1000)
        })
      }
    },
    methods: {
      captureFrame () {
        // capture camera frame
        console.log('capturing frame...')
        this.context.drawImage(this.video, 0, 0, this.video.width, this.video.height)
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
    height: 180px;
  }

  video {
    width: 240px;
    height: 180px;
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
    width: 500px;
  }

  .history {
    text-align: left;
    padding-left: 5%;
    img {
      width: 15%;

      height: auto;
      &:not(:last-child) {
        margin-right: 5%;
      }
    }
  }
</style>
