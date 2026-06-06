<template>
  <div class="field-upload">
    <el-upload
      class="upload-dragger"
      drag
      :action="uploadUrl"
      :headers="headers"
      :show-file-list="false"
      :before-upload="beforeUpload"
      :on-success="onSuccess"
      :on-error="onError"
      accept="image/*"
    >
      <div v-if="modelValue" class="upload-preview">
        <img :src="fullUrl(modelValue)" class="preview-img" />
        <div class="preview-overlay">
          <span>点击或拖拽替换</span>
        </div>
      </div>
      <div v-else class="upload-placeholder">
        <el-icon class="upload-icon"><Plus /></el-icon>
        <span class="upload-text">拖拽图片到此处，或<em>点击上传</em></span>
      </div>
    </el-upload>
    <div v-if="modelValue" class="upload-info">
      <span class="upload-path" :title="modelValue">{{ modelValue }}</span>
      <el-button link type="danger" size="small" @click.stop="handleClear">清除</el-button>
    </div>
    <div v-if="uploading" class="upload-loading">上传中...</div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getToken } from '../api'
import { decrypt } from '../utils/crypto'

const props = defineProps({
  modelValue: { type: String, default: '' },
})
const emit = defineEmits(['update:modelValue'])

const uploading = ref(false)
const BASE = 'http://localhost:8001'
const uploadUrl = `${BASE}/api/upload/`

const headers = computed(() => {
  const token = getToken()
  return token ? { Authorization: `Bearer ${token}` } : {}
})

function fullUrl(path) {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return BASE + path
}

function beforeUpload(file) {
  const allowed = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml', 'image/bmp']
  if (!allowed.includes(file.type)) {
    ElMessage.error('不支持的图片格式，请上传 JPG/PNG/GIF/WebP/SVG/BMP')
    return false
  }
  if (file.size > 10 * 1024 * 1024) {
    ElMessage.error('图片不能超过 10 MB')
    return false
  }
  uploading.value = true
  return true
}

function onSuccess(response) {
  uploading.value = false
  try {
    let data = response
    // 响应经过 AES 加密中间件，格式为 {data: "<encrypted-base64>"}
    if (response && typeof response.data === 'string' && !response.url) {
      const decrypted = decrypt(response.data)
      data = JSON.parse(decrypted)
    }
    if (data && data.url) {
      emit('update:modelValue', data.url)
      ElMessage.success('上传成功')
    } else {
      console.warn('上传响应异常:', response)
      ElMessage.error('上传响应格式异常')
    }
  } catch (e) {
    console.error('解析上传响应失败:', e)
    ElMessage.error('上传响应解析失败')
  }
}

function onError() {
  uploading.value = false
  ElMessage.error('上传失败，请重试')
}

function handleClear() {
  emit('update:modelValue', '')
}
</script>

<style scoped>
.field-upload {
  width: 100%;
}

.upload-dragger {
  width: 100%;
}

.upload-dragger :deep(.el-upload) {
  width: 100%;
}

.upload-dragger :deep(.el-upload-dragger) {
  width: 100%;
  padding: 0;
  border-radius: 12px;
  border: 2px dashed #d0ddd5;
  transition: border-color 0.25s;
  overflow: hidden;
}

.upload-dragger :deep(.el-upload-dragger:hover) {
  border-color: #3b9d6a;
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 28px 16px;
  gap: 8px;
}

.upload-icon {
  font-size: 36px;
  color: #a3c4b3;
}

.upload-text {
  font-size: 13px;
  color: #7a9a8a;
}

.upload-text em {
  color: #3b9d6a;
  font-style: normal;
  font-weight: 700;
}

.upload-preview {
  position: relative;
  width: 100%;
  min-height: 140px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f9f7;
}

.preview-img {
  max-width: 100%;
  max-height: 220px;
  object-fit: contain;
}

.preview-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.35);
  opacity: 0;
  transition: opacity 0.25s;
  color: #fff;
  font-size: 13px;
  font-weight: 700;
}

.upload-preview:hover .preview-overlay {
  opacity: 1;
}

.upload-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 6px;
  padding: 0 2px;
}

.upload-path {
  font-size: 12px;
  color: #7a9a8a;
  max-width: 260px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.upload-loading {
  margin-top: 6px;
  font-size: 12px;
  color: #3b9d6a;
  font-weight: 700;
}
</style>
