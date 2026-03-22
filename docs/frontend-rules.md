# 前端开发规范

## 技术栈选择

根据项目类型选择对应规范。

---

## Vue 3 + Vite + Tailwind CSS

### 推荐项目结构

```
frontend/
├── src/
│   ├── assets/           # 静态资源
│   ├── components/       # 公共组件
│   │   └── common/       # 通用组件
│   ├── views/            # 页面组件
│   ├── api/              # API 调用
│   ├── utils/            # 工具函数
│   ├── router/           # 路由配置
│   ├── App.vue
│   └── main.js
├── index.html
└── vite.config.js
```

### Vue 3 规范

#### 组件规范
- 组件文件放在 `src/components/`
- 组件名用 PascalCase（如 `UserCard.vue`）
- 组件只做一件事
- 组件内代码顺序：`props` → `reactive/ref` → `computed` → `methods`

#### 组合式 API 规范
```vue
<script setup>
import { ref, computed, onMounted } from 'vue'

// 1. props
const props = defineProps({
  title: String
})

// 2. reactive/ref
const count = ref(0)

// 3. computed
const doubleCount = computed(() => count.value * 2)

// 4. methods
function increment() {
  count.value++
}

// 5. lifecycle
onMounted(() => {
  console.log('mounted')
})
</script>
```

#### 模板规范
- 使用 `<script setup>` 语法
- 优先使用 `v-if` + `v-else` 而非 `v-show`
- 循环使用 `v-for` 时必须加 `key`
- 避免在模板中使用复杂表达式

#### 样式规范
- 优先使用 Tailwind 类名
- 不创建多余的 CSS 文件
- 避免深度选择器
- 公共样式用 `:deep()` 或 `::v-deep`
- 组件样式加 `scoped`

### 状态管理
- 简单状态用 `ref` / `reactive`
- 组件间共享用 `props` / `emits`
- 不轻易引入 Pinia（等真正需要再加）
- 需要时按模块拆分 store

### API 调用规范
```javascript
// api/user.js
import request from './request'

export const getUser = (id) => request.get(`/users/${id}`)
export const createUser = (data) => request.post('/users', data)

// 组件中使用
import { getUser } from '@/api/user'
const user = await getUser(1)
```

---

## UniApp 开发规范（小程序 + H5）

### 推荐项目结构

```
uniapp/
├── src/
│   ├── api/               # API 调用
│   ├── components/        # 组件
│   ├── pages/             # 页面
│   ├── static/            # 静态资源
│   ├── store/             # 状态管理（可选 Pinia）
│   ├── styles/            # 公共样式
│   ├── utils/             # 工具函数
│   ├── App.vue
│   ├── main.js
│   ├── manifest.json      # 应用配置
│   └── pages.json         # 页面配置
├── index.html
└── package.json
```

### 平台差异处理

#### 条件编译
```javascript
// #ifdef H5
import { h5Api } from './h5'
// #endif

// #ifdef MP-WEIXIN
import { wxApi } from './weixin'
// #endif
```

#### 样式差异
```css
/* 微信小程序 */
page { background: #fff; }

/* #ifdef H5 */
page { background: #f5f5f5; }
/* #endif */
```

#### API 调用封装
```javascript
// utils/request.js
export function request(url, options) {
  return new Promise((resolve, reject) => {
    // #ifdef MP-WEIXIN
    uni.request({
      url: `/api${url}`,
      ...options,
      success: resolve,
      fail: reject
    })
    // #endif

    // #ifdef H5
    fetch(`/api${url}`, options)
      .then(resolve)
      .catch(reject)
    // #endif
  })
}
```

### 组件规范
- 使用 Vue 3 Composition API
- 生命周期用 `onMounted` 等组合式 API
- 页面通信用 `uni.$emit` / `uni.$on`
- 或使用 Pinia 进行状态管理

### 页面规范
- 页面文件放在 `pages/` 下
- 每个页面有对应的目录
- 页面配置在 `pages.json`

### H5 特定规范
- 使用 `window.location` 时注意兼容
- 路由使用 `uni.navigateTo` 而非直接操作 history
- 注意微信登录和 H5 登录的差异

### 小程序特定规范
- 页面路径在 `pages.json` 中配置
- 组件注册使用 `easycom`
- 注意包大小限制
- 样式使用 `rpx` 单位

### API 请求规范
```javascript
// api/user.js
import { request } from '@/utils/request'

export const getUserInfo = () => request('/user/info')
export const login = (data) => request('/user/login', { method: 'POST', data })
```

### 状态管理
- 简单状态用 `ref` / `reactive`
- 页面间共享用 Pinia
- 不轻易引入 Vuex

---

## 禁止事项（通用）

- ❌ 不在模板中写复杂计算逻辑
- ❌ 不在组件中写过多业务逻辑（抽取到 api/utils）
- ❌ 不在 `v-for` 中使用对象遍历（性能差）
- ❌ 不在样式中使用 `!important`
- ❌ 不创建过多层级嵌套的组件

---

## 禁止事项（Vue 3）

- ❌ 不混用 Options API 和 Composition API
- ❌ 不在 `watch` 中修改被监听的值（死循环）
- ❌ 不在 `computed` 中修改值（只读）
- ❌ 不在模板中使用 `v-html`（XSS 风险）

---

## 禁止事项（UniApp）

- ❌ 不在小程序中使用 `window.document`
- ❌ 不在小程序中使用 `axios`（用 uni.request）
- ❌ 不在组件中直接修改 `props`
- ❌ 不在 `onLoad` 中使用 `async/await`（用回调或 Promise）

---

## 变更记录

| 日期 | 更新内容 |
|------|----------|
| 2026-03-22 | 添加 Vue 3 详细规范和 UniApp 规范 |
