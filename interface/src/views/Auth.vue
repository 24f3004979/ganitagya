<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import LoginForm from '../components/LoginForm.vue'
import RegisterForm from '../components/RegisterForm.vue'

const route = useRoute()
const router = useRouter()

// The URL decides which form shows, so /login and /register both work
const isRegister = computed(() => route.path === '/register')
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-white p-4 text-slate-900 antialiased">
    <RegisterForm v-if="isRegister" @switch="router.push('/login')" />
    <LoginForm v-else @switch="router.push('/register')" />
  </div>
</template>
