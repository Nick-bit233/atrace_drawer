<template>
  <div class="bg-white rounded-lg shadow-sm p-4 space-y-4">
    <h3 class="font-medium text-gray-700 mb-2">参数设置</h3>

    <!-- 时间轴位置start -->
    <div>
        <div class="flex justify-between">
            <label class="block text-sm font-medium text-gray-700">时间轴开始</label>
            <span class="text-xs text-gray-500">{{ params.time_s }}</span>
        </div>
        <div class="flex items-center space-x-2">
            <input
                type="number"
                v-model.number="params.time_s"
                min="0"
                max="100000"
                step="1"
                class="w-16 px-2 py-1 text-xs border rounded"
            />
        </div>
    </div>

    <!-- 时间轴位置end -->
        <div>
        <div class="flex justify-between">
            <label class="block text-sm font-medium text-gray-700">时间轴结束</label>
            <span class="text-xs text-gray-500">{{ params.time_e }}</span>
        </div>
        <div class="flex items-center space-x-2">
            <input
                type="number"
                v-model.number="params.time_e"
                min="0"
                max="100000"
                step="1"
                class="w-16 px-2 py-1 text-xs border rounded"
            />
        </div>
    </div>

    <!-- 采样率 -->
    <div>
      <div class="flex justify-between">
        <label class="block text-sm font-medium text-gray-700">采样率</label>
        <span class="text-xs text-gray-500">{{ params.sampling_rate.toFixed(3) }}</span>
      </div>
      <div class="flex items-center space-x-2">
        <input
          type="range"
          v-model.number="params.sampling_rate"
          min="0.001"
          max="0.01"
          step="0.0001"
          class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
        />
        <input
          type="number"
          v-model.number="params.sampling_rate"
          min="0.001"
          max="0.01"
          step="0.0001"
          class="w-16 px-2 py-1 text-xs border rounded"
        />
      </div>
    </div>

    <!-- 原点 X -->
    <div>
      <div class="flex justify-between">
        <label class="block text-sm font-medium text-gray-700">原点 X</label>
        <span class="text-xs text-gray-500">{{ params.origin_x }}</span>
      </div>
      <div class="flex items-center space-x-2">
        <input
          type="range"
          v-model.number="params.origin_x"
          min="-1"
          max="2"
          step="0.01"
          class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
        />
        <input
          type="number"
          v-model.number="params.origin_x"
          min="-1"
          max="2"
          step="0.01"
          class="w-16 px-2 py-1 text-xs border rounded"
        />
      </div>
    </div>

    <!-- 原点 Y -->
    <div>
      <div class="flex justify-between">
        <label class="block text-sm font-medium text-gray-700">原点 Y</label>
        <span class="text-xs text-gray-500">{{ params.origin_y }}</span>
      </div>
      <div class="flex items-center space-x-2">
        <input
          type="range"
          v-model.number="params.origin_y"
          min="0"
          max="2"
          step="0.01"
          class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
        />
        <input
          type="number"
          v-model.number="params.origin_y"
          min="0"
          max="2"
          step="0.01"
          class="w-16 px-2 py-1 text-xs border rounded"
        />
      </div>
    </div>

    <!-- 缩放比例 -->
    <div>
      <div class="flex justify-between">
        <label class="block text-sm font-medium text-gray-700">缩放比例</label>
        <span class="text-xs text-gray-500">{{ params.scale.toFixed(2) }}</span>
      </div>
      <div class="flex items-center space-x-2">
        <input
          type="range"
          v-model.number="params.scale"
          min="0.1"
          max="5"
          step="0.1"
          class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
        />
        <input
          type="number"
          v-model.number="params.scale"
          min="0.1"
          max="5"
          step="0.1"
          class="w-16 px-2 py-1 text-xs border rounded"
        />
      </div>
    </div>

    <!-- 生成方法 -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-2">生成方法</label>
      <div class="flex space-x-4">
        <label class="inline-flex items-center">
          <input
            type="radio"
            v-model="params.method"
            value="contour"
            class="form-radio h-4 w-4 text-blue-600"
          />
          <span class="ml-2 text-sm text-gray-700">边缘轮廓</span>
        </label>
        <label class="inline-flex items-center">
          <input
            type="radio"
            v-model="params.method"
            value="thinning"
            class="form-radio h-4 w-4 text-blue-600"
          />
          <span class="ml-2 text-sm text-gray-700">骨架化</span>
        </label>
      </div>
    </div>

    <!-- 显示模式 -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-2">表示模式</label>
      <div class="flex space-x-4">
        <label class="inline-flex items-center">
          <input
            type="radio"
            v-model="params.mode"
            value="vertical"
            class="form-radio h-4 w-4 text-blue-600"
          />
          <span class="ml-2 text-sm text-gray-700">垂直</span>
        </label>
        <label class="inline-flex items-center">
          <input
            type="radio"
            v-model="params.mode"
            value="timeline"
            class="form-radio h-4 w-4 text-blue-600"
          />
          <span class="ml-2 text-sm text-gray-700">时间轴</span>
        </label>
      </div>
    </div>

    <!-- 重新生成按钮 -->
    <button
      @click="regenerate"
      class="w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-md shadow-sm disabled:bg-blue-300 disabled:cursor-not-allowed transition-colors"
      :disabled="processing"
    >
      {{ processing ? '处理中...' : '生成矢量图' }}
    </button>
  </div>
</template>

<script setup>
import { defineProps, defineEmits, ref, watch } from 'vue'

const props = defineProps({
  params: {
    type: Object,
    required: true,
    default: () => ({
      method: 'contour',
      mode: 'vertical',
      sampling_rate: 0.01,
      origin_x: 0,
      origin_y: 0,
      scale: 1,
      time_s: 0,
      time_e: 0
    })
  },
  processing: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:params', 'regenerate'])

// 使用本地副本进行双向绑定
const params = ref({ ...props.params })

// 监听本地参数变化，向父组件发射更新事件
watch(params, (newParams) => {
  emit('update:params', { ...newParams })
}, { deep: true })

// 监听父组件传入的参数变化，更新本地参数
watch(() => props.params, (newParams) => {
  params.value = { ...newParams }
}, { deep: true })

// 触发重新生成事件
const regenerate = () => {
  emit('regenerate')
}
</script>
