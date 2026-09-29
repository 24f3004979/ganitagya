import { reactive, computed } from 'vue'
import { request, ENDPOINTS, TOKEN_KEY } from '../api/client'

const EMAIL_KEY = 'chintan_email'
const SID_KEY = 'chintan_student_id'

// Module-level state, so every component shares one session without needing Pinia.
const state = reactive({
  token: localStorage.getItem(TOKEN_KEY) ?? '',
  email: localStorage.getItem(EMAIL_KEY) ?? '',
  studentId: localStorage.getItem(SID_KEY) ? Number(localStorage.getItem(SID_KEY)) : (null as number | null)
})

function persist() {
  const set = (k: string, v: string) => (v ? localStorage.setItem(k, v) : localStorage.removeItem(k))
  set(TOKEN_KEY, state.token)
  set(EMAIL_KEY, state.email)
  set(SID_KEY, state.studentId === null ? '' : String(state.studentId))
}

// Login returns the token directly on success, or a {message, status} dict on failure.
function extractToken(res: any): string | null {
  if (typeof res === 'string') return res
  if (res && typeof res === 'object') return res.access_token ?? res.token ?? null
  return null
}

// The student-id route's response shape isn't fixed yet, so accept the common ones.
function extractStudentId(res: any): number | null {
  const v = typeof res === 'object' && res !== null ? res.student_id ?? res.id ?? res.studentId : res
  const n = Number(v)
  return Number.isInteger(n) ? n : null
}

export function useAuth() {
  const isLoggedIn = computed(() => !!state.token)

  async function register(email: string, password: string) {
    const res = await request(ENDPOINTS.register, { method: 'POST', body: { email, password } })
    // Registration reports its outcome in the body: status 200 = created.
    if (res?.status !== 200) throw new Error(res?.message ?? 'Registration failed.')
  }

  async function login(email: string, password: string) {
    const res = await request(ENDPOINTS.login, { method: 'POST', body: { email, password } })
    const token = extractToken(res)
    if (!token) throw new Error(res?.message?.trim() || 'Login failed.')

    state.token = token
    state.email = email
    state.studentId = null
    persist()
    await loadStudentId()
  }

  async function loadStudentId() {
    const res = await request(`${ENDPOINTS.studentId}?username=${encodeURIComponent(state.email)}`)
    const id = extractStudentId(res)
    if (id === null) throw new Error("Logged in, but couldn't find your student profile.")
    state.studentId = id
    persist()
  }

  function logout() {
    state.token = ''
    state.email = ''
    state.studentId = null
    persist()
  }

  return { state, isLoggedIn, register, login, loadStudentId, logout }
}
