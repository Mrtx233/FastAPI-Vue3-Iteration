<template>
  <el-table :data="tableData" v-loading="loading" stripe style="width: 100%" max-height="600" empty-text="暂无数据">
    <el-table-column
      v-for="col in columns"
      :key="col.prop"
      :prop="col.prop"
      :label="col.label"
      :min-width="col.width || 140"
      show-overflow-tooltip
    />
  </el-table>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  fetchFn: { type: Function, required: true },
  columns: { type: Array, required: true },
})

const loading = ref(false)
const tableData = ref([])

async function loadData() {
  loading.value = true
  try {
    const res = await props.fetchFn()
    tableData.value = res.data
  } catch {
    ElMessage.error('加载数据失败')
    tableData.value = []
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
watch(() => props.fetchFn, loadData)

defineExpose({ reload: loadData })
</script>
