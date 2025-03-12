import axios from 'axios'

export const fetchInstructions = async (imageFile, params) => {
  const formData = new FormData()
  formData.append('image', dataURLtoFile(imageFile))
  Object.entries(params).forEach(([key, val]) => formData.append(key, val))

  const response = await axios.post('http://127.0.0.1:5000/process', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  
  if (response.data.status !== 'success') {
    throw new Error(response.data.message || 'Processing failed')
  }
  return response.data
}

// DataURL转File对象
const dataURLtoFile = (dataurl) => {
  const arr = dataurl.split(',')
  const mime = arr[0].match(/:(.*?);/)[1]
  const bstr = atob(arr[1])
  let n = bstr.length
  const u8arr = new Uint8Array(n)
  while (n--) u8arr[n] = bstr.charCodeAt(n)
  return new File([u8arr], 'image.png', { type: mime })
}