# FastAPI + Vue3 Demo

一个基于 FastAPI 和 Vue3 的全栈用户管理 Demo，实现了 AES 加密存储与响应体整体加密传输。

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | FastAPI + Uvicorn |
| ORM | SQLAlchemy 2.0（异步模式） |
| 数据库 | MySQL（aiomysql 驱动） |
| 加密方案 | AES-256-CBC + PKCS7 填充 + 随机 IV |
| 前端框架 | Vue 3 + Vite |
| UI 组件库 | Element Plus |
| HTTP 客户端 | Axios |
| 前端加密库 | crypto-js |

## 项目结构

```
FastAPI+Vue3 Demo/
├── start.bat                    # 一键启动脚本（同时启动前后端）
│
├── backend/                     # 后端项目
│   ├── main.py                  # FastAPI 应用入口
│   ├── requirements.txt         # Python 依赖清单
│   ├── .env                     # 环境变量配置（可选，覆盖默认配置）
│   └── app/
│       ├── __init__.py
│       ├── config.py            # 配置管理（数据库、AES 密钥）
│       ├── crypto.py            # AES-CBC 加解密工具
│       ├── database.py          # 异步数据库引擎与会话工厂
│       ├── middleware.py        # 响应体 AES 加密中间件
│       ├── models.py            # SQLAlchemy ORM 模型
│       ├── schemas.py           # Pydantic 请求/响应模型
│       └── routers/
│           ├── __init__.py
│           └── user.py          # 用户管理路由（CRUD + 登录）
│
└── frontend/                    # 前端项目
    ├── index.html               # HTML 入口
    ├── vite.config.js           # Vite 构建配置
    ├── package.json             # Node.js 依赖清单
    └── src/
        ├── main.js              # Vue 应用入口（注册 Element Plus、Router）
        ├── App.vue              # 根组件（顶部导航 + router-view）
        ├── style.css            # 全局基础样式
        ├── api/
        │   └── index.js         # Axios 实例与 API 封装（含自动解密拦截器）
        ├── router/
        │   └── index.js         # Vue Router 路由配置
        ├── utils/
        │   └── crypto.js        # AES-CBC 解密工具（与后端 crypto.py 对应）
        └── views/
            ├── UserList.vue     # 用户管理页面（表格、分页、增删改）
            └── Login.vue        # 登录页面
```

## 各文件详细说明

### 根目录

| 文件 | 说明 |
|------|------|
| `start.bat` | 双击即可同时启动前后端。会打开两个命令行窗口：后端跑在 `localhost:8001`，前端跑在 `localhost:5173`。 |

### 后端 — `backend/`

| 文件 | 说明 |
|------|------|
| `main.py` | FastAPI 应用入口。通过 `lifespan` 在启动时自动建表（`create_all`），注册 CORS 跨域中间件和响应加密中间件，挂载用户路由。 |
| `requirements.txt` | Python 依赖包列表，使用 `pip install -r requirements.txt` 安装。 |
| `.env` | 可选的环境变量文件，可覆盖 `config.py` 中的默认值（数据库地址、端口、密码、AES 密钥等）。 |

### 后端 — `backend/app/`

| 文件 | 说明 |
|------|------|
| `config.py` | 基于 `pydantic-settings` 的配置类 `Settings`，管理数据库连接参数（`DB_HOST`、`DB_PORT`、`DB_USER`、`DB_PASSWORD`、`DB_NAME`）和 AES 密钥（`AES_SECRET_KEY`）。支持通过 `.env` 文件覆盖。 |
| `crypto.py` | AES-256-CBC 加解密工具。`encrypt(plaintext, key)` 将明文加密为 base64 字符串（格式：`IV[16字节] + 密文`），`decrypt(encrypted, key)` 反向解密。密钥自动补齐到 32 字节，使用 PKCS7 填充，每次加密使用随机 IV。 |
| `database.py` | 创建异步 SQLAlchemy 引擎（`create_async_engine`）和会话工厂（`async_sessionmaker`），提供 `get_db()` 依赖注入函数供路由使用。 |
| `middleware.py` | `EncryptResponseMiddleware` 中间件，拦截所有 JSON 响应，将整个响应体序列化后进行 AES 加密，返回 `{"data": "<密文>"}` 格式。Swagger 文档路径（`/docs`、`/redoc`、`/openapi.json`）不受影响。 |
| `models.py` | 定义 `SysUser` ORM 模型，映射到 `sys_user` 表，包含 `user_id`、`username`、`password`、`real_name`、`phone`、`status` 字段。 |
| `schemas.py` | 定义 Pydantic 模型：`UserCreate`（创建请求）、`UserUpdate`（更新请求）、`UserResponse`（响应，含加密密码）、`UserLogin`（登录请求）、`LoginResponse`（登录响应）、`PageResponse`（通用分页包装）。 |

