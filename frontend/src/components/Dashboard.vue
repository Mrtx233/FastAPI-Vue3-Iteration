<template>
  <el-container class="dashboard-shell">
    <!-- 侧边栏 -->
    <el-aside width="248px" class="dashboard-aside">
      <div class="aside-title">
        <span>数据目录</span>
        <small>{{ menuGroups.length }} 组模块</small>
      </div>
      <el-menu :default-active="activeKey" @select="onSelect" class="dashboard-menu">
        <el-sub-menu v-for="group in menuGroups" :key="group.key" :index="group.key">
          <template #title>
            <span class="menu-group-title">{{ group.label }}</span>
          </template>
          <el-menu-item v-for="item in group.children" :key="item.key" :index="item.key">
            {{ item.label }}
          </el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>

    <!-- 内容区 -->
    <el-main class="dashboard-main">
      <template v-if="activeKey">
        <div class="dashboard-heading">
          <div>
            <span class="heading-kicker">当前数据表</span>
            <h3>{{ activeConfig.label }}</h3>
          </div>
          <span class="heading-pill">{{ activeKey }}</span>
        </div>
        <DataExplorer
          :fetch-fn="activeConfig.fetchFn"
          :columns="activeConfig.columns"
          :create-fn="activeConfig.createFn"
          :update-fn="activeConfig.updateFn"
          :delete-fn="activeConfig.deleteFn"
          :get-by-id-fn="activeConfig.getByIdFn"
          :id-search-label="activeConfig.idSearchLabel"
          :create-fields="activeConfig.createFields"
          :edit-fields="activeConfig.editFields"
          :id-prop="activeConfig.idProp"
          :key="activeKey"
        />
      </template>
      <div v-else class="dashboard-empty">
        <div class="empty-mark">FM</div>
        <h3>选择一个数据表开始管理</h3>
        <p>左侧目录按照系统、门店、课程、动作和内容组织，适合快速巡检和维护业务数据。</p>
      </div>
    </el-main>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import DataExplorer from '../components/DataExplorer.vue'
import * as api from '../api'
import { getToken } from '../api'

const props = defineProps({
  menuGroups: { type: Array, required: true },
  canDeleteUser: { type: Boolean, default: true },
  loadDropdowns: { type: Boolean, default: false },
})

// 从 JWT 中提取用户信息
function decodeJwtPayload() {
  try {
    const token = getToken()
    if (!token) return null
    const payload = JSON.parse(atob(token.split('.')[1]))
    return { user_id: parseInt(payload.sub), role_id: payload.role_id, username: payload.username }
  } catch { return null }
}

// 缓存角色和权限列表（用于下拉选择）
const roleOptions = ref([])
const permOptions = ref([])
const userOptions = ref([])
const currentUser = ref(null)

// 判断当前页面是否需要加载系统下拉选项（仅超管/运营需要）

onMounted(async () => {
  currentUser.value = decodeJwtPayload()

  // 教练和会员页面不需要加载角色/权限/用户下拉选项
  if (!props.loadDropdowns) return

  try {
    const [rolesRes, permsRes, usersRes] = await Promise.allSettled([
      api.getRoles(),
      api.getPermissions(),
      api.getUsers({ params: { page_size: 999 } }),
    ])
    if (rolesRes.status === 'fulfilled') {
      roleOptions.value = rolesRes.value.data.map(r => ({ label: `${r.role_name} (${r.role_code})`, value: r.id }))
    }
    if (permsRes.status === 'fulfilled') {
      permOptions.value = permsRes.value.data.map(p => ({ label: `${p.permission_name} (${p.permission_code})`, value: p.id }))
    }
    if (usersRes.status === 'fulfilled') {
      const usersList = usersRes.value.data?.items ?? usersRes.value.data
      userOptions.value = usersList.map(u => ({ label: `${u.username}${u.real_name ? ' - ' + u.real_name : ''}`, value: u.user_id }))
    }
  } catch (e) {
    console.warn('加载下拉选项失败:', e)
  }
})

// 判断当前用户是否有 user:list 权限（超管 role_id=1 / 运营 role_id=2）
const hasUserListPerm = () => {
  const role = currentUser.value?.role_id
  return role === 1 || role === 2
}

// 各角色可执行 CRUD 的表（超管拥有全部，运营同超管但不可删除用户）
const roleManageMap = {
  1: null, // 超级管理员：全部可管理
  2: null,
  3: new Set([]), // 教练：系统表只读
  4: new Set([]), // 会员：全部只读
}

const canManageTable = (tableKey) => {
  const roleId = currentUser.value?.role_id
  if (!roleId) return false
  const allowed = roleManageMap[roleId]
  return allowed === null || allowed.has(tableKey) // null = 全部可管理
}

