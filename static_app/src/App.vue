<template>
  <div id="app">
    <div>
      <h1>Face detector</h1>
      <img src="https://via.placeholder.com/480x360" v-if="!cameraLoaded">
      <video id="video" width="480" height="360" preload autoplay loop muted v-show="cameraLoaded"></video>
    </div>
    <div>
      <h1>Face processor</h1>
      <img id="input-image" :src="this.base64Image || 'https://via.placeholder.com/480x360'">
      <img id="output-image" :src="this.responseImage || 'https://via.placeholder.com/480x360'">
    </div>
  </div>
</template>

<script>
  const API_URL = 'http://localhost:8000'
  import axios from 'axios'

  export default {
    data () {
      return {
        video: null,
        canvas: null,
        context: null,
        blobImage: null,
        base64Image: null,
        responseImage: null,
        modelLoaded: false,
        cameraLoaded: false,
      }
    },
    computed: {
      isReady () {
        return this.modelLoaded && this.cameraLoaded
      }
    },
    mounted () {
      // get camera input
      this.video = document.getElementById('video')

      navigator.mediaDevices.getUserMedia({video: true, audio: false})
        .then(stream => {
          this.video.srcObject = stream
          this.cameraLoaded = true
          this.canvas = document.createElement('canvas');
          this.canvas.width = this.video.width;
          this.canvas.height = this.video.height;
          this.context = this.canvas.getContext('2d')
          console.log("Camera loaded")
        })
        .catch(error => {
          console.log("Error loading camera.", error)
        })

      // load network model
      faceapi.loadSsdMobilenetv1Model('dist/')
        .then(() => {
          this.modelLoaded = true
          console.log("Model loaded")
        })
        .catch(err => {
          console.log("Error loading model.", err)
        })
    },
    watch: {
      isReady (nowReady, wasReady) {
        if (!wasReady && nowReady) {
          console.log("Detecting faces started...")
          setTimeout(this.detectFace, 1000)
        }
      },
      blobImage (blob) {
        // render preview
        const reader = new FileReader();
        reader.readAsDataURL(blob)
        reader.onloadend = () => {
          this.base64Image = reader.result
        }
        // send and retrieve result
        const data = new FormData()
        data.append('photo', blob)
        axios.post(API_URL + '/process', data, {
          headers: {'Content-Type': 'multipart/form-data'}
        }).then(response => {
          console.log(response)
          if (response.data.photo) {
            this.responseImage = `${API_URL}/${response.data.photo}`
          } else {
            alert("Backend couldn't find face!")
            this.responseImage = null
          }
        })
      }
    },
    methods: {
      detectFace () {
        console.log("detecting...")
        faceapi.detectSingleFace(this.video)
          .then(result => {
            if (result && result.score > 0.5) {
              console.log("Face deteceted.")
              this.context.drawImage(this.video, 0, 0, this.video.width, this.video.height)
              this.canvas.toBlob(blob => {
                this.blobImage = blob
              })
              setTimeout(this.detectFace, 5000)
            } else {
              console.log("Face was not detected.")
              this.blobImage = null
              this.base64Image = null
              this.responseImage = null
              setTimeout(this.detectFace, 1000)
            }
          })
          .catch(error => {
            console.log("Error detecting face.", error)
            setTimeout(this.detectFace, 1000)
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
</style>
