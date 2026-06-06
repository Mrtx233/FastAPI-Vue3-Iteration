<template>
  <div class="data-explorer">
    <!-- 工具栏 -->
    <div v-if="crudEnabled || getByIdFn" class="explorer-toolbar">
      <el-button v-if="createFn" type="primary" @click="openCreateDialog">
        新增
      </el-button>
      <template v-if="getByIdFn">
        <el-input
          v-model="searchId"
          :placeholder="idSearchLabel"
          class="id-search"
          clearable
          @keyup.enter="handleSearchById"
          @clear="handleSearchClear"
        />
        <el-button type="success" @click="handleSearchById">按 ID 查询</el-button>
        <el-button v-if="isSearchMode" @click="handleSearchClear">返回全部</el-button>
      </template>
    </div>

    <!-- 数据表格 -->
    <div class="table-panel">
      <div class="table-summary">
        <span>{{ isSearchMode ? '查询结果' : '全部记录' }}</span>
        <strong>{{ tableData.length }}</strong>
      </div>
      <el-table
        :data="tableData"
        v-loading="loading"
        stripe
        class="explorer-table"
        max-height="600"
        :empty-text="emptyText"
      >
        <el-table-column
          v-for="col in columns"
          :key="col.prop"
          :prop="col.prop"
          :label="col.label"
          :min-width="col.width || 140"
          show-overflow-tooltip
        />
        <!-- 操作列 -->
        <el-table-column v-if="updateFn || deleteFn" label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button v-if="updateFn" size="small" @click="openEditDialog(row)">编辑</el-button>
            <el-popconfirm
              v-if="deleteFn"
              title="确认删除此记录？"
              confirm-button-text="确定"
              cancel-button-text="取消"
              @confirm="handleDelete(row)"
            >
              <template #reference>
                <el-button size="small" type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 新增/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑' : '新增'"
      width="520px"
      destroy-on-close
      class="data-dialog"
    >
      <el-form :model="formData" label-width="110px" class="data-form">
        <el-form-item
          v-for="field in activeFields"
          :key="field.prop"
          :label="field.label"
        >
          <!-- 下拉选择 -->
          <el-select
            v-if="field.type === 'select'"
            v-model="formData[field.prop]"
            :placeholder="'请选择' + field.label"
            style="width: 100%"
            clearable
          >
            <el-option
              v-for="opt in field.options"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>
          <!-- 数字输入 -->
          <el-input-number
            v-else-if="field.type === 'number'"
            v-model="formData[field.prop]"
            :placeholder="'请输入' + field.label"
            style="width: 100%"
            :min="field.min"
            :max="field.max"
          />
          <!-- 日期选择 -->
          <el-date-picker
            v-else-if="field.type === 'date'"
            v-model="formData[field.prop]"
            type="date"
            :placeholder="'请选择' + field.label"
            style="width: 100%"
            value-format="YYYY-MM-DD"
          />
          <!-- 日期时间选择 -->
          <el-date-picker
            v-else-if="field.type === 'datetime'"
            v-model="formData[field.prop]"
            type="datetime"
            :placeholder="'请选择' + field.label"
            style="width: 100%"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
          <!-- 多行文本 -->
          <el-input
            v-else-if="field.type === 'textarea'"
            v-model="formData[field.prop]"
            type="textarea"
            :rows="3"
            :placeholder="'请输入' + field.label"
          />
          <!-- 密码输入 -->
          <el-input
            v-else-if="field.type === 'password'"
            v-model="formData[field.prop]"
            type="password"
            show-password
            :placeholder="'请输入' + field.label"
          />
          <!-- 默认文本 -->
          <el-input
            v-else
            v-model="formData[field.prop]"
            :placeholder="'请输入' + field.label"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  fetchFn: { type: Function, required: true },
  columns: { type: Array, required: true },
  // CRUD 相关（可选）
  createFn: { type: Function, default: null },
  updateFn: { type: Function, default: null },
  deleteFn: { type: Function, default: null },
  // 按 ID 查询
  getByIdFn: { type: Function, default: null },
  idSearchLabel: { type: String, default: '输入 ID 查询' },
  // 表单字段定义
  createFields: { type: Array, default: () => [] },
  editFields: { type: Array, default: () => [] },
  // 主键字段名
  idProp: { type: String, default: 'id' },
})

