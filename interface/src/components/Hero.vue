<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount } from 'vue'

/* ---------- Theme (light / dark) ---------- */
const isDark = ref(true)
const applyTheme = () => document.documentElement.classList.toggle('dark', isDark.value)
const toggleTheme = () => {
  isDark.value = !isDark.value
  applyTheme()
  try { localStorage.setItem('ganitagya-theme', isDark.value ? 'dark' : 'light') } catch (e) {}
}

/* ---------- Cards (full class strings so Tailwind can detect them) ---------- */
const cards = [
  {
    name: 'Siddhi', tag: '01 // ENGINE',
    text: 'A smart quiz engine built to understand you and adapt perfectly to your unique learning style.',
    title: 'text-indigo-600 dark:text-indigo-400',
    badge: 'border-indigo-500/30 text-indigo-600 dark:text-indigo-400 bg-indigo-500/5',
    hover: 'hover:border-indigo-500/60', glow: 'bg-indigo-500/20', bar: 'bg-indigo-500',
  },
  {
    name: 'Chintan', tag: '02 // SPACE',
    text: 'A dedicated, distraction-free space engineered for deep thought, continuous exploration, and advanced data visualization.',
    title: 'text-emerald-600 dark:text-emerald-400',
    badge: 'border-emerald-500/30 text-emerald-600 dark:text-emerald-400 bg-emerald-500/5',
    hover: 'hover:border-emerald-500/60', glow: 'bg-emerald-500/20', bar: 'bg-emerald-500',
  },
  {
    name: 'Mool', tag: '03 // GRAPH',
    text: 'Your personal knowledge graph that organically grows, beautifully connects, and scales seamlessly alongside your mind.',
    title: 'text-amber-600 dark:text-amber-400',
    badge: 'border-amber-500/30 text-amber-600 dark:text-amber-400 bg-amber-500/5',
    hover: 'hover:border-amber-500/60', glow: 'bg-amber-500/20', bar: 'bg-amber-500',
  },
]

/* ---------- Deck state ---------- */
const order = ref([0, 1, 2])           // order[0] is the front card
const tilt = reactive({ x: 0, y: 0 })  // 3D tilt for front card
const drag = reactive({ active: false, startX: 0, startY: 0, dx: 0, dy: 0 })
const deckEl = ref(null)

const next = () => order.value.push(order.value.shift())
const prev = () => order.value.unshift(order.value.pop())
const bringToFront = (i) => { while (order.value[0] !== i) next() }

const cardStyle = (i) => {
  const p = order.value.indexOf(i)
  if (p === 0) {
    if (drag.active) {
      return { transform: `translate3d(${drag.dx}px, ${drag.dy}px, 0) rotate(${drag.dx / 14}deg)`, zIndex: 30, transition: 'none' }
    }
    return { transform: `rotateX(${tilt.x}deg) rotateY(${tilt.y}deg)`, zIndex: 30 }
  }
  return {
    transform: `translate3d(${p * 22}px, ${-p * 18}px, ${-p * 60}px) rotate(${p * 5}deg) scale(${1 - p * 0.05})`,
    zIndex: 30 - p * 10,
    opacity: 1 - p * 0.12,
  }
}

const onPointerDown = (e, i) => {
  if (order.value[0] !== i) return bringToFront(i)
  drag.active = true
  drag.startX = e.clientX; drag.startY = e.clientY; drag.dx = 0; drag.dy = 0
  e.currentTarget.setPointerCapture(e.pointerId)
}
const onPointerMove = (e) => {
  if (drag.active) {
    drag.dx = e.clientX - drag.startX
    drag.dy = (e.clientY - drag.startY) * 0.4
    return
  }
  const r = deckEl.value.getBoundingClientRect()
  tilt.y = ((e.clientX - r.left) / r.width - 0.5) * 14
  tilt.x = -((e.clientY - r.top) / r.height - 0.5) * 14
}
const onPointerUp = () => {
  if (!drag.active) return
  const moved = Math.abs(drag.dx)
  drag.active = false
  if (moved > 70 || moved < 4) next()   // fling or tap sends it to the back
}
const resetTilt = () => { tilt.x = 0; tilt.y = 0 }

