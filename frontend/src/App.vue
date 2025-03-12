<template>
  <div class="min-h-screen bg-gray-100 p-8">
    <!-- 标题 -->
    <h1 class="text-3xl font-bold text-gray-800 mb-8">Image to Vector Converter</h1>

    <!-- 主要布局 -->
    <div class="flex flex-col lg:flex-row gap-8">
      <!-- 左侧控制面板 -->
      <div class="w-full lg:w-96 space-y-6">
        <ImageUploader v-model:previewImage="previewImage" @upload="handleUpload" />
        <ParameterControls
          v-model:params="params"
          :processing="isProcessing"
          @regenerate="generateInstructions"
        />
      </div>

      <!-- 右侧预览区 -->
      <div class="flex-1">
        <CanvasPreview
          :originalImage="previewImage"
          :instructions="instructions"
          :params="params"
          class="border rounded-lg bg-white p-4 shadow-sm"
        />
        
        <!-- 指令输出 -->
        <div class="mt-6 bg-white rounded-lg shadow-sm p-4">
          <div class="flex justify-between items-center mb-4">
            <h3 class="font-semibold">Generated Instructions ({{ instructions.length }})</h3>
            <button @click="copyAll" class="text-blue-600 hover:text-blue-800">
              Copy All
            </button>
          </div>
          <ul class="max-h-96 overflow-y-auto space-y-2">
            <li
              v-for="(line, index) in instructions"
              :key="index"
              class="font-mono text-sm p-2 hover:bg-gray-50 cursor-pointer"
              @click="copySingle(line)"
            >
              {{ line }}
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useToast } from 'vue-toast-notification'
import ImageUploader from './components/ImageUploader.vue'
import ParameterControls from './components/ParameterControls.vue'
import CanvasPreview from './components/CanvasPreview.vue'
import { fetchInstructions } from './utils/api'

const $toast = useToast()

// 响应式状态
const previewImage = ref(null)
const params = ref({
  method: 'edge',
  sampling_rate: 0.05,
  origin_x: 0,
  origin_y: 0,
  scale: 1,
  time_s: 0,
  time_e: 0
})
const instructions = ref([])
const isProcessing = ref(false)

// 处理图片上传
const handleUpload = (file) => {
  const reader = new FileReader()
  reader.onload = (e) => previewImage.value = e.target.result
  reader.readAsDataURL(file)
}

// 获取指令
const generateInstructions = async () => {
  try {
    isProcessing.value = true
    
    // 创建一个超时Promise
    const timeout = new Promise((_, reject) => {
      setTimeout(() => reject(new Error('Request timed out. Server may be busy.')), 10000); // 30秒超时
    });
    
    // 原始请求Promise
    const request = fetchInstructions(previewImage.value, params.value);
    
    // 使用Promise.race竞争，哪个先完成就用哪个结果
    const response = await Promise.race([request, timeout]);
    instructions.value = response.instructions;
  } catch (error) {
    $toast.error(error.message || 'An error occurred while processing the image');
    console.error('Error generating instructions:', error);
  } finally {
    isProcessing.value = false;
  }
}

// 复制功能
const copySingle = (text) => navigator.clipboard.writeText(text)
const copyAll = () => navigator.clipboard.writeText(instructions.value.join('\n'))
</script>