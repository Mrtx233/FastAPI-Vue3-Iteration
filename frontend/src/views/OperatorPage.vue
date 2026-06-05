<template>
  <Dashboard :menu-groups="menuGroups" :can-delete-user="false" :load-dropdowns="true" />
</template>

<script setup>
import Dashboard from '../components/Dashboard.vue'

const menuGroups = [
  {
    key: 'system', label: '系统管理',
    children: [
      { key: 'permissions', label: '权限定义' },
      { key: 'roles', label: '角色' },
      { key: 'role_permissions', label: '角色权限' },
      { key: 'users', label: '用户' },
      { key: 'user_profiles', label: '用户档案' },
    ],
  },
  {
    key: 'store', label: '门店管理',
    children: [
      { key: 'provinces', label: '省份区域' },
      { key: 'stores', label: '门店信息' },
      { key: 'user_stores', label: '用户门店' },
    ],
  },
  {
    key: 'course', label: '课程管理',
    children: [
      { key: 'course_categories', label: '课程分类' },
      { key: 'courses', label: '课程' },
      { key: 'course_favorites', label: '课程收藏' },
    ],
  },
  {
    key: 'action', label: '动作库',
    children: [
      { key: 'action_categories', label: '动作分类' },
      { key: 'actions', label: '动作' },
      { key: 'action_favorites', label: '动作收藏' },
    ],
  },
  {
    key: 'content', label: '内容管理',
    children: [
      { key: 'slogans', label: '标语' },
      { key: 'activities', label: '赛事活动' },
    ],
  },
]
</script>
