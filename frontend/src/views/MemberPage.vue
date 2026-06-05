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
      { key: 'course_categories', label: '课程分类' },
      { key: 'courses', label: '课程列表' },
      { key: 'course_favorites', label: '我的收藏' },
    ],
  },
  {
    key: 'action', label: '动作库',
    children: [
      { key: 'action_categories', label: '动作分类' },
      { key: 'actions', label: '动作列表' },
      { key: 'action_favorites', label: '我的收藏' },
    ],
  },
  {
    key: 'content', label: '内容',
    children: [
      { key: 'slogans', label: '标语' },
      { key: 'activities', label: '赛事活动' },
    ],
  },
]
</script>
