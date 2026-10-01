<script setup>
import { reactive, ref, computed } from 'vue'
import AuthField from './AuthField.vue'

defineProps({
  loading: { type: Boolean, default: false },
  error: { type: String, default: '' }, // server-side error message
})
// submit payload: { name, email, password }
const emit = defineEmits(['submit', 'switch'])

const form = reactive({ name: '', email: '', password: '', confirm: '', terms: false })
const errors = reactive({ name: '', email: '', password: '', confirm: '', terms: '' })
const shake = ref(false)

/* Password strength: 0-4 */
const score = computed(() => {
  const p = form.password
  let s = 0
  if (p.length >= 8) s++
  if (/[a-z]/.test(p) && /[A-Z]/.test(p)) s++
  if (/\d/.test(p)) s++
  if (/[^A-Za-z0-9]/.test(p)) s++
  return p ? Math.max(s, 1) : 0
})
const strengthLabel = computed(() => ['', 'Weak', 'Fair', 'Good', 'Strong'][score.value])
const barColor = computed(() => ['', 'bg-red-500', 'bg-amber-500', 'bg-lime-500', 'bg-emerald-500'][score.value])

const validate = () => {
  errors.name = form.name.trim().length >= 2 ? '' : 'Enter your name.'
  errors.email = /^\S+@\S+\.\S+$/.test(form.email.trim()) ? '' : 'Enter a valid email address.'
  errors.password = form.password.length >= 8 ? '' : 'Use at least 8 characters.'
  errors.confirm = form.confirm === form.password ? '' : 'Passwords do not match.'
  errors.terms = form.terms ? '' : 'Accept the terms to continue.'
  return Object.values(errors).every((e) => !e)
}

const onSubmit = () => {
  if (!validate()) {
    shake.value = false
    requestAnimationFrame(() => (shake.value = true))
    return
  }
  emit('submit', { name: form.name.trim(), email: form.email.trim(), password: form.password })
}
</script>

<template>
  <form novalidate @submit.prevent="onSubmit" @animationend="shake = false" :class="shake && 'shake'" class="space-y-5">

    <div v-if="error" role="alert"
         class="rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-700 dark:text-red-300">
      {{ error }}
    </div>

    <AuthField id="reg-name" v-model="form.name" label="Full name" autocomplete="name"
               placeholder="Your name" :error="errors.name" />

    <AuthField id="reg-email" v-model="form.email" label="Email" type="email" autocomplete="email"
               placeholder="you@example.com" :error="errors.email" />

    <div>
      <AuthField id="reg-password" v-model="form.password" label="Password" type="password"
                 autocomplete="new-password" placeholder="At least 8 characters" :error="errors.password" />

      <!-- Strength meter -->
      <div class="mt-2 flex items-center gap-2" aria-live="polite">
        <div class="flex flex-1 gap-1">
          <span v-for="n in 4" :key="n" class="h-1.5 flex-1 rounded-full bg-slate-200 transition-colors duration-300 dark:bg-slate-800"
                :class="n <= score && barColor"></span>
        </div>
        <span class="w-12 text-right text-xs font-medium text-slate-500">{{ strengthLabel }}</span>
      </div>
    </div>

    <AuthField id="reg-confirm" v-model="form.confirm" label="Confirm password" type="password"
               autocomplete="new-password" placeholder="Repeat your password" :error="errors.confirm" />

    <div>
      <label class="flex cursor-pointer items-start gap-2 text-sm text-slate-600 dark:text-slate-400">
        <input v-model="form.terms" type="checkbox" class="mt-0.5 h-4 w-4 rounded border-slate-300 accent-emerald-600" />
        <span>I agree to the <a href="/terms" class="font-semibold text-emerald-600 hover:underline dark:text-emerald-400">Terms</a>
          and <a href="/privacy" class="font-semibold text-emerald-600 hover:underline dark:text-emerald-400">Privacy Policy</a>.</span>
      </label>
      <p v-if="errors.terms" role="alert" class="mt-1.5 text-sm text-red-600 dark:text-red-400">{{ errors.terms }}</p>
    </div>

    <button type="submit" :disabled="loading"
            class="w-full rounded-xl bg-emerald-600 py-3 font-semibold text-white shadow-lg shadow-emerald-500/30
                   transition-all duration-200 hover:-translate-y-0.5 hover:bg-emerald-500 active:translate-y-0
                   disabled:cursor-not-allowed disabled:opacity-70 disabled:hover:translate-y-0
                   focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald-500">
      <span class="inline-flex items-center justify-center gap-2">
        <svg v-if="loading" class="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
          <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="3" class="opacity-25" />
          <path d="M21 12a9 9 0 00-9-9" stroke="currentColor" stroke-width="3" stroke-linecap="round" />
        </svg>
        {{ loading ? 'Creating account…' : 'Create account' }}
      </span>
    </button>

    <p class="text-center text-sm text-slate-600 dark:text-slate-400">
      Already have an account?
      <button type="button" @click="emit('switch')" class="font-semibold text-emerald-600 hover:underline dark:text-emerald-400">Log in</button>
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
