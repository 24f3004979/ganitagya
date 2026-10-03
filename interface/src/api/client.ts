// Single place for backend paths. Change these once and every view follows.
export const BASE_URL: string = 'http://localhost:8000'

export const ENDPOINTS = {
  register: '/api/v1/register',
  login: '/api/v1/login',
  studentId: '/api/v1/fetch-id',
  quizStart: '/quiz/start',
  quizAnswer: '/quiz/answer',
  quizAbandon: (studentId: number) => `/quiz/abandon/${studentId}`
}

export const TOKEN_KEY = 'chintan_token'

export class ApiError extends Error {
  status: number
  constructor(message: string, status: number) {
    super(message)
    this.status = status
  }
}

interface Options {
  method?: 'GET' | 'POST' | 'DELETE'
  body?: unknown
}

export async function request<T = any>(path: string, opts: Options = {}): Promise<T> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  const token = localStorage.getItem(TOKEN_KEY)
  if (token) headers.Authorization = `Bearer ${token}`

  let res: Response
  try {
    res = await fetch(BASE_URL + path, {
      method: opts.method ?? 'GET',
      headers,
      body: opts.body === undefined ? undefined : JSON.stringify(opts.body)
    })
  } catch {
    throw new ApiError("Can't reach the server. Check that the backend is running.", 0)
  }

  const data = await res.json().catch(() => null)
  if (!res.ok) {
    // FastAPI puts messages in `detail`; validation errors send a list there.
    const detail = data?.detail
    const msg = typeof detail === 'string' ? detail : data?.message ?? `Request failed (${res.status})`
    throw new ApiError(msg, res.status)
  }
  return data as T
}
