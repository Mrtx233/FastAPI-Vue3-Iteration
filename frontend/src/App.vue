<template>
  <el-container style="min-height: 100vh">
    <el-header class="app-header">
      <span class="logo">FastAPI + Vue3 Demo</span>
      <el-menu mode="horizontal" :default-active="route.path" router :ellipsis="false" class="header-menu">
        <el-menu-item index="/users">用户管理</el-menu-item>
        <el-menu-item index="/login">登录</el-menu-item>
      </el-menu>
    </el-header>
    <el-main>
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup>
import { useRoute } from 'vue-router'
const route = useRoute()
</script>

<style>
body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
.app-header {
  display: flex;
  align-items: center;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0 24px;
  height: 60px;
}
.logo { font-size: 18px; font-weight: 700; margin-right: 40px; color: #409eff; white-space: nowrap; }
.header-menu { border-bottom: none; }
</style>
