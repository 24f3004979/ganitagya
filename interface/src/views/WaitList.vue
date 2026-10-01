<script setup>
import WaitlistForm from '../components/WaitlistForm.vue';
</script>

<template>
  <div class="h-screen w-screen flex flex-col items-center justify-center gap-6 py-12 bg-black text-white">
    <h1 class="text-4xl font-bold tracking-wide text-slate-900 dark:text-white">Welcome to Ganitagya</h1>
    <p class="max-w-md text-center text-lg text-slate-600 dark:text-slate-400">
      Ganitagya is a platform for learning and practicing mathematics. Join the waitlist to be notified when we launch.
    </p>
    <WaitlistForm @joined="onJoined" />
  </div>

</template>