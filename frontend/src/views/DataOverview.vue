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
          :key="activeKey"
        />
      </template>
      <el-empty v-else description="请从左侧选择一个数据表" />
    </el-main>
  </el-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import DataExplorer from '../components/DataExplorer.vue'
import * as api from '../api'

// 菜单分组定义
const menuGroups = [
  {
    key: 'system',
    label: '系统管理',
    children: [
      { key: 'permissions', label: '权限定义' },
      { key: 'roles', label: '角色' },
      { key: 'role_permissions', label: '角色权限' },
      { key: 'users', label: '用户' },
      { key: 'user_profiles', label: '用户档案' },
    ],
  },
  {
    key: 'store',
    label: '门店管理',
    children: [
      { key: 'provinces', label: '省份区域' },
      { key: 'stores', label: '门店信息' },
      { key: 'user_stores', label: '用户门店' },
    ],
  },
  {
    key: 'course',
    label: '课程管理',
    children: [
      { key: 'course_categories', label: '课程分类' },
      { key: 'courses', label: '课程' },
      { key: 'course_favorites', label: '课程收藏' },
    ],
  },
  {
    key: 'action',
    label: '动作库',
    children: [
      { key: 'action_categories', label: '动作分类' },
      { key: 'actions', label: '动作' },
      { key: 'action_favorites', label: '动作收藏' },
    ],
  },
  {
    key: 'content',
    label: '内容管理',
    children: [
      { key: 'slogans', label: '标语' },
      { key: 'activities', label: '赛事活动' },
    ],
  },
]

// 每个 key 对应的 API 和列定义
const tableConfig = {
  // 系统管理
  permissions: {
    label: '权限定义 (sys_permission)',
    fetchFn: api.getPermissions,
    columns: [
      { prop: 'id', label: 'ID', width: 80 },
      { prop: 'permission_code', label: '权限标识符' },
      { prop: 'permission_name', label: '权限名称' },
      { prop: 'menu_path', label: '前端路由路径' },
    ],
  },
  roles: {
    label: '角色 (sys_role)',
    fetchFn: api.getRoles,
    columns: [
      { prop: 'id', label: 'ID', width: 80 },
      { prop: 'role_code', label: '角色代码' },
      { prop: 'role_name', label: '角色名称' },
    ],
  },
  role_permissions: {
    label: '角色权限 (sys_role_permission)',
    fetchFn: api.getRolePermissions,
    columns: [
      { prop: 'id', label: 'ID', width: 80 },
      { prop: 'role_id', label: '角色ID' },
      { prop: 'permission_id', label: '权限ID' },
    ],
  },
  users: {
    label: '用户 (sys_user)',
    fetchFn: api.getUsers,
    columns: [
      { prop: 'user_id', label: 'ID', width: 80 },
      { prop: 'role_id', label: '角色ID', width: 80 },
      { prop: 'username', label: '用户名' },
      { prop: 'password', label: '密码(加密)', width: 200 },
      { prop: 'real_name', label: '真实姓名' },
      { prop: 'phone', label: '手机号' },
      { prop: 'status', label: '状态', width: 80 },
    ],
  },
  user_profiles: {
    label: '用户档案 (sys_user_profile)',
    fetchFn: api.getUserProfiles,
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
  },
  // 门店管理
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
  // 课程管理
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
  // 动作库
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
  // 内容管理
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
}

const activeKey = ref('')
const activeConfig = computed(() => tableConfig[activeKey.value] || null)

function onSelect(key) {
  activeKey.value = key
}
</script>