const crudEnabled = computed(() => !!(props.createFn || props.updateFn || props.deleteFn))

const loading = ref(false)
const tableData = ref([])
const emptyText = ref('暂无数据')

// 弹窗相关
const dialogVisible = ref(false)
const isEdit = ref(false)
const formData = ref({})
const submitting = ref(false)
let editingRow = null

const activeFields = computed(() => isEdit.value ? props.editFields : props.createFields)

// 按 ID 查询相关
const searchId = ref('')
const isSearchMode = ref(false)

async function loadData() {
  loading.value = true
  emptyText.value = '暂无数据'
  isSearchMode.value = false
  try {
    const res = await props.fetchFn()
    tableData.value = res.data
  } catch (e) {
    tableData.value = []
    if (e.response && e.response.status === 403) {
      emptyText.value = '权限不足，无法访问此数据'
    } else {
      emptyText.value = '加载失败'
    }
  } finally {
    loading.value = false
  }
}

async function handleSearchById() {
  if (!props.getByIdFn || !searchId.value) return
  loading.value = true
  isSearchMode.value = false
  try {
    const res = await props.getByIdFn(Number(searchId.value))
    tableData.value = [res.data]
    isSearchMode.value = true
    emptyText.value = '未找到该记录'
  } catch (e) {
    tableData.value = []
    const detail = e.response?.data?.detail || e.message || '查询失败'
    ElMessage.error(detail)
  } finally {
    loading.value = false
  }
}

async function handleSearchClear() {
  searchId.value = ''
  isSearchMode.value = false
  await loadData()
}

function openCreateDialog() {
  isEdit.value = false
  editingRow = null
  // 初始化默认值
  const init = {}
  props.createFields.forEach(f => {
    init[f.prop] = f.default ?? (f.type === 'number' ? undefined : '')
  })
  formData.value = init
  dialogVisible.value = true
}

function openEditDialog(row) {
  isEdit.value = true
  editingRow = row
  const init = {}
  props.editFields.forEach(f => {
    init[f.prop] = row[f.prop] ?? (f.type === 'number' ? undefined : '')
  })
  formData.value = init
  dialogVisible.value = true
}

async function handleSubmit() {
  submitting.value = true
  try {
    if (isEdit.value && props.updateFn) {
      await props.updateFn(editingRow[props.idProp], formData.value)
      ElMessage.success('编辑成功')
    } else if (!isEdit.value && props.createFn) {
      await props.createFn(formData.value)
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
    await loadData()
  } catch (e) {
    const detail = e.response?.data?.detail || '操作失败'
    ElMessage.error(detail)
  } finally {
    submitting.value = false
  }
}

async function handleDelete(row) {
  if (!props.deleteFn) return
  try {
    await props.deleteFn(row[props.idProp])
    ElMessage.success('删除成功')
    await loadData()
  } catch (e) {
    const detail = e.response?.data?.detail || '删除失败'
    ElMessage.error(detail)
  }
}

onMounted(loadData)
watch(() => props.fetchFn, loadData)

defineExpose({ reload: loadData })
</script>

<style scoped>
.data-explorer {
  min-width: 0;
}

.explorer-toolbar {
  margin-bottom: 14px;
  padding: 14px;
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
  border: 1px solid var(--fm-border);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.78);
  box-shadow: 0 8px 24px rgba(20, 33, 28, 0.05);
}

.id-search {
  width: 220px;
}

.table-panel {
  overflow: hidden;
  border: 1px solid var(--fm-border);
  border-radius: 18px;
  background: #fff;
  box-shadow: var(--fm-shadow-card);
}

.table-summary {
  min-height: 50px;
  padding: 0 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--fm-border);
  background: #fbfdfb;
}

.table-summary span {
  color: var(--fm-muted);
  font-size: 13px;
  font-weight: 800;
}

.table-summary strong {
  color: var(--fm-accent-strong);
  font-size: 20px;
}

.explorer-table {
  width: 100%;
  border: none;
  border-radius: 0;
}

.data-form {
  max-height: 60vh;
  padding-right: 8px;
  overflow-y: auto;
}

@media (max-width: 640px) {
  .explorer-toolbar {
    align-items: stretch;
    flex-direction: column;
  }

  .explorer-toolbar :deep(.el-button),
  .id-search {
    width: 100%;
  }
}
</style>
