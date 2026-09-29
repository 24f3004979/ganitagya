<template>
  <div class="min-h-screen bg-white font-mono dark:bg-slate-950">
    <main class="mx-auto max-w-md px-4 sm:px-6 py-16">
      <h1 class="text-3xl font-bold tracking-tight text-slate-900 dark:text-slate-100">Create account</h1>
      <p class="mt-2 text-sm text-slate-500 dark:text-slate-400">One account tracks your level in every topic you practice.</p>

      <AuthForm mode="register" :loading="loading" :error="error" @submit="onSubmit" />

      <p class="mt-6 text-sm text-slate-500 dark:text-slate-400">
        Already registered?
        <RouterLink to="/login" class="font-semibold text-sky-600 hover:text-sky-700">Log in</RouterLink>
      </p>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import AuthForm from '../components/AuthForm.vue'
import { useAuth } from '../composables/useAuth'

const router = useRouter()
const { register, login } = useAuth()

const loading = ref(false)
const error = ref('')

async function onSubmit({ email, password }: { email: string; password: string }) {
  error.value = ''
  loading.value = true
  try {
    await register(email, password)
    await login(email, password) // straight into the quiz after signing up
    router.push('/quiz')
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Registration failed.'
  } finally {
    loading.value = false
  }
}
</script>
