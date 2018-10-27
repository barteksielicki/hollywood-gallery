const app = new Vue({
    el: "#app",
    data () {
        return {
            requestImage: null,
            responseImageSrc: null,
        }
    },
    computed: {
      requestImageSrc () {
          return this.requestImage && URL.createObjectURL(this.requestImage)
      }
    },
    methods: {
        handleNewImage (e) {
            this.requestImage = e.target.files[0]
        },
        uploadImage () {
            const data = new FormData()
            data.append('photo', this.requestImage)
            axios.post('/process', data, {
                headers: {'Content-Type': 'multipart/form-data'}
            }).then(response => {
                console.log(response)
                if (response.data.photo) {
                    this.responseImageSrc = response.data.photo
                } else {
                    alert("Face was not found!")
                    this.responseImageSrc = null
                }
            })
        }
    }
})