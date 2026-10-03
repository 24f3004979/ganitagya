<script setup>
import { ref } from 'vue'

const emit = defineEmits(['switch'])
const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

const form = ref({ username: '', password: '' })
const repass = ref('')
const error = ref('')
const success = ref('')
const loading = ref(false)

const Register = async () => {
  error.value = ''
  success.value = ''

  if (form.value.password.length < 8) {
    error.value = 'Password must be at least 8 characters.'
    return
  }
  if (form.value.password !== repass.value) {
    error.value = 'Passwords do not match.'
    return
  }

  loading.value = true

  try {
    // Only username and password go to the backend, not the confirmation
    const response = await fetch(`${API_URL}/api/v1/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form.value),
    })

    if (response.ok) {
      success.value = 'Account created. Taking you to log in...'
      form.value = { username: '', password: '' }
      repass.value = ''
      setTimeout(() => emit('switch'), 1200)
      return
    }

    if (response.status === 409) {
      error.value = 'That username is already taken. Try another or log in.'
      return
    }

    const errorData = await response.json().catch(() => null)
    error.value =
      typeof errorData?.detail === 'string'
        ? errorData.detail
        : 'Please check your input and try again.'
  } catch (e) {
    console.error('Register request failed', e)
    error.value = 'Could not reach the server. Please try again later.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <form @submit.prevent="Register" class="w-full max-w-sm space-y-5 rounded-lg border border-slate-200 p-8">
    <div>
      <h1 class="text-2xl font-semibold tracking-tight">Create your account</h1>
      <p class="mt-1 text-sm text-slate-500">Start learning with Ganitagya.</p>
    </div>

    <div v-if="error" role="alert" class="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800">
      {{ error }}
    </div>

    <div v-if="success" role="status"
      class="rounded-md border border-green-200 bg-green-50 px-3 py-2 text-sm text-green-800">
      {{ success }}
    </div>

    <div>
      <label for="username" class="mb-1 block text-sm font-medium text-slate-700">Username</label>
      <input id="username" v-model="form.username" type="text" autocomplete="username" required
        class="w-full rounded-md border border-slate-300 px-3 py-2 focus:border-slate-900 focus:outline-none focus:ring-1 focus:ring-slate-900" />
    </div>

    <div>
      <label for="password" class="mb-1 block text-sm font-medium text-slate-700">Password</label>
      <input id="password" v-model="form.password" type="password" autocomplete="new-password" minlength="8" required
        class="w-full rounded-md border border-slate-300 px-3 py-2 focus:border-slate-900 focus:outline-none focus:ring-1 focus:ring-slate-900" />
    </div>

    <div>
      <label for="repassword" class="mb-1 block text-sm font-medium text-slate-700">Confirm password</label>
      <input id="repassword" v-model="repass" type="password" autocomplete="new-password" required
        class="w-full rounded-md border border-slate-300 px-3 py-2 focus:border-slate-900 focus:outline-none focus:ring-1 focus:ring-slate-900" />
    </div>

    <button type="submit" :disabled="loading"
      class="w-full rounded-md bg-slate-900 py-2.5 text-sm font-medium text-white hover:bg-slate-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-900 disabled:cursor-not-allowed disabled:opacity-60">
      {{ loading ? 'Creating account...' : 'Create account' }}
    </button>

    <p class="text-center text-sm text-slate-500">
      Already have an account?
      <button type="button" @click="emit('switch')" class="font-medium text-slate-900 underline underline-offset-4">
        Log in
      </button>
    </p>
  </form>
</template>
