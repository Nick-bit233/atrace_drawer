<template>
    <div class="space-y-4">
      <label class="block text-sm font-medium text-gray-700">上传图片</label>
      <input
        type="file"
        accept="image/png, image/jpeg"
        @change="handleFileUpload"
        class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
      />
      <img v-if="previewImage" :src="previewImage" class="mt-2 max-h-40 rounded-lg border" />
    </div>
  </template>
  
  <script setup>
  import { defineEmits, defineProps } from 'vue'
  
  const props = defineProps({
    previewImage: String
  })
  
  const emit = defineEmits(['update:previewImage', 'upload'])
  
  const handleFileUpload = (e) => {
    const file = e.target.files[0]
    if (!file) return
  
    const reader = new FileReader()
    reader.onload = (e) => {
      emit('update:previewImage', e.target.result)
      emit('upload', file)
    }
    reader.readAsDataURL(file)
  }
  </script>