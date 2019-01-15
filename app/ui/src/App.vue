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
        <h3 class="text-center">{{ actorName }}</h3>
      </div>
      <div>
        <h1>Settings</h1>
        <div>
          Actors limit: {{ actorsLimit }}<br>
          <input type="range" min="1" max="18826" v-model="actorsLimit" class="slider">
        </div>
      </div>
    </div>
    <div class="right-panel">
      <div class="right-panel-header">
        <h4>Last 5 actors</h4>
      </div>
      <div v-for="actor in actors_history">
        {{ actor.name }}
      </div>
      <div class="stats">
        <h4>Most appearing actors</h4>
        <div class="stats-list">
          <div v-for="(actor, index) in actors_freq">
            {{index+1}}. {{ actor.name }}: {{ actor.val }}%
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import axios from 'axios'

  const API_URL = 'http://3.121.199.45'

  export default {
    data () {
      return {
        video: null,
        canvas: null,
        context: null,
        blobImage: null,
        base64Image: null,
        responseImage: null,
        actorName: null,
        cameraLoaded: false,
        actorsLimit: 1000,
        actors_history: [],
        n: 0,
        actors_stats: {},
        actors_freq: [],
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

        // send and retrieve result
        const data = new FormData()
        data.append('photo', blob)
        data.append('limit', this.actorsLimit)
        console.log('making request...')
        axios.post(API_URL + '/process', data, {
          headers: {'Content-Type': 'multipart/form-data'}
        }).then(response => {
          if (response.data.photo) {
            this.responseImage = `${API_URL}/${response.data.photo}`
            this.actorName = response.data.name
            this.save_stats(response.data.name)
            this.faceNotDetectedCounter = 0
          } else {
            this.responseImage = null
            this.actorName = null
            this.showWarn('Cannot detect face', 'Try to bring your face closer to the webcam.')
            if (this.faceNotDetectedCounter++ == 10) {
              this.resetStats()
            }
          }
        }).catch(err => {
          this.responseImage = null
          this.actorName = null
          this.showError('Error', 'Something went wrong, please contact serwer administrator.')
        }).finally(() => {
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
      save_stats (name) {
        this.n++
        if (this.actors_history.length == 5) {
          this.actors_history.splice(0, 1)
        }
        this.actors_history.push({name: name})

        if (typeof this.actors_stats[name] === 'undefined') {
          this.actors_stats[name] = 0
        }

        this.actors_stats[name]++

        this.actors_freq = []
        for (let key in this.actors_stats) {
          this.actors_freq.push({name: key, val: Number((this.actors_stats[key] * 100 / this.n).toFixed(1))})
        }

        this.actors_freq.sort(function (obj1, obj2) {
          return obj1.val < obj2.val ? 1 : -1
        })
        this.actors_freq = this.actors_freq.splice(0, 10)
      },
      resetStats () {
        this.n = 0
        this.faceNotDetectedCounter = 0
        this.actors_history = []
        this.actors_stats = {}
        this.actors_freq = []
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

  .right-panel {
    width: 350px;
    border-left: 2px solid #2c3e50;
    height: 100%;
    padding-top: 150px;
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
</style>
