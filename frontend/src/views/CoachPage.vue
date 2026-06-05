<template>
  <Dashboard :menu-groups="menuGroups" />
</template>

<script setup>
import Dashboard from '../components/Dashboard.vue'

const menuGroups = [
  {
    key: 'system', label: '用户管理',
    children: [
      { key: 'users', label: '用户列表' },
      { key: 'user_profiles', label: '用户档案' },
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