/* ---------- Kinetic title: letters dodge the cursor ---------- */
const word = 'GANITAGYA'.split('')
const letterEls = ref([])
const letterState = word.map(() => ({ x: 0, y: 0, r: 0 }))
const mouse = reactive({ x: -9999, y: -9999 })
const glow = reactive({ x: 0, y: 0 })
const glowEl = ref(null)
let raf = 0

const onMouse = (e) => { mouse.x = e.clientX; mouse.y = e.clientY }

const loop = () => {
  glow.x += (mouse.x - glow.x) * 0.08
  glow.y += (mouse.y - glow.y) * 0.08
  if (glowEl.value) glowEl.value.style.transform = `translate(${glow.x}px, ${glow.y}px)`

  letterEls.value.forEach((el, i) => {
    if (!el) return
    const b = el.getBoundingClientRect()
    const dx = b.left + b.width / 2 - mouse.x
    const dy = b.top + b.height / 2 - mouse.y
    const d = Math.hypot(dx, dy) || 1
    const f = Math.max(0, 1 - d / 180)
    const s = letterState[i]
    s.x += ((dx / d) * f * 34 - s.x) * 0.14
    s.y += ((dy / d) * f * 34 - s.y) * 0.14
    s.r += ((dx / d) * f * 14 - s.r) * 0.14
    el.style.transform = `translate(${s.x.toFixed(1)}px, ${s.y.toFixed(1)}px) rotate(${s.r.toFixed(1)}deg)`
  })
  raf = requestAnimationFrame(loop)
}

/* ---------- Keyboard ---------- */
const onKey = (e) => {
  if (e.key === 'ArrowRight' || e.key === 'ArrowDown') { e.preventDefault(); next() }
  if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') { e.preventDefault(); prev() }
}

const reduceMotion = typeof matchMedia !== 'undefined' && matchMedia('(prefers-reduced-motion: reduce)').matches

onMounted(() => {
  let saved = null
  try { saved = localStorage.getItem('ganitagya-theme') } catch (e) {}
  isDark.value = saved ? saved === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches
  applyTheme()
  if (!reduceMotion) {
    window.addEventListener('pointermove', onMouse)
    raf = requestAnimationFrame(loop)
  }
})
onBeforeUnmount(() => {
  window.removeEventListener('pointermove', onMouse)
  cancelAnimationFrame(raf)
})
</script>

