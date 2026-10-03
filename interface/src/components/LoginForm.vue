<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const emit = defineEmits(['switch'])
const router = useRouter()
const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

const form = ref({ username: '', password: '' })
const error = ref('')
const loading = ref(false)

const Login = async () => {
  error.value = ''
  loading.value = true

  try {
    const response = await fetch(`${API_URL}/api/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form.value),
    })

    if (response.ok) {
      const data = await response.json()
      localStorage.setItem('access_token', data.token)
      router.push('/dashboard')
      return
    }

    if (response.status === 400) {
      error.value = 'User does not exist. Create an account first.'
      return
    }

    if (response.status === 401) {
      error.value = 'Wrong username or password.'
      return
    }

    const errorData = await response.json().catch(() => null)
    error.value =
      typeof errorData?.detail === 'string'
        ? errorData.detail
        : 'Please check your input and try again.'
  } catch (e) {
    console.error('Login request failed', e)
    error.value = 'Could not reach the server. Please try again later.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <form @submit.prevent="Login" class="w-full max-w-sm space-y-5 rounded-lg border border-slate-200 p-8">
    <div>
      <h1 class="text-2xl font-semibold tracking-tight">Welcome back</h1>
      <p class="mt-1 text-sm text-slate-500">Log in to continue learning.</p>
    </div>

    <div v-if="error" role="alert" class="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800">
      {{ error }}
    </div>

    <div>
      <label for="username" class="mb-1 block text-sm font-medium text-slate-700">Username</label>
      <input id="username" v-model="form.username" type="text" autocomplete="username" required
        class="w-full rounded-md border border-slate-300 px-3 py-2 focus:border-slate-900 focus:outline-none focus:ring-1 focus:ring-slate-900" />
    </div>

    <div>
      <label for="password" class="mb-1 block text-sm font-medium text-slate-700">Password</label>
      <input id="password" v-model="form.password" type="password" autocomplete="current-password" required
        class="w-full rounded-md border border-slate-300 px-3 py-2 focus:border-slate-900 focus:outline-none focus:ring-1 focus:ring-slate-900" />
    </div>

    <button type="submit" :disabled="loading"
      class="w-full rounded-md bg-slate-900 py-2.5 text-sm font-medium text-white hover:bg-slate-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-900 disabled:cursor-not-allowed disabled:opacity-60">
      {{ loading ? 'Logging in...' : 'Log in' }}
    </button>

    <p class="text-center text-sm text-slate-500">
      New here?
      <button type="button" @click="emit('switch')" class="font-medium text-slate-900 underline underline-offset-4">
        Create an account
      </button>
    </p>
  </form>
</template>
