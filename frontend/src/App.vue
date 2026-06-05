<template>
  <el-container style="min-height: 100vh">
    <el-header v-if="showHeader" class="app-header">
      <span class="logo">Fitness Management</span>
      <div v-if="userInfo" class="header-right">
        <el-dropdown @command="handleCommand">
          <span class="user-info">
            {{ userInfo.username }}
            <el-tag size="small" type="info" style="margin-left: 6px">
              {{ roleLabel }}
            </el-tag>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>
    <router-view />
  </el-container>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getToken, clearToken, getMe } from './api'

const route = useRoute()
const router = useRouter()
const userInfo = ref(null)

const showHeader = computed(() => route.name !== 'Login')

const roleMap = {
  1: '超级管理员',
  2: '运营管理员',
  3: '教练',
  4: '会员',
}
const roleLabel = computed(() => roleMap[userInfo.value?.role_id] || '未知')

async function fetchMe() {
  if (!getToken()) return
  try {
    const { data } = await getMe()
    userInfo.value = data
  } catch {
    userInfo.value = null
  }
}

watch(() => route.name, (name) => {
  if (name !== 'Login' && getToken()) fetchMe()
}, { immediate: true })

function handleCommand(cmd) {
  if (cmd === 'logout') {
    clearToken()
    userInfo.value = null
    router.push('/login')
  }
}
</script>

<style>
body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0 24px;
  height: 60px;
}
.logo { font-size: 18px; font-weight: 700; color: #409eff; }
.header-right { display: flex; align-items: center; }
.user-info { cursor: pointer; font-size: 14px; color: #606266; }
</style>
