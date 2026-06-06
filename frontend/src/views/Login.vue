<template>
  <div class="login-wrapper">
    <section class="login-hero">
      <div class="login-copy">
        <div class="brand-row">
          <span class="brand-mark">FM</span>
          <span>Fitness Management</span>
        </div>
        <h1>把门店、课程和训练内容放进同一个工作台</h1>
        <p>为运营、教练和会员提供分角色入口，快速查看课程、动作库、活动和个人档案。</p>
        <div class="login-metrics">
          <div>
            <strong>5</strong>
            <span>业务模块</span>
          </div>
          <div>
            <strong>4</strong>
            <span>角色入口</span>
          </div>
          <div>
            <strong>1</strong>
            <span>统一数据后台</span>
          </div>
        </div>
      </div>

      <div class="training-panel" aria-hidden="true">
        <div class="panel-top">
          <span>今日训练</span>
          <b>82%</b>
        </div>
        <div class="progress-track"><span></span></div>
        <div class="training-list">
          <i></i>
          <i></i>
          <i></i>
        </div>
      </div>
    </section>

    <el-card class="login-card" shadow="never">
      <div class="login-heading">
        <h2 class="login-title">登录系统</h2>
        <p class="login-subtitle">使用你的账号进入对应角色页面</p>
      </div>
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="0"
        @submit.prevent="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="用户名"
            prefix-icon="User"
            size="large"
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            prefix-icon="Lock"
            size="large"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            class="login-button"
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>
      <div class="login-hint">
        <span>测试账号</span>
        <div>admin / admin123</div>
        <div>operator / oper123</div>
        <div>coach_w / coach123</div>
        <div>member_w / member123</div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { login, setToken, getRouteByRole } from '../api'

const router = useRouter()
const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handleLogin() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const { data } = await login(form.username, form.password)
    setToken(data.access_token)
    ElMessage.success(`欢迎, ${data.username}`)
    router.push({ name: getRouteByRole(data.role_id) })
  } catch (e) {
    const msg = e.response?.data?.detail || '登录失败'
    ElMessage.error(msg)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-wrapper {
  min-height: 100dvh;
  padding: 48px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 420px;
  gap: 28px;
  align-items: center;
  background:
    radial-gradient(circle at 14% 16%, rgba(31, 122, 77, 0.18), transparent 28%),
    linear-gradient(135deg, #edf5eb 0%, #f8faf7 52%, #e6efe7 100%);
}

.login-hero {
  min-height: 560px;
  position: relative;
  overflow: hidden;
  border-radius: 28px;
  padding: 48px;
  color: #fff;
  background:
    linear-gradient(135deg, rgba(20, 33, 28, 0.9), rgba(31, 122, 77, 0.88)),
    url("https://images.unsplash.com/photo-1517836357463-d25dfeac3438?auto=format&fit=crop&w=1400&q=80") center / cover;
  box-shadow: var(--fm-shadow-soft);
}

.login-hero::after {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, rgba(20, 33, 28, 0.78), rgba(20, 33, 28, 0.25));
}

.login-copy,
.training-panel {
  position: relative;
  z-index: 1;
}

.brand-row {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  font-weight: 800;
  letter-spacing: 0;
}

.brand-mark {
  width: 38px;
  height: 38px;
  border-radius: 12px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.16);
  border: 1px solid rgba(255, 255, 255, 0.22);
}

.login-copy h1 {
  max-width: 680px;
  margin: 70px 0 18px;
  font-size: clamp(34px, 5vw, 58px);
  line-height: 1.06;
  font-weight: 850;
  letter-spacing: 0;
}

.login-copy p {
  max-width: 520px;
  margin: 0;
  color: rgba(255, 255, 255, 0.82);
  font-size: 16px;
  line-height: 1.8;
}

.login-metrics {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 120px));
  gap: 12px;
  margin-top: 42px;
}

.login-metrics div {
  padding: 16px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.16);
  backdrop-filter: blur(12px);
}

.login-metrics strong {
  display: block;
  font-size: 26px;
  line-height: 1;
}

.login-metrics span {
  display: block;
  margin-top: 8px;
  color: rgba(255, 255, 255, 0.72);
  font-size: 12px;
}

.training-panel {
  width: 280px;
  margin-top: 72px;
  padding: 20px;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.14);
  border: 1px solid rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(16px);
}

.panel-top {
  display: flex;
  justify-content: space-between;
  color: rgba(255, 255, 255, 0.9);
  font-size: 13px;
}

.progress-track {
  height: 9px;
  margin: 18px 0;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.18);
  overflow: hidden;
}

.progress-track span {
  display: block;
  width: 82%;
  height: 100%;
  border-radius: inherit;
  background: #a9f0c4;
}

.training-list {
  display: grid;
  gap: 10px;
}

.training-list i {
  display: block;
  height: 12px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.22);
}

.training-list i:nth-child(2) { width: 82%; }
.training-list i:nth-child(3) { width: 62%; }

.login-card {
  width: 100%;
  border: 1px solid rgba(220, 230, 222, 0.92);
  border-radius: 24px;
  padding: 10px;
  box-shadow: var(--fm-shadow-soft);
}

.login-heading {
  margin-bottom: 24px;
}

.login-title {
  margin: 0;
  font-size: 26px;
  font-weight: 850;
  color: var(--fm-ink);
}

.login-subtitle {
  margin: 8px 0 0;
  font-size: 14px;
  color: var(--fm-muted);
}

.login-button {
  width: 100%;
  min-height: 44px;
  margin-top: 2px;
}

.login-hint {
  margin-top: 18px;
  padding: 16px;
  border-radius: 16px;
  background: var(--fm-surface-soft);
  font-size: 12px;
  color: var(--fm-muted);
  line-height: 1.9;
}

.login-hint span {
  display: block;
  margin-bottom: 4px;
  color: var(--fm-ink);
  font-weight: 800;
}

@media (max-width: 980px) {
  .login-wrapper {
    grid-template-columns: 1fr;
    padding: 24px;
  }

  .login-hero {
    min-height: auto;
    padding: 34px;
  }

  .login-copy h1 {
    margin-top: 48px;
  }

  .training-panel {
    display: none;
  }
}

@media (max-width: 640px) {
  .login-wrapper {
    padding: 14px;
  }

  .login-hero {
    border-radius: 20px;
    padding: 24px;
  }

  .login-metrics {
    grid-template-columns: 1fr;
  }
}
</style>
