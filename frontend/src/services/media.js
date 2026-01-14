export class AudioRecorder {
  constructor() {
    this.mediaRecorder = null
    this.audioChunks = []
    this.stream = null
  }

  async startRecording() {
    try {
      this.stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      this.mediaRecorder = new MediaRecorder(this.stream)
      this.audioChunks = []

      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.audioChunks.push(event.data)
        }
      }

      this.mediaRecorder.start()
      return true
    } catch (error) {
      console.error('Error starting recording:', error)
      return false
    }
  }

  async stopRecording() {
    return new Promise((resolve) => {
      if (!this.mediaRecorder || this.mediaRecorder.state === 'inactive') {
        resolve(null)
        return
      }

      this.mediaRecorder.onstop = () => {
        const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' })
        this.cleanup()
        resolve(audioBlob)
      }

      this.mediaRecorder.stop()
    })
  }

  cleanup() {
    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop())
      this.stream = null
    }
    this.audioChunks = []
  }

  isRecording() {
    return this.mediaRecorder && this.mediaRecorder.state === 'recording'
  }
}

export class CameraCapture {
  constructor() {
    this.videoElement = null
    this.stream = null
  }

  async startCamera(videoElement) {
    try {
      this.videoElement = videoElement
      this.stream = await navigator.mediaDevices.getUserMedia({ 
        video: { facingMode: 'user' } 
      })
      this.videoElement.srcObject = this.stream
      await this.videoElement.play()
      return true
    } catch (error) {
      console.error('Error starting camera:', error)
      return false
    }
  }

  captureSnapshot() {
    if (!this.videoElement) return null

    const canvas = document.createElement('canvas')
    canvas.width = this.videoElement.videoWidth
    canvas.height = this.videoElement.videoHeight
    const ctx = canvas.getContext('2d')
    ctx.drawImage(this.videoElement, 0, 0)

    return canvas.toDataURL('image/jpeg', 0.8).split(',')[1] // base64
  }

  stopCamera() {
    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop())
      this.stream = null
    }
    if (this.videoElement) {
      this.videoElement.srcObject = null
    }
  }
}
