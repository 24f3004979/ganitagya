<script setup>
import { ref } from 'vue';
import RegisterForm from '../components/RegisterForm.vue';
import LoginForm from '../components/LoginForm.vue';

const mode = ref('register'); // 'register' | 'login'
</script>

<template>
  <div class="flex min-h-screen flex-col items-center justify-center gap-2 bg-black p-4">
    <!-- Tabs -->
    <div class="flex gap-1 rounded-md bg-white p-1 shadow-md">
      <button type="button" @click="mode = 'register'" :class="[
        'rounded-md px-4 py-2 text-sm font-medium',
        mode === 'register' ? 'bg-green-700 text-white' : 'text-gray-700 hover:bg-gray-100',
      ]">
        Register
      </button>
      <button type="button" @click="mode = 'login'" :class="[
        'rounded-md px-4 py-2 text-sm font-medium',
        mode === 'login' ? 'bg-green-700 text-white' : 'text-gray-700 hover:bg-gray-100',
      ]">
        Log in
      </button>
    </div>

    <RegisterForm v-if="mode === 'register'" />
    <LoginForm v-else />
  </div>
</template>