// 用户/用户档案的智能获取（按权限直接选择请求方式，避免产生 403）
const fetchUsersSmart = () => {
  if (hasUserListPerm()) {
    return api.getUsers({ params: { page_size: 999 } }).then(unwrapPaginated)
  }
  // 教练 / 会员：直接查看自己
  return api.getUserById(currentUser.value.user_id).then(res => ({ data: [res.data] }))
}

const fetchProfilesSmart = () => {
  if (hasUserListPerm()) {
    return api.getUserProfiles()
  }
  // 教练 / 会员：直接查看自己的档案
  return api.getUserProfileByUserId(currentUser.value.user_id).then(res => ({ data: [res.data] }))
}

// 分页响应解包：将 {items:[], total, page, page_size} 转为 {data: items}
function unwrapPaginated(res) {
  if (res.data && Array.isArray(res.data.items)) {
    return { data: res.data.items }
  }
  return res
}

// 全部表格配置
const tableConfig = computed(() => ({
  // ========== 系统管理 ==========
  permissions: {
    label: '权限定义 (sys_permission)',
    fetchFn: api.getPermissions,
    idProp: 'id',
    getByIdFn: (id) => api.getPermissionById(id),
    idSearchLabel: '输入权限 ID 查询',
    columns: [
      { prop: 'id', label: 'ID', width: 80 },
      { prop: 'permission_code', label: '权限标识符' },
      { prop: 'permission_name', label: '权限名称' },
      { prop: 'menu_path', label: '前端路由路径' },
    ],
    createFn: (data) => api.createPermission(data),
    updateFn: (id, data) => api.updatePermission(id, data),
    deleteFn: (id) => api.deletePermission(id),
    createFields: [
      { prop: 'permission_code', label: '权限标识符', required: true },
      { prop: 'permission_name', label: '权限名称', required: true },
      { prop: 'menu_path', label: '前端路由路径' },
    ],
    editFields: [
      { prop: 'permission_code', label: '权限标识符' },
      { prop: 'permission_name', label: '权限名称' },
      { prop: 'menu_path', label: '前端路由路径' },
    ],
  },
  roles: {
    label: '角色 (sys_role)',
    fetchFn: api.getRoles,
    idProp: 'id',
    getByIdFn: (id) => api.getRoleById(id),
    idSearchLabel: '输入角色 ID 查询',
    columns: [
      { prop: 'id', label: 'ID', width: 80 },
      { prop: 'role_code', label: '角色代码' },
      { prop: 'role_name', label: '角色名称' },
    ],
    createFn: (data) => api.createRole(data),
    updateFn: (id, data) => api.updateRole(id, data),
    deleteFn: (id) => api.deleteRole(id),
    createFields: [
      { prop: 'role_code', label: '角色代码', required: true },
      { prop: 'role_name', label: '角色名称', required: true },
    ],
    editFields: [
      { prop: 'role_code', label: '角色代码' },
      { prop: 'role_name', label: '角色名称' },
    ],
  },
  role_permissions: {
    label: '角色权限 (sys_role_permission)',
    fetchFn: api.getRolePermissions,
    idProp: 'id',
    columns: [
      { prop: 'id', label: 'ID', width: 80 },
      { prop: 'role_id', label: '角色ID' },
      { prop: 'permission_id', label: '权限ID' },
    ],
    createFn: (data) => api.createRolePermission(data),
    deleteFn: (id) => api.deleteRolePermission(id),
    createFields: [
      { prop: 'role_id', label: '角色', type: 'select', required: true, options: roleOptions.value },
      { prop: 'permission_id', label: '权限', type: 'select', required: true, options: permOptions.value },
    ],
    editFields: [],
  },
  users: {
    label: '用户 (sys_user)',
    fetchFn: fetchUsersSmart,
    idProp: 'user_id',
    getByIdFn: (id) => {
      if (!hasUserListPerm() && currentUser.value && Number(id) !== currentUser.value.user_id) {
        return Promise.reject(new Error('您只能查看自己的信息'))
      }
      return api.getUserById(id)
    },
    idSearchLabel: '输入用户 ID 查询',
    columns: [
      { prop: 'user_id', label: 'ID', width: 80 },
      { prop: 'role_id', label: '角色ID', width: 80 },
      { prop: 'username', label: '用户名' },
      { prop: 'password', label: '密码(加密)', width: 200 },
      { prop: 'real_name', label: '真实姓名' },
      { prop: 'phone', label: '手机号' },
      { prop: 'status', label: '状态', width: 80 },
    ],
    createFn: canManageTable('users') ? ((data) => api.createUser(data)) : null,
    updateFn: canManageTable('users') ? ((id, data) => api.updateUser(id, data)) : null,
    deleteFn: (canManageTable('users') && props.canDeleteUser) ? ((id) => api.deleteUser(id)) : null,
    createFields: [
      { prop: 'role_id', label: '角色', type: 'select', required: true, options: roleOptions.value },
      { prop: 'username', label: '用户名', required: true },
      { prop: 'password', label: '密码', type: 'password', required: true },
      { prop: 'real_name', label: '真实姓名' },
      { prop: 'phone', label: '手机号' },
      { prop: 'status', label: '状态', type: 'select', default: 1, options: [{ label: '启用', value: 1 }, { label: '禁用', value: 0 }] },
    ],
    editFields: [
      { prop: 'role_id', label: '角色', type: 'select', options: roleOptions.value },
      { prop: 'username', label: '用户名' },
      { prop: 'password', label: '新密码(留空不修改)', type: 'password' },
      { prop: 'real_name', label: '真实姓名' },
      { prop: 'phone', label: '手机号' },
      { prop: 'status', label: '状态', type: 'select', options: [{ label: '启用', value: 1 }, { label: '禁用', value: 0 }] },
    ],
  },
  user_profiles: {
    label: '用户档案 (sys_user_profile)',
    fetchFn: fetchProfilesSmart,
    idProp: 'profile_id',
    getByIdFn: (id) => {
      if (!hasUserListPerm() && currentUser.value && Number(id) !== currentUser.value.user_id) {
        return Promise.reject(new Error('您只能查看自己的档案'))
      }
      return api.getUserProfileByUserId(id)
    },
    idSearchLabel: '输入用户 ID 查询',
    columns: [
      { prop: 'profile_id', label: 'ID', width: 80 },
      { prop: 'user_id', label: '用户ID', width: 80 },
      { prop: 'level', label: '等级', width: 70 },
      { prop: 'gender', label: '性别', width: 70 },
      { prop: 'birthday', label: '生日' },
      { prop: 'height_cm', label: '身高cm', width: 80 },
      { prop: 'weight_kg', label: '体重kg', width: 80 },
      { prop: 'avatar_url', label: '头像URL', width: 200 },
      { prop: 'intro', label: '简介' },
      { prop: 'create_time', label: '创建时间' },
      { prop: 'join_time', label: '入职时间' },
      { prop: 'expire_date', label: '到期日期' },
    ],
    createFn: canManageTable('user_profiles') ? ((data) => api.createUserProfile(data)) : null,
    updateFn: canManageTable('user_profiles') ? ((id, data) => api.updateUserProfile(id, data)) : null,
    deleteFn: (canManageTable('user_profiles') && props.canDeleteUser) ? ((id) => api.deleteUserProfile(id)) : null,
    createFields: [
      { prop: 'user_id', label: '用户', type: 'select', required: true, options: userOptions.value },
      { prop: 'level', label: '等级', type: 'number', min: 0, max: 100 },
      { prop: 'gender', label: '性别', type: 'select', options: [{ label: '男', value: 1 }, { label: '女', value: 2 }] },
      { prop: 'birthday', label: '生日', type: 'date' },
      { prop: 'height_cm', label: '身高(cm)', type: 'number' },
      { prop: 'weight_kg', label: '体重(kg)', type: 'number' },
      { prop: 'avatar_url', label: '头像URL' },
      { prop: 'intro', label: '个人简介', type: 'textarea' },
      { prop: 'create_time', label: '创建时间', type: 'datetime' },
      { prop: 'join_time', label: '入职时间', type: 'datetime' },
      { prop: 'expire_date', label: '到期日期', type: 'datetime' },
    ],
    editFields: [
      { prop: 'level', label: '等级', type: 'number', min: 0, max: 100 },
      { prop: 'gender', label: '性别', type: 'select', options: [{ label: '男', value: 1 }, { label: '女', value: 2 }] },
      { prop: 'birthday', label: '生日', type: 'date' },
      { prop: 'height_cm', label: '身高(cm)', type: 'number' },
      { prop: 'weight_kg', label: '体重(kg)', type: 'number' },
      { prop: 'avatar_url', label: '头像URL' },
      { prop: 'intro', label: '个人简介', type: 'textarea' },
      { prop: 'create_time', label: '创建时间', type: 'datetime' },
      { prop: 'join_time', label: '入职时间', type: 'datetime' },
      { prop: 'expire_date', label: '到期日期', type: 'datetime' },
    ],
  },
  // ========== 门店管理 ==========
  provinces: {
    label: '省份区域 (t_store_province)',
    fetchFn: api.getProvinces,
    idProp: 'province_id',
    getByIdFn: (id) => api.getProvinceById(id),
    idSearchLabel: '输入省份 ID 查询',
    columns: [
      { prop: 'province_id', label: 'ID', width: 80 },
      { prop: 'province_name', label: '省份名称' },
      { prop: 'center_lng', label: '中心经度' },
      { prop: 'center_lat', label: '中心纬度' },
    ],
    createFn: canManageTable('provinces') ? ((data) => api.createProvince(data)) : null,
    updateFn: canManageTable('provinces') ? ((id, data) => api.updateProvince(id, data)) : null,
    deleteFn: canManageTable('provinces') ? ((id) => api.deleteProvince(id)) : null,
    createFields: [
      { prop: 'province_name', label: '省份名称', required: true },
      { prop: 'center_lng', label: '中心经度', type: 'number' },
      { prop: 'center_lat', label: '中心纬度', type: 'number' },
    ],
    editFields: [
      { prop: 'province_name', label: '省份名称' },
      { prop: 'center_lng', label: '中心经度', type: 'number' },
      { prop: 'center_lat', label: '中心纬度', type: 'number' },
    ],
  },
  stores: {
    label: '门店信息 (t_store)',
    fetchFn: () => api.getStores({ params: { page_size: 999 } }).then(unwrapPaginated),
    idProp: 'store_id',
    getByIdFn: (id) => api.getStoreById(id),
    idSearchLabel: '输入门店 ID 查询',
    columns: [
      { prop: 'store_id', label: 'ID', width: 80 },
      { prop: 'store_name', label: '门店名称' },
      { prop: 'store_type', label: '类型', width: 70 },
      { prop: 'province_name', label: '省份' },
      { prop: 'city', label: '城市' },
      { prop: 'district', label: '区县' },
      { prop: 'address', label: '地址', width: 200 },
      { prop: 'store_phone', label: '电话' },
      { prop: 'business_hours', label: '营业时间' },
      { prop: 'is_operating', label: '营业', width: 70 },
    ],
    createFn: canManageTable('stores') ? ((data) => api.createStore(data)) : null,
    updateFn: canManageTable('stores') ? ((id, data) => api.updateStore(id, data)) : null,
    deleteFn: canManageTable('stores') ? ((id) => api.deleteStore(id)) : null,
    createFields: [
      { prop: 'store_name', label: '门店名称', required: true },
      { prop: 'store_type', label: '门店类型', type: 'select', required: true, options: [{ label: '旗舰店', value: 1 }, { label: '私教馆', value: 2 }, { label: '社区店', value: 3 }] },
      { prop: 'province_id', label: '省份ID', type: 'number', required: true },
      { prop: 'province_name', label: '省份名称' },
      { prop: 'city', label: '城市' },
      { prop: 'district', label: '区县' },
      { prop: 'address', label: '详细地址' },
      { prop: 'store_phone', label: '门店电话' },
      { prop: 'store_image_url', label: '门店图片', type: 'upload' },
      { prop: 'store_introduction', label: '门店介绍', type: 'textarea' },
      { prop: 'business_hours', label: '营业时间' },
      { prop: 'is_operating', label: '是否营业', type: 'select', default: 1, options: [{ label: '营业中', value: 1 }, { label: '停业', value: 0 }] },
      { prop: 'store_lng', label: '经度', type: 'number' },
      { prop: 'store_lat', label: '纬度', type: 'number' },
    ],
    editFields: [
      { prop: 'store_name', label: '门店名称' },
      { prop: 'store_type', label: '门店类型', type: 'select', options: [{ label: '旗舰店', value: 1 }, { label: '私教馆', value: 2 }, { label: '社区店', value: 3 }] },
      { prop: 'province_id', label: '省份ID', type: 'number' },
      { prop: 'province_name', label: '省份名称' },
      { prop: 'city', label: '城市' },
      { prop: 'district', label: '区县' },
      { prop: 'address', label: '详细地址' },
      { prop: 'store_phone', label: '门店电话' },
      { prop: 'store_image_url', label: '门店图片', type: 'upload' },
      { prop: 'store_introduction', label: '门店介绍', type: 'textarea' },
      { prop: 'business_hours', label: '营业时间' },
      { prop: 'is_operating', label: '是否营业', type: 'select', options: [{ label: '营业中', value: 1 }, { label: '停业', value: 0 }] },
      { prop: 'store_lng', label: '经度', type: 'number' },
      { prop: 'store_lat', label: '纬度', type: 'number' },
    ],
  },
  user_stores: {
    label: '用户门店关联 (y_user_store)',
    fetchFn: api.getUserStores,
    idProp: 'id',
    getByIdFn: (id) => api.getUserStoreById(id),
    idSearchLabel: '输入关联 ID 查询',
    columns: [
      { prop: 'id', label: 'ID', width: 80 },
      { prop: 'user_id', label: '用户ID' },
      { prop: 'role_id', label: '角色ID' },
      { prop: 'store_id', label: '门店ID' },
      { prop: 'created_at', label: '关联时间' },
    ],
    createFn: canManageTable('user_stores') ? ((data) => api.createUserStore(data)) : null,
    updateFn: canManageTable('user_stores') ? ((id, data) => api.updateUserStore(id, data)) : null,
    deleteFn: canManageTable('user_stores') ? ((id) => api.deleteUserStore(id)) : null,
    createFields: [
      { prop: 'user_id', label: '用户', type: 'select', required: true, options: userOptions.value },
      { prop: 'role_id', label: '角色', type: 'select', required: true, options: roleOptions.value },
      { prop: 'store_id', label: '门店ID', type: 'number', required: true },
    ],
    editFields: [
      { prop: 'user_id', label: '用户', type: 'select', options: userOptions.value },
      { prop: 'role_id', label: '角色', type: 'select', options: roleOptions.value },
      { prop: 'store_id', label: '门店ID', type: 'number' },
    ],
  },
  // ========== 课程管理 ==========
  course_categories: {
    label: '课程分类 (t_course_category)',
    fetchFn: api.getCourseCategories,
    idProp: 'category_id',
    getByIdFn: (id) => api.getCourseCategoryById(id),
    idSearchLabel: '输入分类 ID 查询',
    columns: [
      { prop: 'category_id', label: 'ID', width: 80 },
      { prop: 'category_name', label: '分类名称' },
      { prop: 'category_url', label: '图片URL', width: 200 },
      { prop: 'description', label: '描述' },
      { prop: 'status', label: '状态', width: 70 },
    ],
    createFn: canManageTable('course_categories') ? ((data) => api.createCourseCategory(data)) : null,
    updateFn: canManageTable('course_categories') ? ((id, data) => api.updateCourseCategory(id, data)) : null,
    deleteFn: canManageTable('course_categories') ? ((id) => api.deleteCourseCategory(id)) : null,
    createFields: [
      { prop: 'category_name', label: '分类名称', required: true },
      { prop: 'category_url', label: '分类图片', type: 'upload' },
      { prop: 'description', label: '描述', type: 'textarea' },
      { prop: 'status', label: '状态', type: 'select', default: 1, options: [{ label: '启用', value: 1 }, { label: '禁用', value: 0 }] },
    ],
    editFields: [
      { prop: 'category_name', label: '分类名称' },
      { prop: 'category_url', label: '分类图片', type: 'upload' },
      { prop: 'description', label: '描述', type: 'textarea' },
      { prop: 'status', label: '状态', type: 'select', options: [{ label: '启用', value: 1 }, { label: '禁用', value: 0 }] },
    ],
  },
  courses: {
    label: '课程 (t_course)',
    fetchFn: () => api.getCourses({ params: { page_size: 999 } }).then(unwrapPaginated),
    idProp: 'course_id',
    getByIdFn: (id) => api.getCourseById(id),
    idSearchLabel: '输入课程 ID 查询',
    columns: [
      { prop: 'course_id', label: 'ID', width: 80 },
      { prop: 'course_name', label: '课程名称' },
      { prop: 'category_id', label: '分类ID', width: 80 },
      { prop: 'course_difficulty', label: '难度', width: 70 },
      { prop: 'duration_minutes', label: '时长(分)', width: 80 },
      { prop: 'max_participants', label: '最大人数', width: 80 },
      { prop: 'schedule_info', label: '排课信息' },
      { prop: 'description', label: '描述' },
      { prop: 'status', label: '状态', width: 70 },
    ],
    createFn: canManageTable('courses') ? ((data) => api.createCourse(data)) : null,
    updateFn: canManageTable('courses') ? ((id, data) => api.updateCourse(id, data)) : null,
    deleteFn: canManageTable('courses') ? ((id) => api.deleteCourse(id)) : null,
    createFields: [
      { prop: 'course_name', label: '课程名称', required: true },
      { prop: 'category_id', label: '分类ID', type: 'number', required: true },
      { prop: 'course_difficulty', label: '难度(1-5)', type: 'number', min: 1, max: 5 },
      { prop: 'duration_minutes', label: '时长(分钟)', type: 'number' },
      { prop: 'max_participants', label: '最大人数', type: 'number' },
      { prop: 'schedule_info', label: '排课信息' },
      { prop: 'description', label: '描述', type: 'textarea' },
      { prop: 'status', label: '状态', type: 'select', default: 1, options: [{ label: '启用', value: 1 }, { label: '禁用', value: 0 }] },
    ],
    editFields: [
      { prop: 'course_name', label: '课程名称' },
      { prop: 'category_id', label: '分类ID', type: 'number' },
      { prop: 'course_difficulty', label: '难度(1-5)', type: 'number', min: 1, max: 5 },
      { prop: 'duration_minutes', label: '时长(分钟)', type: 'number' },
      { prop: 'max_participants', label: '最大人数', type: 'number' },
      { prop: 'schedule_info', label: '排课信息' },
      { prop: 'description', label: '描述', type: 'textarea' },
      { prop: 'status', label: '状态', type: 'select', options: [{ label: '启用', value: 1 }, { label: '禁用', value: 0 }] },
    ],
  },
  course_favorites: {
    label: '课程收藏 (y_user_course_favorite)',
    fetchFn: api.getCourseFavorites,
    idProp: 'favorite_id',
    getByIdFn: (id) => api.getCourseFavoriteById(id),
    idSearchLabel: '输入收藏 ID 查询',
    columns: [
      { prop: 'favorite_id', label: 'ID', width: 80 },
      { prop: 'user_id', label: '用户ID' },
      { prop: 'course_id', label: '课程ID' },
      { prop: 'created_at', label: '收藏时间' },
    ],
    createFn: canManageTable('course_favorites') ? ((data) => api.createCourseFavorite(data)) : null,
    updateFn: canManageTable('course_favorites') ? ((id, data) => api.updateCourseFavorite(id, data)) : null,
    deleteFn: canManageTable('course_favorites') ? ((id) => api.deleteCourseFavorite(id)) : null,
    createFields: [
      { prop: 'course_id', label: '课程ID', type: 'number', required: true },
    ],
    editFields: [
      { prop: 'course_id', label: '课程ID', type: 'number' },
    ],
  },
  // ========== 动作库 ==========
  action_categories: {
    label: '动作分类 (t_action_category)',
    fetchFn: api.getActionCategories,
    idProp: 'category_id',
    getByIdFn: (id) => api.getActionCategoryById(id),
    idSearchLabel: '输入分类 ID 查询',
    columns: [
      { prop: 'category_id', label: 'ID', width: 80 },
      { prop: 'category_name', label: '分类名称' },
      { prop: 'category_image_url', label: '图片URL', width: 200 },
    ],
    createFn: canManageTable('action_categories') ? ((data) => api.createActionCategory(data)) : null,
    updateFn: canManageTable('action_categories') ? ((id, data) => api.updateActionCategory(id, data)) : null,
    deleteFn: canManageTable('action_categories') ? ((id) => api.deleteActionCategory(id)) : null,
    createFields: [
      { prop: 'category_name', label: '分类名称', required: true },
      { prop: 'category_image_url', label: '分类图片', type: 'upload' },
    ],
    editFields: [
      { prop: 'category_name', label: '分类名称' },
      { prop: 'category_image_url', label: '分类图片', type: 'upload' },
    ],
  },
  actions: {
    label: '动作 (t_action)',
    fetchFn: () => api.getActions({ params: { page_size: 999 } }).then(unwrapPaginated),
    idProp: 'action_id',
    getByIdFn: (id) => api.getActionById(id),
    idSearchLabel: '输入动作 ID 查询',
    columns: [
      { prop: 'action_id', label: 'ID', width: 80 },
      { prop: 'action_name', label: '动作名称' },
      { prop: 'category_id', label: '分类ID', width: 80 },
      { prop: 'action_difficulty', label: '难度', width: 70 },
      { prop: 'action_image_url', label: '图片URL', width: 160 },
      { prop: 'applicable_equipment', label: '适用器械' },
      { prop: 'applicable_store_type', label: '适用门店', width: 80 },
    ],
    createFn: canManageTable('actions') ? ((data) => api.createAction(data)) : null,
    updateFn: canManageTable('actions') ? ((id, data) => api.updateAction(id, data)) : null,
    deleteFn: canManageTable('actions') ? ((id) => api.deleteAction(id)) : null,
    createFields: [
      { prop: 'action_name', label: '动作名称', required: true },
      { prop: 'category_id', label: '分类ID', type: 'number', required: true },
      { prop: 'action_difficulty', label: '难度(1-5)', type: 'number', min: 1, max: 5 },
      { prop: 'action_image_url', label: '动作图片', type: 'upload' },
      { prop: 'action_steps', label: '动作步骤', type: 'textarea' },
      { prop: 'attention_points', label: '注意事项', type: 'textarea' },
      { prop: 'applicable_equipment', label: '适用器械' },
      { prop: 'applicable_store_type', label: '适用门店类型', type: 'select', options: [{ label: '旗舰店', value: 1 }, { label: '私教馆', value: 2 }, { label: '社区店', value: 3 }] },
    ],
    editFields: [
      { prop: 'action_name', label: '动作名称' },
      { prop: 'category_id', label: '分类ID', type: 'number' },
      { prop: 'action_difficulty', label: '难度(1-5)', type: 'number', min: 1, max: 5 },
      { prop: 'action_image_url', label: '动作图片', type: 'upload' },
      { prop: 'action_steps', label: '动作步骤', type: 'textarea' },
      { prop: 'attention_points', label: '注意事项', type: 'textarea' },
      { prop: 'applicable_equipment', label: '适用器械' },
      { prop: 'applicable_store_type', label: '适用门店类型', type: 'select', options: [{ label: '旗舰店', value: 1 }, { label: '私教馆', value: 2 }, { label: '社区店', value: 3 }] },
    ],
  },
  action_favorites: {
    label: '动作收藏 (y_user_action_favorite)',
    fetchFn: api.getActionFavorites,
    idProp: 'favorite_id',
    getByIdFn: (id) => api.getActionFavoriteById(id),
    idSearchLabel: '输入收藏 ID 查询',
    columns: [
      { prop: 'favorite_id', label: 'ID', width: 80 },
      { prop: 'user_id', label: '用户ID' },
      { prop: 'action_id', label: '动作ID' },
      { prop: 'created_at', label: '收藏时间' },
    ],
    createFn: canManageTable('action_favorites') ? ((data) => api.createActionFavorite(data)) : null,
    updateFn: canManageTable('action_favorites') ? ((id, data) => api.updateActionFavorite(id, data)) : null,
    deleteFn: canManageTable('action_favorites') ? ((id) => api.deleteActionFavorite(id)) : null,
    createFields: [
      { prop: 'action_id', label: '动作ID', type: 'number', required: true },
    ],
    editFields: [
      { prop: 'action_id', label: '动作ID', type: 'number' },
    ],
  },
  // ========== 内容管理 ==========
  slogans: {
    label: '标语 (t_slogan_info)',
    fetchFn: api.getSlogans,
    idProp: 'slogan_id',
    getByIdFn: (id) => api.getSloganById(id),
    idSearchLabel: '输入标语 ID 查询',
    columns: [
      { prop: 'slogan_id', label: 'ID', width: 80 },
      { prop: 'slogan_name', label: '标语名称' },
      { prop: 'slogan_content', label: '标语内容' },
      { prop: 'slogan_image_url', label: '图片URL', width: 200 },
      { prop: 'status', label: '状态', width: 70 },
    ],
    createFn: canManageTable('slogans') ? ((data) => api.createSlogan(data)) : null,
    updateFn: canManageTable('slogans') ? ((id, data) => api.updateSlogan(id, data)) : null,
    deleteFn: canManageTable('slogans') ? ((id) => api.deleteSlogan(id)) : null,
    createFields: [
      { prop: 'slogan_name', label: '标语名称', required: true },
      { prop: 'slogan_content', label: '标语内容', required: true, type: 'textarea' },
      { prop: 'slogan_image_url', label: '标语图片', type: 'upload' },
      { prop: 'status', label: '状态', type: 'select', default: 1, options: [{ label: '启用', value: 1 }, { label: '禁用', value: 0 }] },
    ],
    editFields: [
      { prop: 'slogan_name', label: '标语名称' },
      { prop: 'slogan_content', label: '标语内容', type: 'textarea' },
      { prop: 'slogan_image_url', label: '标语图片', type: 'upload' },
      { prop: 'status', label: '状态', type: 'select', options: [{ label: '启用', value: 1 }, { label: '禁用', value: 0 }] },
    ],
  },
  activities: {
    label: '赛事活动 (t_activity_event)',
    fetchFn: api.getActivities,
    idProp: 'event_id',
    getByIdFn: (id) => api.getActivityById(id),
    idSearchLabel: '输入活动 ID 查询',
    columns: [
      { prop: 'event_id', label: 'ID', width: 80 },
      { prop: 'title', label: '标题' },
      { prop: 'event_date', label: '日期' },
      { prop: 'location', label: '地点' },
      { prop: 'status', label: '状态' },
      { prop: 'description', label: '描述' },
      { prop: 'tags', label: '标签' },
      { prop: 'prize', label: '奖金/奖品' },
      { prop: 'scale', label: '规模' },
      { prop: 'created_at', label: '创建时间' },
    ],
    createFn: canManageTable('activities') ? ((data) => api.createActivity(data)) : null,
    updateFn: canManageTable('activities') ? ((id, data) => api.updateActivity(id, data)) : null,
    deleteFn: canManageTable('activities') ? ((id) => api.deleteActivity(id)) : null,
    createFields: [
      { prop: 'title', label: '标题', required: true },
      { prop: 'event_date', label: '活动日期', type: 'date', required: true },
      { prop: 'location', label: '地点', required: true },
      { prop: 'status', label: '状态', type: 'select', required: true, options: [{ label: '预告', value: '预告' }, { label: '报名中', value: '报名中' }, { label: '早鸟票', value: '早鸟票' }, { label: '进行中', value: '进行中' }, { label: '已结束', value: '已结束' }] },
      { prop: 'description', label: '描述', type: 'textarea', required: true },
      { prop: 'tags', label: '标签(逗号分隔)' },
      { prop: 'prize', label: '奖金/奖品' },
      { prop: 'scale', label: '规模' },
    ],
    editFields: [
      { prop: 'title', label: '标题' },
      { prop: 'event_date', label: '活动日期', type: 'date' },
      { prop: 'location', label: '地点' },
      { prop: 'status', label: '状态', type: 'select', options: [{ label: '预告', value: '预告' }, { label: '报名中', value: '报名中' }, { label: '早鸟票', value: '早鸟票' }, { label: '进行中', value: '进行中' }, { label: '已结束', value: '已结束' }] },
      { prop: 'description', label: '描述', type: 'textarea' },
      { prop: 'tags', label: '标签(逗号分隔)' },
      { prop: 'prize', label: '奖金/奖品' },
      { prop: 'scale', label: '规模' },
    ],
  },
}))

