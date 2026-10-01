<script setup>
import { ref, computed } from 'vue'
import LoginForm from '../components/LoginForm.vue'
import RegisterForm from '../components/RegisterForm.vue'

// With the router, pass this from the route: /login -> 'login', /register -> 'register'
const props = defineProps({
  initialMode: { type: String, default: 'login', validator: (v) => ['login', 'register'].includes(v) },
})

const mode = ref(props.initialMode)
const direction = ref(1) // 1 = slide left, -1 = slide right
const loading = ref(false)
const error = ref('')

const isLogin = computed(() => mode.value === 'login')

const setMode = (m) => {
  if (m === mode.value) return
  direction.value = m === 'register' ? 1 : -1
  error.value = ''
  mode.value = m
}

/* ---------- Back end wiring ---------- */
async function handleLogin({ email, password, remember }) {
  loading.value = true
  error.value = ''
  try {
    // TODO: const res = await api.post('/auth/login', { email, password, remember })
    // TODO: store session/token, then router.push('/')
    console.log('login payload', { email, remember })
  } catch (e) {
    error.value = e?.message || 'Could not log in. Check your details and try again.'
  } finally {
    loading.value = false
  }
}

async function handleRegister({ name, email, password }) {
  loading.value = true
  error.value = ''
  try {
    // TODO: await api.post('/auth/register', { name, email, password })
    // TODO: then either log the user in or switch to the login form: setMode('login')
    console.log('register payload', { name, email })
  } catch (e) {
    error.value = e?.message || 'Could not create your account. Try again.'
  } finally {
    loading.value = false
  }
}

const handleForgot = () => {
  // TODO: router.push('/forgot-password')
}

/* Decorative deck behind the card; it fans out as you switch modes */
const layers = computed(() => [
  { color: 'bg-indigo-500/25 dark:bg-indigo-500/20', t: isLogin.value ? 'translate(18px,-14px) rotate(3deg)' : 'translate(-26px,-22px) rotate(-5deg)' },
  { color: 'bg-emerald-500/25 dark:bg-emerald-500/20', t: isLogin.value ? 'translate(36px,-28px) rotate(6deg)' : 'translate(18px,-14px) rotate(3deg)' },
  { color: 'bg-amber-500/25 dark:bg-amber-500/20', t: isLogin.value ? 'translate(54px,-42px) rotate(9deg)' : 'translate(36px,-28px) rotate(6deg)' },
])
</script>

<template>
  <section class="h-screen w-screen relative flex flex-1 items-center justify-center overflow-hidden px-4 py-16
                  bg-slate-100 text-slate-900 transition-colors duration-500 dark:bg-black dark:text-white">

    <!-- Ambient glow shifts color with the mode -->
    <div class="pointer-events-none absolute left-1/2 top-1/2 h-[520px] w-[520px] -translate-x-1/2 -translate-y-1/2 rounded-full blur-[120px] transition-colors duration-700"
         :class="isLogin ? 'bg-indigo-500/20 dark:bg-indigo-500/10' : 'bg-emerald-500/20 dark:bg-emerald-500/10'"></div>

    <div class="relative w-full max-w-md">

      <!-- Auth card -->
      <div class="relative z-10 overflow-hidden rounded-2xl border border-slate-200 bg-white/95 p-8 shadow-2xl shadow-slate-300/50 backdrop-blur-xl
                  transition-colors duration-500 dark:border-slate-800 dark:bg-slate-950/95 dark:shadow-black/60">

        <!-- Accent bar -->
        <div class="absolute left-0 top-0 h-1 w-full transition-colors duration-500" :class="isLogin ? 'bg-indigo-500' : 'bg-emerald-500'"></div>

        <!-- Tab switch with sliding pill -->
        <div role="tablist" aria-label="Authentication"
             class="relative mb-8 grid grid-cols-2 rounded-xl bg-slate-100 p-1 dark:bg-slate-900">
          <span class="absolute inset-y-1 left-1 w-[calc(50%-4px)] rounded-lg bg-white shadow transition-transform duration-500 ease-[cubic-bezier(.2,1.2,.35,1)] dark:bg-slate-800"
                :class="isLogin ? 'translate-x-0' : 'translate-x-full'"></span>
          <button role="tab" :aria-selected="isLogin" @click="setMode('login')"
                  class="relative z-10 rounded-lg py-2 text-sm font-semibold transition-colors"
                  :class="isLogin ? 'text-indigo-600 dark:text-indigo-400' : 'text-slate-500'">Log in</button>
          <button role="tab" :aria-selected="!isLogin" @click="setMode('register')"
                  class="relative z-10 rounded-lg py-2 text-sm font-semibold transition-colors"
                  :class="!isLogin ? 'text-emerald-600 dark:text-emerald-400' : 'text-slate-500'">Sign up</button>
        </div>

        <div class="mb-6">
          <h1 class="text-2xl font-bold tracking-wide">{{ isLogin ? 'Welcome back' : 'Create your account' }}</h1>
          <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">
            {{ isLogin ? 'Log in to pick up where you left off.' : 'Start learning with Siddhi, Chintan and Mool.' }}
          </p>
        </div>

        <!-- Forms slide past each other -->
        <Transition :name="direction > 0 ? 'slide-left' : 'slide-right'" mode="out-in">
          <LoginForm v-if="isLogin" key="login" :loading="loading" :error="error"
                     @submit="handleLogin" @forgot="handleForgot" @switch="setMode('register')" />
          <RegisterForm v-else key="register" :loading="loading" :error="error"
                        @submit="handleRegister" @switch="setMode('login')" />
        </Transition>
      </div>
    </div>
  </section>
</template>

<style scoped>
.slide-left-enter-active, .slide-left-leave-active,
.slide-right-enter-active, .slide-right-leave-active { transition: opacity 0.25s ease, transform 0.25s ease; }
.slide-left-enter-from  { opacity: 0; transform: translateX(32px); }
.slide-left-leave-to    { opacity: 0; transform: translateX(-32px); }
.slide-right-enter-from { opacity: 0; transform: translateX(-32px); }
.slide-right-leave-to   { opacity: 0; transform: translateX(32px); }

@media (prefers-reduced-motion: reduce) {
  .slide-left-enter-active, .slide-left-leave-active,
  .slide-right-enter-active, .slide-right-leave-active { transition: none; }
}
</style>
