<script setup>
const toTop = () => {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches
  window.scrollTo({ top: 0, behavior: reduce ? 'auto' : 'smooth' })
}
</script>

<template>
  <footer
    class="w-full border-t transition-colors duration-500
           border-slate-200 bg-white/80 text-slate-600
           dark:border-slate-800 dark:bg-black dark:text-slate-400"
  >
    <div class="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 px-6 py-8 text-sm sm:flex-row">

      <p>© 2026 Madhav Rimal. All Rights Reserved</p>

      <div class="flex items-center gap-5">
        <a
          href="mailto:madhavprapanna@gmail.com"
          class="group relative font-medium text-slate-900 dark:text-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-indigo-500"
        >
          Contact: madhavprapanna@gmail.com
          <span class="absolute -bottom-0.5 left-0 h-0.5 w-full origin-left scale-x-0 bg-indigo-500 transition-transform duration-300 group-hover:scale-x-100"></span>
        </a>

        <button
          @click="toTop"
          aria-label="Back to top"
          class="group grid h-9 w-9 place-items-center rounded-full border transition-all duration-300
                 border-slate-300 bg-white hover:-translate-y-1 hover:border-indigo-500
                 dark:border-slate-700 dark:bg-slate-900
                 focus-visible:outline focus-visible:outline-2 focus-visible:outline-indigo-500"
        >
          <svg class="h-4 w-4 transition-transform duration-300 group-hover:-translate-y-0.5" viewBox="0 0 24 24" fill="none"
               stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 19V5M5 12l7-7 7 7" />
          </svg>
        </button>
      </div>

    </div>
  </footer>
</template>