const activeKey = ref('')
const activeConfig = computed(() => tableConfig.value[activeKey.value] || null)

function onSelect(key) {
  activeKey.value = key
}
</script>

<style scoped>
.dashboard-shell {
  min-height: calc(100dvh - 64px);
  background: transparent;
}

.dashboard-aside {
  padding: 18px 14px;
  border-right: 1px solid var(--fm-border);
  background: rgba(255, 255, 255, 0.78);
  backdrop-filter: blur(14px);
}

.aside-title {
  padding: 8px 10px 16px;
  border-bottom: 1px solid var(--fm-border);
  margin-bottom: 12px;
}

.aside-title span,
.aside-title small {
  display: block;
}

.aside-title span {
  color: var(--fm-ink);
  font-size: 15px;
  font-weight: 850;
}

.aside-title small {
  margin-top: 4px;
  color: var(--fm-muted);
  font-size: 12px;
}

.dashboard-menu {
  border: none;
  background: transparent;
}

.dashboard-menu :deep(.el-sub-menu__title),
.dashboard-menu :deep(.el-menu-item) {
  height: 42px;
  border-radius: 10px;
  margin: 4px 0;
}

.dashboard-menu :deep(.el-menu-item.is-active) {
  color: var(--fm-accent-strong);
  background: var(--fm-accent-soft);
  font-weight: 800;
}

