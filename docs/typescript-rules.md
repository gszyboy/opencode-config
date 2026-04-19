# TypeScript 规范

## 基础规范

### 文件命名
- 文件名使用 kebab-case：`user-service.ts`
- 类型定义文件：`*.d.ts`
- 测试文件：`*.test.ts` 或 `*.spec.ts`
- 组件文件：`.vue` / `.tsx`

### 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 变量/函数 | camelCase | `getUserInfo` |
| 类/接口/类型 | PascalCase | `UserInfo`, `ResponseData` |
| 常量 | UPPER_SNAKE_CASE | `MAX_COUNT`, `API_BASE_URL` |
| 文件名 | kebab-case | `user-api.ts` |
| 枚举成员 | PascalCase | `UserStatus.Active` |

### 类型定义

```typescript
// 使用 interface 定义对象结构
interface User {
  id: number
  name: string
  email: string
}

// 使用 type 定义联合类型、交叉类型
type UserRole = 'admin' | 'user' | 'guest'
type UserWithRole = User & { role: UserRole }

// 使用 enum 定义枚举（慎用，优先用联合类型）
enum Status {
  Active = 'active',
  Inactive = 'inactive'
}
```

### 基础类型规范

```typescript
// ✅ 好：显式类型注解
const count: number = 0
const name: string = 'John'
const isActive: boolean = true
const list: string[] = []
const obj: Record<string, number> = {}

// ✅ 好：类型推断
const count = 0 // number
const name = 'John' // string
const list = [] // never[]，需要手动指定类型

// ❌ 不好：any
const data: any = fetchData()

// ✅ 好：unknown + 类型守卫
const data: unknown = fetchData()
if (typeof data === 'string') {
  console.log(data.toUpperCase())
}
```

---

## 函数规范

### 函数定义

```typescript
// ✅ 好：箭头函数 + 类型注解
const getUser = (id: number): User => {
  return users.find(u => u.id === id)
}

// ✅ 好：可选参数 + 默认值
const createUser = (name: string, age?: number = 18): User => {
  return { id: Date.now(), name, age }
}

// ✅ 好：函数重载
function parseInput(input: string): string[]
function parseInput(input: number): number
function parseInput(input: string | number): string[] | number {
  // 实现
}

// ❌ 不好：any 返回值
const fetchData = (): any => {
  return api.get()
}
```

### 泛型

```typescript
// ✅ 好：使用泛型
function getItem<T>(list: T[], id: number): T | undefined {
  return list.find(item => item.id === id)
}

// ✅ 好：约束泛型
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key]
}

// ✅ 好：内置泛型
const list: Array<User> = []
const promise: Promise<string> = Promise.resolve('ok')
const map: Map<string, number> = new Map()
```

---

## 接口和类型

### 命名规范

```typescript
// ✅ 好：I 前缀（可选，统一即可）
interface IUserService {
  getUser(id: number): Promise<User>
}

// ✅ 好：不用前缀，直接 PascalCase
interface UserService {
  getUser(id: number): Promise<User>
}

// ✅ 好：Response/Request 后缀
interface LoginResponse {
  token: string
  user: User
}

interface LoginRequest {
  username: string
  password: string
}
```

### 解构和类型推导

```typescript
// ✅ 好：解构时指定类型
const { name, age }: { name: string; age: number } = user

// ✅ 好：类型守卫
if (user && typeof user === 'object' && 'id' in user) {
  // user 推断为 { id: unknown }
}
```

---

## Vue 3 + TypeScript

### 组件定义

```vue
<script setup lang="ts">
import { ref, computed } from 'vue'

// ✅ 好：定义 Props
interface Props {
  title: string
  count?: number
}

const props = withDefaults(defineProps<Props>(), {
  count: 0
})

// ✅ 好：定义 Emits
const emit = defineEmits<{
  (e: 'update', value: number): void
  (e: 'delete'): void
}>()

// ✅ 好：使用 ref/reactive + 类型
const loading = ref<boolean>(false)
const userList = ref<User[]>([])

// ✅ 好：使用 computed
const doubledCount = computed<number>(() => props.count * 2)

// ✅ 好：函数定义
const handleClick = (): void => {
  emit('update', props.count + 1)
}
</script>
```

### API 类型定义

```typescript
// types/api.ts
export interface ApiResponse<T = unknown> {
  code: number
  message: string
  data: T
}

export interface PaginationParams {
  page: number
  pageSize: number
}

export interface PaginatedResponse<T> {
  list: T[]
  total: number
  page: number
  pageSize: number
}

// api/user.ts
import type { ApiResponse, User } from '@/types/api'

export const getUser = (id: number): Promise<ApiResponse<User>> => {
  return request.get(`/users/${id}`)
}
```

---

## 类型断言和守卫

### 类型断言

```typescript
// ✅ 好：使用 as（断言为更具体类型）
const data = response.data as User

// ❌ 不好：双重断言（除非万不得已）
const data = response.data as unknown as User

// ✅ 好：类型守卫函数
function isUser(obj: unknown): obj is User {
  return typeof obj === 'object' && obj !== null && 'id' in obj
}
```

### 严格空检查

```typescript
// ✅ 好：显式检查
if (user !== null && user !== undefined) {
  console.log(user.name)
}

// ✅ 好：可选链 + 空值合并
const name = user?.name ?? '匿名'

// ✅ 好：使用 Array.isArray
if (Array.isArray(list)) {
  list.forEach(item => console.log(item))
}
```

---

## 禁止事项

- ❌ 禁止使用 `any`，使用 `unknown` + 类型守卫
- ❌ 禁止类型断言滥用（双重断言）
- ❌ 禁止 `var`，使用 `const` / `let`
- ❌ 禁止 `ts-ignore`，使用 `ts-expect-error`（确有必要时）
- ❌ 禁止裸类型：`Array` 用 `T[]` 或 `Array<T>`
- ❌ 禁止隐式 any（函数参数必须有类型）

---

## tsconfig.json 规范

```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true
  }
}
```


