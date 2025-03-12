<template>
  <div class="canvas-preview-container">
    <h2 class="main-title">转换预览</h2>
    <!-- Canvas comparison layout -->
    <div class="canvas-comparison">
      <!-- 原始图片预览 -->
      <div class="canvas-column">
        <h3 class="canvas-title">原始图片</h3>
        <div class="canvas-wrapper">
          <canvas ref="originalCanvas" class="canvas-display" />
        </div>
      </div>

      <!-- 生成线段预览 -->
      <div class="canvas-column">
        <h3 class="canvas-title">Traces</h3>
        <div class="canvas-wrapper">
          <canvas ref="vectorCanvas" class="canvas-display" />
        </div>
      </div>
    </div>
  </div>
</template>
  
<script setup>
import { ref, watch, onMounted } from 'vue'
import { drawImage, drawInstructions } from '../utils/canvasUtils'
  
const props = defineProps({
  originalImage: String,
  instructions: Array,
  params: Object,
  maxHeight: {
    type: Number,
    default: 600 // 默认最大高度为600px
  }
})
  
const originalCanvas = ref(null)
const vectorCanvas = ref(null)
  
// 绘图逻辑
const renderPreviews = async () => {
  if (!props.originalImage) return
    
  const ctxOriginal = originalCanvas.value.getContext('2d')
  const ctxVector = vectorCanvas.value.getContext('2d')
    
  // 创建图像对象以获取原始尺寸
  const img = new Image()
  img.src = props.originalImage
  await new Promise(resolve => {
    img.onload = resolve
  })
    
  // 计算并设置保持原始比例的画布尺寸，但不超过最大高度
  const setCanvasSize = (canvas) => {
    const containerWidth = canvas.parentElement.clientWidth
    const aspectRatio = img.height / img.width
    
    // 先根据容器宽度计算高度
    let canvasWidth = containerWidth
    let canvasHeight = containerWidth * aspectRatio
    
    // 如果计算出的高度超过最大高度，则按最大高度重新计算宽度
    if (canvasHeight > props.maxHeight) {
      canvasHeight = props.maxHeight
      canvasWidth = canvasHeight / aspectRatio
    }
    
    canvas.width = canvasWidth
    canvas.height = canvasHeight
    
    // 设置样式宽度以确保在DOM中也是正确大小
    canvas.style.width = `${canvasWidth}px`
    canvas.style.height = `${canvasHeight}px`
  }
    
  setCanvasSize(originalCanvas.value)
  setCanvasSize(vectorCanvas.value)
    
  // 清空画布
  ctxOriginal.clearRect(0, 0, originalCanvas.value.width, originalCanvas.value.height)
  ctxVector.clearRect(0, 0, vectorCanvas.value.width, vectorCanvas.value.height)
    
  // 绘制原始图片
  drawImage(ctxOriginal, props.originalImage)
  // 绘制矢量线段
  drawInstructions(ctxVector, props.instructions, props.params)
}
  
// 窗口大小变化时重新渲染以保持响应式
window.addEventListener('resize', renderPreviews)
  
// 监听参数变化自动重绘
watch(() => [props.originalImage, props.instructions, props.params, props.maxHeight], renderPreviews, { deep: true })
onMounted(renderPreviews)
</script>

<style scoped>
.canvas-preview-container {
  width: 96%;
  padding: 2%;
  background-color: rgb(230, 229, 216);
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  border: 2px solid #e0e0e0;
  margin-bottom: 20px;
}

.main-title {
  text-align: center;
  margin-bottom: 20px;
  color: #333;
  font-size: 1.5rem;
}

.canvas-comparison {
  display: flex;
  flex-direction: row;
  gap: 20px;
  width: 100%;
  align-items: flex-start; /* Align items to the top */
}

.canvas-column {
  flex: 1;
  min-width: 0; /* Prevent flex items from overflowing */
  display: flex;
  flex-direction: column;
  align-items: center; /* Center the canvas horizontally */
  border-radius: 0px;
  padding: 6px;
}

.canvas-title {
  text-align: center;
  margin-bottom: 2px;
  font-weight: 500;
  width: 100%;
  color: #444;
}

.canvas-wrapper {
  display: flex;
  justify-content: center;
  width: 100%;
  max-height: 600px;
  border-radius: 4px;
  overflow: hidden;
  background-color: white;
  border: 2px solid #ddd;
}

.canvas-display {
  max-width: 100%;
  max-height: 600px;
  object-fit: contain;
}

/* Mobile responsiveness */
@media (max-width: 767px) {
  .canvas-comparison {
    flex-direction: column;
  }
  
  .canvas-column {
    margin-bottom: 15px;
  }
}
</style>