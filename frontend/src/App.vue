<template>
  <el-container style="min-height: 100vh">
    <el-header class="app-header">
      <span class="logo">Fitness Management</span>
    </el-header>
    <router-view />
  </el-container>
</template>

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
.logo { font-size: 18px; font-weight: 700; color: #409eff; }
</style>
