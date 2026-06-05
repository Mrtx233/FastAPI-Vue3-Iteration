<template>
  <div class="coach-portal">
    <!-- 顶部页签导航 -->
    <div class="portal-nav">
      <div class="nav-inner">
        <span class="nav-brand">IronForge Fitness</span>
        <div class="nav-tabs">
          <div
            v-for="tab in tabs"
            :key="tab.key"
            class="nav-tab"
            :class="{ active: activeTab === tab.key }"
            @click="activeTab = tab.key"
          >
            {{ tab.label }}
          </div>
        </div>
      </div>
    </div>

    <div class="portal-content">
      <!-- ==================== 首页 ==================== -->
      <template v-if="activeTab === 'home'">
        <!-- 标语轮播 -->
        <el-carousel height="280px" :interval="5000" arrow="hover" class="slogan-carousel">
          <el-carousel-item v-for="slogan in slogans" :key="slogan.slogan_id">
            <div class="carousel-slide" :style="{ background: sloganGradients[slogan.slogan_id % sloganGradients.length] }">
              <h2 class="carousel-title">{{ slogan.slogan_name }}</h2>
              <p class="carousel-text">{{ slogan.slogan_content }}</p>
            </div>
          </el-carousel-item>
          <el-carousel-item v-if="slogans.length === 0">
            <div class="carousel-slide" :style="{ background: sloganGradients[0] }">
              <h2 class="carousel-title">IronForge Fitness</h2>
              <p class="carousel-text">科学训练，健康生活</p>
            </div>
          </el-carousel-item>
        </el-carousel>

        <!-- 赛事活动 -->
        <section class="portal-section">
          <h3 class="section-title">赛事活动</h3>
          <div class="card-grid" v-if="activities.length">
            <div class="activity-card" v-for="act in activities" :key="act.event_id">
              <div class="card-accent" :style="{ background: statusGradient(act.status) }"></div>
              <div class="card-body">
                <div class="card-top-row">
                  <h4 class="card-title">{{ act.title }}</h4>
                  <el-tag :type="activityStatusType(act.status)" size="small" effect="dark">{{ act.status }}</el-tag>
                </div>
                <p class="card-meta">{{ act.event_date }} &nbsp;|&nbsp; {{ act.location }}</p>
                <p class="card-desc">{{ act.description }}</p>
                <div class="card-footer">
                  <span v-if="act.prize" class="footer-tag">{{ act.prize }}</span>
                  <span v-if="act.scale" class="footer-tag">{{ act.scale }}</span>
                  <span v-if="act.tags" class="footer-tags">{{ act.tags }}</span>
                </div>
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无活动" :image-size="80" />
        </section>
      </template>

      <!-- ==================== 课程 ==================== -->
      <template v-if="activeTab === 'courses'">
        <section class="portal-section">
          <div class="filter-bar">
            <el-radio-group v-model="courseFilter" size="large">
              <el-radio-button :value="0">全部</el-radio-button>
              <el-radio-button
                v-for="cat in courseCategories"
                :key="cat.category_id"
                :value="cat.category_id"
              >{{ cat.category_name }}</el-radio-button>
            </el-radio-group>
          </div>
          <div class="card-grid cols-4">
            <div class="course-card" v-for="course in filteredCourses" :key="course.course_id">
              <div class="card-header-bar" :style="{ background: difficultyGradient(course.course_difficulty) }">
                <span class="card-header-title">{{ course.course_name }}</span>
                <span class="card-header-badge">{{ difficultyText(course.course_difficulty) }}</span>
              </div>
              <div class="card-body">
                <p class="card-meta">
                  {{ courseCategoryName(course.category_id) }}
                  <span class="meta-dot">&middot;</span>
                  {{ course.duration_minutes }} 分钟
                  <span class="meta-dot">&middot;</span>
                  最多 {{ course.max_participants }} 人
                </p>
                <p class="card-desc">{{ course.description || '暂无描述' }}</p>
                <div class="card-footer">
                  <el-tag :type="course.status === 1 ? 'success' : 'info'" size="small">
                    {{ course.status === 1 ? '进行中' : '已停' }}
                  </el-tag>
                  <span v-if="course.schedule_info" class="schedule-text">{{ course.schedule_info }}</span>
                </div>
              </div>
            </div>
          </div>
          <el-empty v-if="filteredCourses.length === 0" description="暂无课程" :image-size="80" />
        </section>
      </template>

      <!-- ==================== 动作库 ==================== -->
      <template v-if="activeTab === 'actions'">
        <section class="portal-section">
          <div class="filter-bar">
            <el-radio-group v-model="actionFilter" size="large">
              <el-radio-button :value="0">全部</el-radio-button>
              <el-radio-button
                v-for="cat in actionCategories"
                :key="cat.category_id"
                :value="cat.category_id"
              >{{ cat.category_name }}</el-radio-button>
            </el-radio-group>
          </div>
          <div class="card-grid cols-4">
            <div class="action-card" v-for="act in filteredActions" :key="act.action_id">
              <div class="card-header-bar" :style="{ background: difficultyGradient(act.action_difficulty) }">
                <span class="card-header-title">{{ act.action_name }}</span>
                <span class="card-header-badge">{{ difficultyText(act.action_difficulty) }}</span>
              </div>
              <div class="card-body">
                <p class="card-meta">
                  {{ actionCategoryName(act.category_id) }}
                  <span v-if="act.applicable_equipment" class="meta-dot">&middot;</span>
                  {{ act.applicable_equipment || '' }}
                </p>
                <p class="card-desc">{{ act.action_steps || '暂无说明' }}</p>
                <p v-if="act.attention_points" class="card-tip">{{ act.attention_points }}</p>
              </div>
            </div>
          </div>
          <el-empty v-if="filteredActions.length === 0" description="暂无动作" :image-size="80" />
        </section>
      </template>

      <!-- ==================== 个人中心 ==================== -->
      <template v-if="activeTab === 'profile'">
        <section class="portal-section profile-section">
          <div class="profile-layout">
            <!-- 左侧：个人信息卡片 -->
            <div class="profile-main-card">
              <div class="profile-avatar-area" :style="{ background: avatarGradient }">
                <div class="avatar-circle">{{ currentUser?.username?.charAt(0)?.toUpperCase() || '?' }}</div>
              </div>
              <div class="profile-info-area">
                <h3 class="profile-name">{{ userData?.real_name || currentUser?.username || '未知' }}</h3>
                <el-tag type="primary" effect="dark" size="large">{{ roleName }}</el-tag>
                <div class="profile-detail-grid">
                  <div class="detail-item">
                    <span class="detail-label">用户名</span>
                    <span class="detail-value">{{ userData?.username || '-' }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">手机号</span>
                    <span class="detail-value">{{ userData?.phone || '-' }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">状态</span>
                    <el-tag :type="userData?.status === 1 ? 'success' : 'danger'" size="small">
                      {{ userData?.status === 1 ? '正常' : '禁用' }}
                    </el-tag>
                  </div>
                </div>
              </div>
            </div>

            <!-- 右侧：档案卡片 -->
            <div class="profile-side-card" v-if="profileData">
              <h4 class="side-card-title">个人档案</h4>
              <div class="stat-row">
                <div class="stat-block">
                  <div class="stat-num">{{ profileData.level || 0 }}</div>
                  <div class="stat-label">等级</div>
                </div>
                <div class="stat-block">
                  <div class="stat-num">{{ profileData.height_cm || '-' }}</div>
                  <div class="stat-label">身高 cm</div>
                </div>
                <div class="stat-block">
                  <div class="stat-num">{{ profileData.weight_kg || '-' }}</div>
                  <div class="stat-label">体重 kg</div>
                </div>
              </div>
              <el-descriptions :column="2" border size="small" style="margin-top: 16px">
                <el-descriptions-item label="性别">{{ profileData.gender === 1 ? '男' : profileData.gender === 2 ? '女' : '-' }}</el-descriptions-item>
                <el-descriptions-item label="生日">{{ profileData.birthday || '-' }}</el-descriptions-item>
                <el-descriptions-item label="会员到期" v-if="profileData.expire_date">{{ profileData.expire_date }}</el-descriptions-item>
                <el-descriptions-item label="入职时间" v-if="profileData.join_time">{{ profileData.join_time }}</el-descriptions-item>
                <el-descriptions-item label="简介" :span="2">{{ profileData.intro || '暂无简介' }}</el-descriptions-item>
              </el-descriptions>
            </div>
            <div class="profile-side-card" v-else>
              <el-empty description="暂无档案信息" :image-size="60" />
            </div>
          </div>

          <!-- 教练专属：用户列表 -->
          <div class="coach-users-section">
            <h4 class="side-card-title">用户列表</h4>
            <div class="card-grid cols-4">
              <div class="user-mini-card" v-for="u in userList" :key="u.user_id">
                <div class="mini-avatar" :style="{ background: userGradient(u.user_id) }">
                  {{ (u.real_name || u.username || '?').charAt(0) }}
                </div>
                <div class="mini-info">
                  <div class="mini-name">{{ u.real_name || u.username }}</div>
                  <div class="mini-sub">{{ u.username }} &middot; {{ roleMap[u.role_id] || '未知' }}</div>
                </div>
              </div>
            </div>
            <el-empty v-if="userList.length === 0" description="暂无用户" :image-size="60" />
          </div>
        </section>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import * as api from '../api'
import { getToken } from '../api'

// ---- JWT 解码 ----
function decodeJwt() {
  try {
    const token = getToken()
    if (!token) return null
    const payload = JSON.parse(atob(token.split('.')[1]))
    return { user_id: parseInt(payload.sub), role_id: payload.role_id, username: payload.username }
  } catch { return null }
}

const currentUser = ref(null)
const roleMap = { 1: '超级管理员', 2: '运营管理员', 3: '教练', 4: '会员' }
const roleName = computed(() => roleMap[currentUser.value?.role_id] || '未知')

// ---- 页签 ----
const tabs = [
  { key: 'home', label: '首页' },
  { key: 'courses', label: '课程' },
  { key: 'actions', label: '动作库' },
  { key: 'profile', label: '个人中心' },
]
const activeTab = ref('home')

// ---- 数据 ----
const slogans = ref([])
const activities = ref([])
const courseCategories = ref([])
const courses = ref([])
const actionCategories = ref([])
const actions = ref([])
const userData = ref(null)
const profileData = ref(null)
const userList = ref([])

// ---- 筛选 ----
const courseFilter = ref(0)
const actionFilter = ref(0)

const filteredCourses = computed(() =>
  courseFilter.value === 0 ? courses.value : courses.value.filter(c => c.category_id === courseFilter.value)
)
const filteredActions = computed(() =>
  actionFilter.value === 0 ? actions.value : actions.value.filter(a => a.category_id === actionFilter.value)
)

// ---- 辅助映射 ----
const sloganGradients = [
  'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
  'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
]
const avatarGradient = 'linear-gradient(135deg, #0ea5e9 0%, #6366f1 100%)'

function difficultyText(d) {
  return { 1: '入门', 2: '进阶', 3: '挑战' }[d] || '未知'
}
function difficultyGradient(d) {
  return {
    1: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
    2: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
    3: 'linear-gradient(135deg, #f5576c 0%, #ff6a00 100%)',
  }[d] || 'linear-gradient(135deg, #a8b8d8 0%, #c2d3e8 100%)'
}
function statusGradient(s) {
  return {
    '预告': 'linear-gradient(135deg, #667eea, #764ba2)',
    '报名中': 'linear-gradient(135deg, #43e97b, #38f9d7)',
    '早鸟票': 'linear-gradient(135deg, #fa709a, #fee140)',
    '进行中': 'linear-gradient(135deg, #4facfe, #00f2fe)',
    '已结束': 'linear-gradient(135deg, #a8b8d8, #c2d3e8)',
  }[s] || 'linear-gradient(135deg, #667eea, #764ba2)'
}
function activityStatusType(s) {
  return { '预告': 'info', '报名中': 'success', '早鸟票': 'warning', '进行中': '', '已结束': 'info' }[s] || ''
}
function courseCategoryName(id) {
  return courseCategories.value.find(c => c.category_id === id)?.category_name || '-'
}
function actionCategoryName(id) {
  return actionCategories.value.find(c => c.category_id === id)?.category_name || '-'
}
function userGradient(id) {
  const gradients = [
    'linear-gradient(135deg,#667eea,#764ba2)',
    'linear-gradient(135deg,#43e97b,#38f9d7)',
    'linear-gradient(135deg,#fa709a,#fee140)',
    'linear-gradient(135deg,#4facfe,#00f2fe)',
    'linear-gradient(135deg,#f093fb,#f5576c)',
  ]
  return gradients[id % gradients.length]
}

// ---- 数据加载（按页签懒加载） ----
const loaded = ref({ home: false, courses: false, actions: false, profile: false })

async function loadHome() {
  if (loaded.value.home) return
  const [sRes, aRes] = await Promise.allSettled([api.getSlogans(), api.getActivities()])
  if (sRes.status === 'fulfilled') slogans.value = sRes.value.data
  if (aRes.status === 'fulfilled') activities.value = aRes.value.data
  loaded.value.home = true
}

async function loadCourses() {
  if (loaded.value.courses) return
  const [catRes, cRes] = await Promise.allSettled([api.getCourseCategories(), api.getCourses()])
  if (catRes.status === 'fulfilled') courseCategories.value = catRes.value.data
  if (cRes.status === 'fulfilled') courses.value = cRes.value.data
  loaded.value.courses = true
}

async function loadActions() {
  if (loaded.value.actions) return
  const [catRes, aRes] = await Promise.allSettled([api.getActionCategories(), api.getActions()])
  if (catRes.status === 'fulfilled') actionCategories.value = catRes.value.data
  if (aRes.status === 'fulfilled') actions.value = aRes.value.data
  loaded.value.actions = true
}

async function loadProfile() {
  if (loaded.value.profile) return
  if (!currentUser.value) return
  const uid = currentUser.value.user_id
  const [uRes, pRes] = await Promise.allSettled([
    api.getUserById(uid),
    api.getUserProfileByUserId(uid),
  ])
  if (uRes.status === 'fulfilled') userData.value = uRes.value.data
  if (pRes.status === 'fulfilled') profileData.value = pRes.value.data
  // 教练：始终加载用户列表
  try {
    const listRes = await api.getUsers()
    userList.value = listRes.data
  } catch { userList.value = [] }
  loaded.value.profile = true
}

const tabLoaders = { home: loadHome, courses: loadCourses, actions: loadActions, profile: loadProfile }

watch(activeTab, (tab) => {
  tabLoaders[tab]?.()
}, { immediate: false })

onMounted(() => {
  currentUser.value = decodeJwt()
  loadHome()
})
</script>

<style scoped>
/* ===== 全局 ===== */
.coach-portal { min-height: calc(100vh - 60px); background: #f0f2f5; }

/* ===== 顶部导航 ===== */
.portal-nav {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  padding: 0 32px;
  position: sticky; top: 0; z-index: 10;
}
.nav-inner { max-width: 1200px; margin: 0 auto; display: flex; align-items: center; height: 52px; }
.nav-brand { font-size: 17px; font-weight: 700; color: #fff; margin-right: 40px; letter-spacing: 0.5px; }
.nav-tabs { display: flex; gap: 4px; }
.nav-tab {
  padding: 14px 22px;
  color: rgba(255,255,255,0.65);
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}
.nav-tab:hover { color: #fff; }
.nav-tab.active { color: #fff; border-bottom-color: #4facfe; }

/* ===== 内容区 ===== */
.portal-content { max-width: 1200px; margin: 0 auto; padding: 24px 16px; }
.portal-section { margin-bottom: 32px; }
.section-title { font-size: 20px; font-weight: 600; color: #1a1a2e; margin: 0 0 18px; }

/* ===== 卡片网格 ===== */
.card-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; }
.card-grid.cols-4 { grid-template-columns: repeat(4, 1fr); }
@media (max-width: 900px) {
  .card-grid { grid-template-columns: repeat(2, 1fr); }
  .card-grid.cols-4 { grid-template-columns: repeat(2, 1fr); }
}

/* ===== 轮播 ===== */
.slogan-carousel { border-radius: 12px; overflow: hidden; margin-bottom: 32px; }
.carousel-slide {
  height: 100%; display: flex; flex-direction: column;
  justify-content: center; align-items: center; text-align: center; padding: 0 40px;
}
.carousel-title { font-size: 30px; font-weight: 700; color: #fff; margin: 0 0 12px; text-shadow: 0 2px 8px rgba(0,0,0,0.3); }
.carousel-text { font-size: 16px; color: rgba(255,255,255,0.9); max-width: 600px; line-height: 1.6; text-shadow: 0 1px 4px rgba(0,0,0,0.2); }

/* ===== 活动卡片 ===== */
.activity-card {
  background: #fff; border-radius: 10px; overflow: hidden;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06); transition: transform 0.2s, box-shadow 0.2s;
}
.activity-card:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0,0,0,0.1); }
.card-accent { height: 6px; }
.card-body { padding: 16px 18px; }
.card-top-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px; }
.card-title { font-size: 16px; font-weight: 600; color: #1a1a2e; margin: 0; }
.card-meta { font-size: 13px; color: #909399; margin: 0 0 8px; }
.card-desc { font-size: 13px; color: #606266; line-height: 1.5; margin: 0 0 10px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.card-footer { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
.footer-tag { font-size: 12px; color: #409eff; background: #ecf5ff; padding: 2px 8px; border-radius: 4px; }
.footer-tags { font-size: 12px; color: #909399; }

/* ===== 课程/动作卡片 ===== */
.course-card, .action-card {
  background: #fff; border-radius: 10px; overflow: hidden;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06); transition: transform 0.2s, box-shadow 0.2s;
}
.course-card:hover, .action-card:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0,0,0,0.1); }
.card-header-bar {
  padding: 18px 16px; display: flex; align-items: center; justify-content: space-between;
}
.card-header-title { font-size: 16px; font-weight: 600; color: #fff; text-shadow: 0 1px 4px rgba(0,0,0,0.15); }
.card-header-badge {
  font-size: 12px; color: #fff; background: rgba(255,255,255,0.25);
  padding: 2px 10px; border-radius: 12px; backdrop-filter: blur(4px);
}
.card-tip {
  font-size: 12px; color: #e6a23c; background: #fdf6ec;
  padding: 6px 10px; border-radius: 6px; margin: 8px 0 0; line-height: 1.4;
}
.schedule-text { font-size: 12px; color: #909399; }
.meta-dot { margin: 0 2px; color: #dcdfe6; }

/* ===== 筛选栏 ===== */
.filter-bar { margin-bottom: 20px; }

/* ===== 个人中心 ===== */
.profile-layout { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 28px; }
@media (max-width: 900px) { .profile-layout { grid-template-columns: 1fr; } }

.profile-main-card {
  background: #fff; border-radius: 12px; overflow: hidden;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}
.profile-avatar-area {
  padding: 32px 0; display: flex; justify-content: center;
}
.avatar-circle {
  width: 80px; height: 80px; border-radius: 50%; background: rgba(255,255,255,0.25);
  display: flex; align-items: center; justify-content: center;
  font-size: 32px; font-weight: 700; color: #fff; backdrop-filter: blur(4px);
  border: 3px solid rgba(255,255,255,0.4);
}
.profile-info-area { padding: 0 24px 24px; text-align: center; }
.profile-name { font-size: 22px; font-weight: 600; margin: 0 0 8px; color: #1a1a2e; }
.profile-detail-grid { margin-top: 16px; display: flex; justify-content: center; gap: 32px; }
.detail-item { text-align: center; }
.detail-label { display: block; font-size: 12px; color: #909399; margin-bottom: 4px; }
.detail-value { font-size: 14px; color: #303133; font-weight: 500; }

.profile-side-card {
  background: #fff; border-radius: 12px; padding: 24px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}
.side-card-title { font-size: 16px; font-weight: 600; color: #1a1a2e; margin: 0 0 16px; }
.stat-row { display: flex; justify-content: space-around; text-align: center; }
.stat-num { font-size: 28px; font-weight: 700; color: #409eff; }
.stat-label { font-size: 12px; color: #909399; margin-top: 4px; }

/* ===== 教练用户列表 ===== */
.coach-users-section { margin-top: 8px; }
.user-mini-card {
  background: #fff; border-radius: 10px; padding: 14px;
  display: flex; align-items: center; gap: 14px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05); transition: transform 0.15s;
}
.user-mini-card:hover { transform: translateY(-2px); }
.mini-avatar {
  width: 44px; height: 44px; border-radius: 50%; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  font-size: 18px; font-weight: 600; color: #fff;
}
.mini-name { font-size: 14px; font-weight: 600; color: #303133; }
.mini-sub { font-size: 12px; color: #909399; margin-top: 2px; }
</style>
