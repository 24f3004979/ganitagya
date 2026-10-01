<script setup>
import { reactive, ref } from 'vue'
import AuthField from './AuthField.vue'

defineProps({
  loading: { type: Boolean, default: false },
  error: { type: String, default: '' }, // server-side error message
})
// submit payload: { email, password, remember }
const emit = defineEmits(['submit', 'switch', 'forgot'])

const form = reactive({ email: '', password: '', remember: false })
const errors = reactive({ email: '', password: '' })
const shake = ref(false)

const validate = () => {
  errors.email = /^\S+@\S+\.\S+$/.test(form.email.trim()) ? '' : 'Enter a valid email address.'
  errors.password = form.password ? '' : 'Enter your password.'
  return !errors.email && !errors.password
}

const onSubmit = () => {
  if (!validate()) {
    shake.value = false
    requestAnimationFrame(() => (shake.value = true))
    return
  }
  emit('submit', { email: form.email.trim(), password: form.password, remember: form.remember })
}
</script>

<template>
  <form novalidate @submit.prevent="onSubmit" @animationend="shake = false" :class="shake && 'shake'" class="space-y-5">

    <div v-if="error" role="alert"
         class="rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-700 dark:text-red-300">
      {{ error }}
    </div>

    <AuthField id="login-email" v-model="form.email" label="Email" type="email"
               autocomplete="email" placeholder="you@example.com" :error="errors.email" />

    <AuthField id="login-password" v-model="form.password" label="Password" type="password"
               autocomplete="current-password" placeholder="Your password" :error="errors.password" />

    <div class="flex items-center justify-between text-sm">
      <label class="flex cursor-pointer items-center gap-2 text-slate-600 dark:text-slate-400">
        <input v-model="form.remember" type="checkbox" class="h-4 w-4 rounded border-slate-300 accent-indigo-600" />
        Remember me
      </label>
      <button type="button" @click="emit('forgot')"
              class="font-semibold text-indigo-600 hover:underline dark:text-indigo-400">Forgot password?</button>
    </div>

    <button type="submit" :disabled="loading"
            class="relative w-full overflow-hidden rounded-xl bg-indigo-600 py-3 font-semibold text-white shadow-lg shadow-indigo-500/30
                   transition-all duration-200 hover:-translate-y-0.5 hover:bg-indigo-500 active:translate-y-0
                   disabled:cursor-not-allowed disabled:opacity-70 disabled:hover:translate-y-0
                   focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-500">
      <span class="inline-flex items-center justify-center gap-2">
        <svg v-if="loading" class="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
          <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="3" class="opacity-25" />
          <path d="M21 12a9 9 0 00-9-9" stroke="currentColor" stroke-width="3" stroke-linecap="round" />
        </svg>
        {{ loading ? 'Logging in…' : 'Log in' }}
      </span>
    </button>

    <p class="text-center text-sm text-slate-600 dark:text-slate-400">
      New to Ganitagya?
      <button type="button" @click="emit('switch')" class="font-semibold text-indigo-600 hover:underline dark:text-indigo-400">Create an account</button>
    </p>
  </form>
</template>

<style scoped>
.shake { animation: shake 0.4s cubic-bezier(0.36, 0.07, 0.19, 0.97); }
@keyframes shake {
  10%, 90% { transform: translateX(-2px); }
  20%, 80% { transform: translateX(4px); }
  30%, 50%, 70% { transform: translateX(-6px); }
  40%, 60% { transform: translateX(6px); }
}
@media (prefers-reduced-motion: reduce) { .shake { animation: none; } }
</style>
