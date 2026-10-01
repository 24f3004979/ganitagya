<script setup>
import { ref, onMounted } from 'vue'

// Swap these <a> tags for <RouterLink :to="..."> when the router is in.
const links = [
  { label: 'Home', href: '/' },
  { label: 'About', href: '/about' },
  { label: 'Help', href: '/help' },
]

const path = ref('/')
const menuOpen = ref(false)
const isDark = ref(true)

const applyTheme = () => document.documentElement.classList.toggle('dark', isDark.value)
const toggleTheme = () => {
  isDark.value = !isDark.value
  applyTheme()
  try { localStorage.setItem('ganitagya-theme', isDark.value ? 'dark' : 'light') } catch (e) {}
}

/* Magnetic "Get Started" button: leans toward the cursor */
const cta = ref(null)
const onCtaMove = (e) => {
  const r = cta.value.getBoundingClientRect()
  const x = (e.clientX - (r.left + r.width / 2)) * 0.25
  const y = (e.clientY - (r.top + r.height / 2)) * 0.35
  cta.value.style.transform = `translate(${x}px, ${y}px)`
}
const onCtaLeave = () => { cta.value.style.transform = '' }

onMounted(() => {
  path.value = window.location.pathname
  let saved = null
  try { saved = localStorage.getItem('ganitagya-theme') } catch (e) {}
  isDark.value = saved ? saved === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches
  applyTheme()
})
</script>

<template>
  <header
    class="sticky top-0 z-50 w-full border-b backdrop-blur-xl transition-colors duration-500
           border-slate-800 bg-black text-white"
  >
    <div class="mx-auto flex h-20 max-w-6xl items-center justify-between gap-4 px-6">

      <!-- Brand -->
      <a href="/" class="group flex items-center gap-2 select-none" aria-label="Ganitagya home">
        <span class="text-xl font-black tracking-widest bg-gradient-to-b bg-clip-text text-transparent
                     from-slate-900 to-slate-500 dark:from-white dark:to-slate-400">GANITAGYA</span>
      </a>

      <!-- Desktop nav -->
      <nav class="hidden md:block" aria-label="Main">
        <ul class="flex items-center gap-8">
          <li v-for="l in links" :key="l.href">
            <a
              :href="l.href"
              :aria-current="path === l.href ? 'page' : undefined"
              class="link relative py-1 text-sm font-semibold uppercase tracking-wider transition-colors duration-200
                     text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white"
              :class="path === l.href && 'text-slate-900 dark:text-white'"
            >
              {{ l.label }}
              <span class="absolute -bottom-0.5 left-0 h-0.5 w-full origin-left bg-indigo-500 transition-transform duration-300"
                    :class="path === l.href ? 'scale-x-100' : 'scale-x-0 link-line'"></span>
            </a>
          </li>
        </ul>
      </nav>

      <!-- Right side -->
      <div class="flex items-center gap-3">
        <a
          ref="cta"
          href="/login"
          @pointermove="onCtaMove"
          @pointerleave="onCtaLeave"
          class="hidden sm:inline-block rounded-full bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white shadow-md shadow-indigo-500/30
                 transition-[transform,background-color,box-shadow] duration-200 hover:bg-indigo-500 hover:shadow-lg hover:shadow-indigo-500/40
                 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-500"
        >Get Started</a>

        <!-- Mobile menu button -->
        <button
          @click="menuOpen = !menuOpen"
          :aria-expanded="menuOpen"
          aria-label="Toggle menu"
          class="grid h-10 w-10 place-items-center rounded-full border md:hidden
                 border-slate-300 bg-white dark:border-slate-700 dark:bg-slate-900"
        >
          <span class="relative block h-3.5 w-5">
            <span class="absolute left-0 h-0.5 w-5 bg-current transition-all duration-300" :class="menuOpen ? 'top-1.5 rotate-45' : 'top-0'"></span>
            <span class="absolute left-0 top-1.5 h-0.5 w-5 bg-current transition-opacity duration-200" :class="menuOpen && 'opacity-0'"></span>
            <span class="absolute left-0 h-0.5 w-5 bg-current transition-all duration-300" :class="menuOpen ? 'top-1.5 -rotate-45' : 'top-3'"></span>
          </span>
        </button>
      </div>
    </div>

    <!-- Mobile drawer -->
    <div
      class="grid overflow-hidden transition-[grid-template-rows] duration-500 md:hidden"
      :class="menuOpen ? 'grid-rows-[1fr]' : 'grid-rows-[0fr]'"
    >
      <ul class="min-h-0 space-y-1 px-6 pb-4">
        <li v-for="l in links" :key="l.href">
          <a :href="l.href" class="block rounded-lg px-3 py-3 text-sm font-semibold uppercase tracking-wider
                                   hover:bg-slate-100 dark:hover:bg-slate-900">{{ l.label }}</a>
        </li>
        <li>
          <a href="/start" class="mt-2 block rounded-full bg-indigo-600 px-4 py-3 text-center text-sm font-semibold text-white">Get Started</a>
        </li>
      </ul>
    </div>
  </header>
</template>

<style scoped>
/* Underline grows from the left on hover */
.link:hover .link-line { transform: scaleX(1); }
</style>
