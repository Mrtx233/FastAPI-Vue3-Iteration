<template>
  <el-container style="height: calc(100vh - 60px)">
    <!-- 侧边栏 -->
    <el-aside width="220px" style="border-right: 1px solid #e4e7ed; background: #fafafa">
      <el-menu :default-active="activeKey" @select="onSelect" style="border: none">
        <el-sub-menu v-for="group in menuGroups" :key="group.key" :index="group.key">
          <template #title>
            <span style="font-weight: 600">{{ group.label }}</span>
          </template>
          <el-menu-item v-for="item in group.children" :key="item.key" :index="item.key">
            {{ item.label }}
          </el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>

    <!-- 内容区 -->
    <el-main style="padding: 20px">
      <template v-if="activeKey">
        <h3 style="margin: 0 0 16px; color: #303133">{{ activeConfig.label }}</h3>
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
      <el-empty v-else description="请从左侧选择一个数据表" />
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
      api.getUsers(),
    ])
    if (rolesRes.status === 'fulfilled') {
      roleOptions.value = rolesRes.value.data.map(r => ({ label: `${r.role_name} (${r.role_code})`, value: r.id }))
    }
    if (permsRes.status === 'fulfilled') {
      permOptions.value = permsRes.value.data.map(p => ({ label: `${p.permission_name} (${p.permission_code})`, value: p.id }))
    }
    if (usersRes.status === 'fulfilled') {
      userOptions.value = usersRes.value.data.map(u => ({ label: `${u.username}${u.real_name ? ' - ' + u.real_name : ''}`, value: u.user_id }))
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
    return api.getUsers()
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
    columns: [
      { prop: 'province_id', label: 'ID', width: 80 },
      { prop: 'province_name', label: '省份名称' },
      { prop: 'center_lng', label: '中心经度' },
      { prop: 'center_lat', label: '中心纬度' },
    ],
  },
  stores: {
    label: '门店信息 (t_store)',
    fetchFn: api.getStores,
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
  },
  user_stores: {
    label: '用户门店关联 (y_user_store)',
    fetchFn: api.getUserStores,
    columns: [
      { prop: 'id', label: 'ID', width: 80 },
      { prop: 'user_id', label: '用户ID' },
      { prop: 'role_id', label: '角色ID' },
      { prop: 'store_id', label: '门店ID' },
      { prop: 'created_at', label: '关联时间' },
    ],
  },
  // ========== 课程管理 ==========
  course_categories: {
    label: '课程分类 (t_course_category)',
    fetchFn: api.getCourseCategories,
    columns: [
      { prop: 'category_id', label: 'ID', width: 80 },
      { prop: 'category_name', label: '分类名称' },
      { prop: 'category_url', label: '图片URL', width: 200 },
      { prop: 'description', label: '描述' },
      { prop: 'status', label: '状态', width: 70 },
    ],
  },
  courses: {
    label: '课程 (t_course)',
    fetchFn: api.getCourses,
    columns: [
      { prop: 'course_id', label: 'ID', width: 80 },
      { prop: 'course_name', label: '课程名称' },
      { prop: 'category_id', label: '分类ID', width: 80 },
      { prop: 'course_difficulty', label: '难度', width: 70 },
      { prop: 'duration_minutes', label: '时长(分)', width: 80 },
      { prop: 'max_participants', label: '最大人数', width: 80 },
      { prop: 'description', label: '描述' },
      { prop: 'status', label: '状态', width: 70 },
    ],
  },
  course_favorites: {
    label: '课程收藏 (y_user_course_favorite)',
    fetchFn: api.getCourseFavorites,
    columns: [
      { prop: 'favorite_id', label: 'ID', width: 80 },
      { prop: 'user_id', label: '用户ID' },
      { prop: 'course_id', label: '课程ID' },
      { prop: 'created_at', label: '收藏时间' },
    ],
  },
  // ========== 动作库 ==========
  action_categories: {
    label: '动作分类 (t_action_category)',
    fetchFn: api.getActionCategories,
    columns: [
      { prop: 'category_id', label: 'ID', width: 80 },
      { prop: 'category_name', label: '分类名称' },
      { prop: 'category_image_url', label: '图片URL', width: 200 },
    ],
  },
  actions: {
    label: '动作 (t_action)',
    fetchFn: api.getActions,
    columns: [
      { prop: 'action_id', label: 'ID', width: 80 },
      { prop: 'action_name', label: '动作名称' },
      { prop: 'category_id', label: '分类ID', width: 80 },
      { prop: 'action_difficulty', label: '难度', width: 70 },
      { prop: 'applicable_equipment', label: '适用器械' },
      { prop: 'applicable_store_type', label: '适用门店', width: 80 },
    ],
  },
  action_favorites: {
    label: '动作收藏 (y_user_action_favorite)',
    fetchFn: api.getActionFavorites,
    columns: [
      { prop: 'favorite_id', label: 'ID', width: 80 },
      { prop: 'user_id', label: '用户ID' },
      { prop: 'action_id', label: '动作ID' },
      { prop: 'created_at', label: '收藏时间' },
    ],
  },
  // ========== 内容管理 ==========
  slogans: {
    label: '标语 (t_slogan_info)',
    fetchFn: api.getSlogans,
    columns: [
      { prop: 'slogan_id', label: 'ID', width: 80 },
      { prop: 'slogan_name', label: '标语名称' },
      { prop: 'slogan_content', label: '标语内容' },
      { prop: 'slogan_image_url', label: '图片URL', width: 200 },
      { prop: 'status', label: '状态', width: 70 },
    ],
  },
  activities: {
    label: '赛事活动 (t_activity_event)',
    fetchFn: api.getActivities,
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
  },
}))

const activeKey = ref('')
const activeConfig = computed(() => tableConfig.value[activeKey.value] || null)

function onSelect(key) {
  activeKey.value = key
}
</script>
