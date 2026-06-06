<template>
  <el-container class="app-shell">
    <el-header v-if="showHeader" class="app-header">
      <div class="brand-lockup">
        <span class="brand-mark">FM</span>
        <div>
          <span class="logo">Fitness Management</span>
          <span class="logo-sub">训练与运营中枢</span>
        </div>
      </div>
      <div v-if="userInfo" class="header-right">
        <el-dropdown @command="handleCommand">
          <span class="user-info">
            <span class="user-name">{{ userInfo.username }}</span>
            <el-tag size="small" class="role-tag">{{ roleLabel }}</el-tag>
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
    router.push({ name: 'Login' })
  }
}
</script>

<style>
.app-shell {
  min-height: 100dvh;
  background: transparent;
}

.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
  padding: 0 28px;
  background: rgba(255, 255, 255, 0.88);
  border-bottom: 1px solid rgba(220, 230, 222, 0.9);
  backdrop-filter: blur(18px);
  position: sticky;
  top: 0;
  z-index: 20;
}

.brand-lockup {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.brand-mark {
  width: 38px;
  height: 38px;
  border-radius: 12px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 auto;
  color: #fff;
  background: linear-gradient(135deg, #14211c 0%, #1f7a4d 100%);
  font-size: 13px;
  font-weight: 800;
  box-shadow: 0 12px 28px rgba(31, 122, 77, 0.2);
}

.logo {
  display: block;
  font-size: 17px;
  font-weight: 800;
  color: var(--fm-ink);
  line-height: 1.1;
}

.logo-sub {
  display: block;
  margin-top: 2px;
  font-size: 12px;
  color: var(--fm-muted);
  line-height: 1.1;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-height: 38px;
  padding: 4px 6px 4px 12px;
  border: 1px solid var(--fm-border);
  border-radius: 999px;
  color: var(--fm-ink);
  background: #fff;
  cursor: pointer;
  box-shadow: 0 8px 20px rgba(20, 33, 28, 0.06);
}

.user-name {
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 14px;
  font-weight: 700;
}

.role-tag {
  margin-left: 0;
  color: var(--fm-accent-strong);
  background: var(--fm-accent-soft);
  border-color: transparent;
}

@media (max-width: 640px) {
  .app-header {
    padding: 0 14px;
  }

  .logo-sub {
    display: none;
  }

  .user-name {
    max-width: 96px;
  }
}
</style>