.menu-group-title {
  font-weight: 800;
}

.dashboard-main {
  min-width: 0;
  padding: 24px;
}

.dashboard-heading {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}

.heading-kicker {
  display: block;
  color: var(--fm-muted);
  font-size: 12px;
  font-weight: 800;
}

.dashboard-heading h3 {
  margin: 5px 0 0;
  color: var(--fm-ink);
  font-size: 24px;
  line-height: 1.15;
}

.heading-pill {
  max-width: 220px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  padding: 8px 12px;
  border-radius: 999px;
  color: var(--fm-accent-strong);
  background: var(--fm-accent-soft);
  font-size: 12px;
  font-weight: 800;
}

.dashboard-empty {
  min-height: calc(100dvh - 160px);
  border: 1px dashed #bfd1c4;
  border-radius: 22px;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.92), rgba(239, 247, 241, 0.92));
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 32px;
}

.empty-mark {
  width: 58px;
  height: 58px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 18px;
  color: #fff;
  background: linear-gradient(135deg, #14211c, #1f7a4d);
  font-weight: 900;
}

.dashboard-empty h3 {
  margin: 0;
  color: var(--fm-ink);
  font-size: 22px;
}

.dashboard-empty p {
  max-width: 420px;
  margin: 10px 0 0;
  color: var(--fm-muted);
  line-height: 1.7;
}

@media (max-width: 900px) {
  .dashboard-shell {
    display: block;
  }

  .dashboard-aside {
    width: 100% !important;
    border-right: none;
    border-bottom: 1px solid var(--fm-border);
  }

  .dashboard-main {
    padding: 18px 14px;
  }

  .dashboard-heading {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