### 后端 — `backend/app/routers/`

| 文件 | 说明 |
|------|------|
| `user.py` | 用户管理路由，前缀 `/api/users`。提供 6 个接口：创建用户（POST）、分页列表（GET）、按 ID 查询（GET）、更新用户（PUT）、删除用户（DELETE）、登录验证（POST `/login`）。创建和更新时密码自动 AES 加密存储，登录时从数据库取出加密密码解密后与明文比对。 |

### 前端 — `frontend/src/`

| 文件 | 说明 |
|------|------|
| `main.js` | Vue 应用入口，注册 Element Plus 组件库和 Vue Router。 |
| `App.vue` | 根组件，包含顶部导航栏（Element Plus Menu）和 `<router-view>` 路由出口。 |
| `style.css` | 全局基础样式（清除默认 margin）。 |

### 前端 — `frontend/src/api/`

| 文件 | 说明 |
|------|------|
| `index.js` | 创建 Axios 实例（`baseURL` 指向后端 `localhost:8001`），注册响应拦截器：自动检测 `{"data": "<密文>"}` 格式并调用 `crypto.js` 解密还原为原始 JSON。封装了 `getUsers`、`getUserById`、`createUser`、`updateUser`、`deleteUser`、`login` 等 API 函数。 |

### 前端 — `frontend/src/utils/`

| 文件 | 说明 |
|------|------|
| `crypto.js` | AES-256-CBC 解密函数，与后端 `crypto.py` 的加密逻辑完全对应。将密钥补齐到 32 字节（null padding），从 base64 密文中分离 IV 和密文，使用 CBC 模式 + PKCS7 填充解密。 |

### 前端 — `frontend/src/router/`

| 文件 | 说明 |
|------|------|
| `index.js` | Vue Router 配置，定义 `/users`（用户管理）和 `/login`（登录）两个路由，均使用懒加载。 |

### 前端 — `frontend/src/views/`

| 文件 | 说明 |
|------|------|
| `UserList.vue` | 用户管理主页面。包含 Element Plus 数据表格（显示用户 ID、用户名、加密密码、真实姓名、手机号、状态）、分页组件、新增/编辑对话框（表单）、删除确认。所有数据通过 API 获取并由拦截器自动解密。 |
| `Login.vue` | 登录页面，居中卡片式表单，输入用户名和明文密码后调用 `/api/users/login` 接口，后端解密比对后返回结果。 |

## 数据加密流程

```
┌─────────────────────────────────────────────────────────┐
│                      写入流程                            │
│                                                         │
│  前端明文密码 ──POST──▶ 后端 crypto.encrypt() ──▶ DB 密文 │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                      读取流程                            │
│                                                         │
│  DB 数据 ──▶ 路由返回 JSON ──▶ 中间件整体 AES 加密        │
│       ──▶ 返回 {"data":"密文"} ──▶ 前端拦截器自动解密      │
│       ──▶ 还原原始 JSON ──▶ 页面渲染                     │
└─────────────────────────────────────────────────────────┘
```

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/users` | 创建用户（密码 AES 加密存储） |
| GET | `/api/users` | 分页查询用户列表 |
| GET | `/api/users/{user_id}` | 根据 ID 查询单个用户 |
| PUT | `/api/users/{user_id}` | 更新用户信息（密码自动加密） |
| DELETE | `/api/users/{user_id}` | 删除用户 |
| POST | `/api/users/login` | 登录验证（解密比对） |

所有接口的响应体均被中间件加密为 `{"data": "<AES密文>"}` 格式。

## 快速启动

### 环境要求

- Python 3.12+
- Node.js 18+
- MySQL 5.7+（数据库名 `FastAPI_Vue3`）

### 一键启动

双击根目录的 `start.bat`，会自动启动后端和前端。

### 手动启动

```bash
# 后端
cd backend
pip install -r requirements.txt
.venv/Scripts/python.exe -m uvicorn main:app --reload --port 8001

# 前端
cd frontend
npm install
npm run dev
```

### 访问

- 前端页面：http://localhost:5173
- 后端 API 文档：http://localhost:8001/docs
- 所有用户默认密码：`qweqwe`
