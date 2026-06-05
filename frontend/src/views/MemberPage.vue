<template>
  <Dashboard :menu-groups="menuGroups" />
</template>

<script setup>
import Dashboard from '../components/Dashboard.vue'

const menuGroups = [
  {
    key: 'system', label: '个人信息',
    children: [
      { key: 'users', label: '我的信息' },
      { key: 'user_profiles', label: '我的档案' },
    ],
  },
  {
    key: 'course', label: '课程',
    children: [
      { key: 'courses', label: '课程列表' },
    ],
  },
  {
    key: 'action', label: '动作库',
    children: [
      { key: 'actions', label: '动作列表' },
    ],
  },
]
</script>
