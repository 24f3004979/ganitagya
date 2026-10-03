<script setup>
import { RouterLink } from 'vue-router'

const components = [
  {
    name: 'Siddhi',
    role: 'Adaptive quiz generator',
    text: 'Builds quizzes from ready-made templates and adjusts the questions to how you answer.',
  },
  {
    name: 'Chintan',
    role: 'Numerical and visual dissection tool',
    text: 'Break numbers apart and see how they work, so you can think with numbers instead of memorising them.',
  },
  {
    name: 'Mool',
    role: 'Root graph for topics',
    text: 'A simple graph for moving between topics. It is also the reference map of what you know and what to learn next.',
  },
]
</script>

<template>
  <div class="min-h-screen bg-white text-slate-900 antialiased">
    <!-- Header -->
    <header class="mx-auto flex max-w-5xl items-center justify-between px-6 py-6">
      <RouterLink to="/"
        class="text-lg font-semibold tracking-tight focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-slate-900">
        Ganitagya
      </RouterLink>
      <nav class="flex items-center gap-6 text-sm">
        <a href="#component" class="text-slate-600 hover:text-slate-900">Components</a>
        <RouterLink to="/auth"
          class="rounded-md border border-slate-300 px-4 py-2 font-medium hover:border-slate-900 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-900">
          Log in
        </RouterLink>
      </nav>
    </header>

    <main>
      <!-- Hero -->
      <section class="mx-auto max-w-5xl px-6 pb-24 pt-16 md:pt-24">
        <div>
          <h1 class="max-w-2xl text-4xl font-semibold leading-tight tracking-tight sm:text-5xl md:text-6xl">
            A platform to learn, discover and grow
          </h1>
          <p class="mt-6 max-w-md text-lg leading-relaxed text-slate-600">
            Ganitagya helps students build a real feel for numbers, one clear idea at a time.
          </p>
          <div class="mt-8 flex flex-wrap gap-3">
            <RouterLink to="/auth"
              class="rounded-md bg-slate-900 px-5 py-2.5 text-sm font-medium text-white hover:bg-slate-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-900">
              Create account
            </RouterLink>
            <a href="#components"
              class="rounded-md border border-slate-300 px-5 py-2.5 text-sm font-medium hover:border-slate-900 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-900">
              See how it works
            </a>
          </div>
        </div>
      </section>

      <!-- Problem -->
      <section class="border-t border-slate-200">
        <div class="mx-auto max-w-5xl px-6 py-20 md:grid md:grid-cols-2 md:gap-12">
          <h2 class="text-2xl font-semibold tracking-tight">Why math feels hard</h2>
          <p class="mt-4 max-w-md text-lg leading-relaxed text-slate-600 md:mt-0">
            Many students struggle with math. They never develop a feel for numbers, and abstract
            ideas end up resting on a weak foundation.
          </p>
        </div>
      </section>

      <!-- Components -->
      <section id="components" class="border-t border-slate-200">
        <div class="mx-auto max-w-5xl px-6 py-20">
          <h2 class="text-2xl font-semibold tracking-tight">What is inside</h2>

          <ul class="mt-10 divide-y divide-slate-200 border-y border-slate-200">
            <li v-for="item in components" :key="item.name" class="grid gap-2 py-8 md:grid-cols-[12rem_1fr] md:gap-12">
              <div>
                <h3 class="text-xl font-semibold">{{ item.name }}</h3>
                <p class="mt-1 text-sm text-slate-500">{{ item.role }}</p>
              </div>
              <p class="max-w-lg leading-relaxed text-slate-600">{{ item.text }}</p>
            </li>
          </ul>
        </div>
      </section>
    </main>

    <footer class="border-t border-slate-200">
      <div class="mx-auto max-w-5xl px-6 py-8 text-sm text-slate-500">
        Ganitagya. Learn, discover and grow.
      </div>
    </footer>
  </div>
</template>
