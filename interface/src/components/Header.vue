
<template>
  <header class="sticky top-0 z-50 border-b border-slate-200/80 bg-white/80 font-mono backdrop-blur-md">
    <div class="mx-auto flex max-w-7xl items-center justify-between p-4 sm:px-6 lg:px-8">
      
      <!-- Logo Section -->
      <div class="flex items-center gap-2">
        <div class="h-8 w-8 rounded-lg bg-sky-600 flex items-center justify-center text-white font-bold text-lg">
          G
        </div>
        <span class="text-xl font-bold tracking-tight text-slate-900">Ganit<span class="text-sky-600">agya</span></span>
      </div>

      <!-- Desktop Navigation Links -->
      <nav class="hidden md:flex items-center gap-8 text-sm font-medium text-slate-600">
        <a href="#" class="transition-colors hover:text-sky-600 text-slate-900 font-semibold border-b-2 border-sky-600 pb-1">Home</a>
        <a href="#" class="transition-colors hover:text-sky-600 pb-1">Features</a>
        <a href="#" class="transition-colors hover:text-sky-600 pb-1">About</a>
        <a href="#" class="transition-colors hover:text-sky-600 pb-1">Pricing</a>
      </nav>

      <!-- Action Buttons -->
      <div class="hidden md:flex items-center gap-4">
        <button class="text-sm font-medium text-slate-600 transition-scale text-black hover:font-bold">
          Sign In
        </button>
        <button class="rounded-lg bg-slate-900 px-4 py-2 text-sm font-semibold text-white shadow-xs transition-all hover:bg-slate-800 hover:shadow-md active:scale-98">
          Get Started
        </button>
      </div>

      <!-- Mobile Hamburger Button -->
      <div class="md:hidden">
        <button 
          @click="isMobileMenuOpen = !isMobileMenuOpen"
          class="rounded-md p-2 text-slate-600 hover:bg-slate-100 focus:outline-none"
          aria-label="Toggle Menu"
        >
          <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path v-if="!isMobileMenuOpen" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Mobile Menu Slide Down -->
    <div 
      v-show="isMobileMenuOpen" 
      class="border-t border-slate-100 bg-white p-4 md:hidden shadow-lg transition-all"
    >
      <nav class="flex flex-col gap-4 text-sm font-medium text-slate-600">
        <a href="#" class="rounded-md px-3 py-2 text-slate-900 bg-slate-50 font-semibold">Home</a>
        <a href="#" class="rounded-md px-3 py-2 hover:bg-slate-50 hover:text-slate-900">Features</a>
        <a href="#" class="rounded-md px-3 py-2 hover:bg-slate-50 hover:text-slate-900">Docs</a>
        <a href="#" class="rounded-md px-3 py-2 hover:bg-slate-50 hover:text-slate-900">Pricing</a>
        <hr class="border-slate-100 my-1">
        <button class="w-full rounded-md border border-slate-200 px-3 py-2 text-center text-sm font-medium text-slate-700 hover:bg-slate-50">
          Sign In
        </button>
        <button class="w-full rounded-md bg-slate-900 px-3 py-2 text-center text-sm font-semibold text-white hover:bg-slate-800">
          Get Started
        </button>
      </nav>
    </div>
  </header>
</template>

<script setup>
import { ref } from 'vue'

const isMobileMenuOpen = ref(false)
</script>
