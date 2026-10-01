<script setup>
import { ref } from 'vue'

// Set VITE_API_URL in .env, e.g. https://ganitagya-waitlist-xxxxx-uc.a.run.app
const API_URL = import.meta.env.VITE_API_URL

const emit = defineEmits(['joined'])

const email = ref('')
const website = ref('') // honeypot: must stay empty
const status = ref('idle') // idle | loading | success | error
const message = ref('')

async function join() {
  if (status.value === 'loading') return
  if (!/^\S+@\S+\.\S+$/.test(email.value.trim())) {
    status.value = 'error'
    message.value = 'Enter a valid email address.'
    return
  }

  status.value = 'loading'
  message.value = ''
  try {
    const res = await fetch(`${API_URL}/api/waitlist`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email.value.trim(), website: website.value }),
    })
    const data = await res.json().catch(() => ({}))
    if (!res.ok) throw new Error(data.error || 'Something went wrong. Please try again.')

    status.value = 'success'
    emit('joined', email.value.trim())
    email.value = ''
  } catch (e) {
    status.value = 'error'
    message.value = e.message === 'Failed to fetch' ? 'Could not reach the server. Try again in a moment.' : e.message
  }
}
</script>

<template>
  <section id="waitlist" class="w-full max-w-md text-center">
    <h2 class="text-2xl font-bold tracking-wide text-slate-900 dark:text-white">Join the waitlist</h2>
    <p class="mt-2 text-sm text-slate-600 dark:text-slate-400">
      Be first in line when Siddhi, Chintan and Mool launch.
    </p>

    <!-- Success state -->
    <Transition name="pop" mode="out-in">
      <div v-if="status === 'success'" key="ok" role="status"
           class="mt-6 flex items-center justify-center gap-3 rounded-2xl border border-emerald-500/30 bg-emerald-500/10 px-5 py-4 text-emerald-700 dark:text-emerald-300">
        <svg class="h-6 w-6 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10" class="opacity-30" />
          <path class="check" d="M7 12.5l3.5 3.5L17 9" />
        </svg>
        <span class="font-semibold">You're on the list. We'll be in touch!</span>
      </div>

      <form v-else key="form" novalidate @submit.prevent="join" class="mt-6">
        <div class="flex flex-col gap-3 sm:flex-row">
          <label for="waitlist-email" class="sr-only">Email address</label>
          <input
            id="waitlist-email"
            v-model="email"
            type="email"
            autocomplete="email"
            placeholder="you@example.com"
            :aria-invalid="status === 'error'"
            aria-describedby="waitlist-msg"
            class="min-w-0 flex-1 rounded-xl border bg-white px-4 py-3 text-base text-slate-900 placeholder-slate-400 outline-none
                   transition-all duration-200 focus:-translate-y-0.5 focus:ring-4
                   dark:bg-slate-900 dark:text-white dark:placeholder-slate-600"
            :class="status === 'error'
              ? 'border-red-500 focus:ring-red-500/20'
              : 'border-slate-300 focus:border-indigo-500 focus:ring-indigo-500/20 dark:border-slate-700 dark:focus:border-indigo-400'"
          />

          <!-- Honeypot: hidden from people and screen readers, bots tend to fill it -->
          <input v-model="website" type="text" name="website" tabindex="-1" autocomplete="off" aria-hidden="true"
                 class="absolute -left-[9999px] h-0 w-0 opacity-0" />

          <button
            type="submit"
            :disabled="status === 'loading'"
            class="inline-flex items-center justify-center gap-2 rounded-xl bg-indigo-600 px-6 py-3 font-semibold text-white shadow-lg shadow-indigo-500/30
                   transition-all duration-200 hover:-translate-y-0.5 hover:bg-indigo-500 active:translate-y-0
                   disabled:cursor-not-allowed disabled:opacity-70 disabled:hover:translate-y-0
                   focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-500"
          >
            <svg v-if="status === 'loading'" class="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="3" class="opacity-25" />
              <path d="M21 12a9 9 0 00-9-9" stroke="currentColor" stroke-width="3" stroke-linecap="round" />
            </svg>
            {{ status === 'loading' ? 'Joining…' : 'Join' }}
          </button>
        </div>

        <p id="waitlist-msg" role="alert" class="mt-2 min-h-5 text-left text-sm text-red-600 dark:text-red-400">
          {{ status === 'error' ? message : '' }}
        </p>
        <p class="mt-1 text-xs text-slate-500">We only use your email to tell you about the launch. No spam.</p>
      </form>
    </Transition>
  </section>
</template>

<style scoped>
.pop-enter-active, .pop-leave-active { transition: all 0.35s cubic-bezier(0.2, 1.2, 0.35, 1); }
.pop-enter-from { opacity: 0; transform: scale(0.92) translateY(8px); }
.pop-leave-to { opacity: 0; transform: translateY(-6px); }

.check { stroke-dasharray: 24; stroke-dashoffset: 24; animation: draw 0.5s 0.2s ease forwards; }
@keyframes draw { to { stroke-dashoffset: 0; } }

@media (prefers-reduced-motion: reduce) {
  .pop-enter-active, .pop-leave-active { transition: none; }
  .check { animation: none; stroke-dashoffset: 0; }
}
</style>