<template>
  <div id="app">
    <div>
      <h1>File uploader</h1>
      <input type="file" @change="onFileChanged">
	  <button @click="onUpload">Upload!</button>
    </div>
    <div v-for="image in images">
      <img id="input-image" :src="image.base64Image || 'https://via.placeholder.com/240x180'">
      <img id="output-image" :src="image.responseImage || 'https://via.placeholder.com/240x180'">
      <h3 class="text-center">{{ image.actorName }}</h3>
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
        images: [],
        tmpImage: null,
        modelLoaded: false,
        cameraLoaded: false,
        selectedFile: null
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
    methods: {
	  onFileChanged (event) {
    	this.selectedFile = event.target.files[0]
    	const reader = new FileReader();
        reader.readAsDataURL(this.selectedFile)
        reader.onloadend = () => {
          this.tmpImage = {
          	base64Image: reader.result
          };
        }
	  },
	  onUpload() {
	    const data = new FormData()
	    data.append('photo', this.selectedFile)
	    axios.post(API_URL + '/process', data, {
          headers: {'Content-Type': 'multipart/form-data'}
        }).then(response => {
          console.log(response)
          if (response.data.photo) {
            this.tmpImage["responseImage"] = `${API_URL}/${response.data.photo}`
            this.tmpImage["actorName"] = response.data.name
            this.images.push(this.tmpImage)
          } else {
            this.responseImage = null
            this.actorName = null
          }
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
    width: 240px;
    height: 180px;
  }
</style>