<template>
  <div class="relative min-h-screen w-full flex flex-col items-center justify-center overflow-hidden font-sans py-20 px-4
              bg-slate-100 text-slate-900 dark:bg-black dark:text-white transition-colors duration-500">

    <!-- Cursor-following glow -->
    <div class="pointer-events-none fixed left-0 top-0 z-0 -ml-[280px] -mt-[280px]">
      <div ref="glowEl" class="w-[560px] h-[560px] rounded-full bg-indigo-500/20 dark:bg-indigo-500/10 blur-[120px] will-change-transform"></div>
    </div>
    <div class="relative z-10 w-full max-w-4xl flex flex-col items-center gap-16">

      <!-- Header with kinetic letters -->
      <div class="text-center space-y-4">
        <h1 class="text-5xl sm:text-7xl font-black tracking-widest select-none" aria-label="Ganitagya">
          <span
            v-for="(ch, i) in word"
            :key="i"
            :ref="(el) => (letterEls[i] = el)"
            aria-hidden="true"
            class="letter inline-block will-change-transform bg-gradient-to-b bg-clip-text text-transparent
                   from-slate-900 via-slate-700 to-slate-400 dark:from-white dark:via-slate-200 dark:to-slate-500"
            :style="{ animationDelay: i * 60 + 'ms' }"
          >{{ ch }}</span>
        </h1>
        <h2 class="text-lg font-medium text-slate-500 dark:text-slate-400 tracking-wider uppercase">
          Featuring <span class="text-indigo-600 dark:text-indigo-400 font-semibold">3 Core Components</span>
        </h2>
      </div>

      <!-- Interactive deck -->
      <div
        ref="deckEl"
        tabindex="0"
        aria-label="Ganitagya components. Use arrow keys to browse."
        @keydown="onKey"
        @pointermove="onPointerMove"
        @pointerleave="resetTilt"
        class="relative w-full max-w-md h-[340px] sm:h-[300px] outline-none touch-pan-y [perspective:1100px]
               focus-visible:ring-2 focus-visible:ring-indigo-500/60 rounded-2xl"
      >
        <article
          v-for="(c, i) in cards"
          :key="c.name"
          @pointerdown="onPointerDown($event, i)"
          @pointerup="onPointerUp"
          @pointercancel="onPointerUp"
          :style="cardStyle(i)"
          :class="[c.hover, drag.active && order[0] === i ? 'cursor-grabbing' : 'cursor-grab']"
          class="group absolute inset-0 p-8 rounded-2xl border overflow-hidden select-none origin-bottom
                 border-slate-200 bg-white/95 shadow-xl shadow-slate-300/50
                 dark:border-slate-800 dark:bg-slate-950/95 dark:shadow-black/60
                 backdrop-blur-xl transition-[transform,opacity,background-color,border-color] duration-500 ease-[cubic-bezier(.2,1.2,.35,1)]"
        >
          <!-- Progress bar shows which card is in front -->
          <div class="absolute left-0 top-0 h-1 transition-all duration-700" :class="[c.bar, order[0] === i ? 'w-full' : 'w-0']"></div>

          <div class="flex items-center justify-between mb-4">
            <div class="font-bold text-2xl tracking-wide" :class="c.title">{{ c.name }}</div>
            <div class="text-xs font-mono px-2 py-0.5 rounded border" :class="c.badge">{{ c.tag }}</div>
          </div>
          <p class="text-slate-600 dark:text-slate-400 text-base leading-relaxed transition-colors group-hover:text-slate-900 dark:group-hover:text-slate-200">
            {{ c.text }}
          </p>

          <div class="absolute -bottom-8 -right-8 w-36 h-36 rounded-full blur-xl transition-transform duration-700 group-hover:scale-150" :class="c.glow"></div>
        </article>
      </div>

      <!-- Controls -->
      <div class="flex items-center gap-4 -mt-8">
        <button @click="prev"
                class="rounded-full border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 px-5 py-2 text-sm font-semibold
                       transition hover:-translate-y-0.5 focus-visible:outline focus-visible:outline-2 focus-visible:outline-indigo-500">Back</button>
        <div class="flex gap-2">
          <button
            v-for="(c, i) in cards" :key="c.name" @click="bringToFront(i)" :aria-label="'Show ' + c.name"
            class="h-2.5 rounded-full transition-all duration-500"
            :class="order[0] === i ? 'w-7 bg-slate-900 dark:bg-white' : 'w-2.5 bg-slate-300 dark:bg-slate-700'"></button>
        </div>
        <button @click="next"
                class="rounded-full border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 px-5 py-2 text-sm font-semibold
                       transition hover:-translate-y-0.5 focus-visible:outline focus-visible:outline-2 focus-visible:outline-indigo-500">Next</button>
      </div>
      <p class="-mt-10 text-sm text-slate-500 dark:text-slate-500">Drag, tap, or use arrow keys to shuffle the deck.</p>
    </div>
  </div>
</template>

<style scoped>
/* One-time entrance for the title letters */
.letter { animation: rise 0.9s cubic-bezier(0.2, 1.3, 0.4, 1) both; }
@keyframes rise { from { transform: translateY(60%) rotate(8deg); opacity: 0; } }

@media (prefers-reduced-motion: reduce) {
  .letter { animation: none; }
}
</style>
