<template>
  <div class="min-h-screen bg-white font-mono dark:bg-slate-950">
    <main class="mx-auto max-w-md px-4 sm:px-6 py-16">
      <h1 class="text-3xl font-bold tracking-tight text-slate-900 dark:text-slate-100">Log in</h1>
      <p class="mt-2 text-sm text-slate-500 dark:text-slate-400">Pick up your quiz where your levels left off.</p>

      <AuthForm mode="login" :loading="loading" :error="error" @submit="onSubmit" />

      <p class="mt-6 text-sm text-slate-500 dark:text-slate-400">
        New here?
        <RouterLink to="/register" class="font-semibold text-sky-600 hover:text-sky-700">Create an account</RouterLink>
      </p>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import AuthForm from '../components/AuthForm.vue'
import { useAuth } from '../composables/useAuth'

const router = useRouter()
const route = useRoute()
const { login } = useAuth()

const loading = ref(false)
const error = ref('')

async function onSubmit({ email, password }: { email: string; password: string }) {
  error.value = ''
  loading.value = true
  try {
    await login(email, password)
    router.push((route.query.redirect as string) || '/quiz')
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Login failed.'
  } finally {
    loading.value = false
  }
}
</script>
