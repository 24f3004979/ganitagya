<template>
  <form @submit.prevent="onSubmit" class="mt-6 space-y-4" novalidate>
    <div>
      <label for="email" class="block text-sm font-semibold text-slate-700 dark:text-slate-300">Email</label>
      <input
        id="email"
        v-model.trim="email"
        type="email"
        autocomplete="email"
        placeholder="you@school.com"
        class="mt-1 w-full rounded-lg border border-slate-200 bg-white px-4 py-3 text-slate-900 outline-none focus:ring-2 focus:ring-sky-500 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
      />
    </div>

    <div>
      <label for="password" class="block text-sm font-semibold text-slate-700 dark:text-slate-300">Password</label>
      <input
        id="password"
        v-model="password"
        type="password"
        :autocomplete="mode === 'login' ? 'current-password' : 'new-password'"
        class="mt-1 w-full rounded-lg border border-slate-200 bg-white px-4 py-3 text-slate-900 outline-none focus:ring-2 focus:ring-sky-500 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
      />
    </div>

    <div v-if="mode === 'register'">
      <label for="confirm" class="block text-sm font-semibold text-slate-700 dark:text-slate-300">Confirm password</label>
      <input
        id="confirm"
        v-model="confirm"
        type="password"
        autocomplete="new-password"
        class="mt-1 w-full rounded-lg border border-slate-200 bg-white px-4 py-3 text-slate-900 outline-none focus:ring-2 focus:ring-sky-500 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
      />
    </div>

    <p v-if="shownError" role="alert" class="text-sm text-red-600 dark:text-red-400">{{ shownError }}</p>

    <button
      type="submit"
      :disabled="loading"
      class="w-full rounded-lg bg-sky-600 px-6 py-3 font-semibold text-white transition-transform hover:bg-sky-700 active:scale-95 disabled:cursor-not-allowed disabled:opacity-60"
    >
      {{ loading ? 'Please wait…' : mode === 'login' ? 'Log in' : 'Create account' }}
    </button>
  </form>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const props = defineProps<{
  mode: 'login' | 'register'
  loading?: boolean
  error?: string
}>()

const emit = defineEmits<{ (e: 'submit', payload: { email: string; password: string }): void }>()

const email = ref('')
const password = ref('')
const confirm = ref('')
const localError = ref('')

const shownError = computed(() => localError.value || props.error || '')

function onSubmit() {
  localError.value = ''
  if (!/^\S+@\S+\.\S+$/.test(email.value)) return (localError.value = 'Enter a valid email address.')
  if (!password.value) return (localError.value = 'Enter your password.')
  if (props.mode === 'register') {
    if (password.value.length < 6) return (localError.value = 'Use at least 6 characters for your password.')
    if (password.value !== confirm.value) return (localError.value = "The two passwords don't match.")
  }
  emit('submit', { email: email.value, password: password.value })
}
</script>
