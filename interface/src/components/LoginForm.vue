<script setup>
import { ref } from 'vue' // reactive variables

// Required variables
const form = ref({ username: '', password: '' });
const error = ref('');
const success = ref('');

const Login = async () => {
  error.value = '';
  success.value = '';

  try {
    const response = await fetch(
      'http://localhost:8000/api/v1/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form.value)
    }
    );
    const data = await response.json();

    if (response.ok) {
      success.value = data.message;
      localStorage.setItem("access_token", data.token) // Token stored into local storage

      // routing to dashboard
      window.location.href = "http://localhost:5173/dashboard";

      form.value = { username: '', password: '' };
    } else {
      error.value =
        typeof data.detail === 'string'
          ? data.detail
          : 'Please check your input annd try again';
    }
  } catch (e) {
    console.error('Login request failed', e);
    error.value = "Could not reach the server, please try again later";
  }
};
</script>


<template>
  <div class="flex min-h-screen items-center justify-center bg-transparent p-4">
    <form @submit.prevent="Login" class="w-full max-w-sm space-y-4 rounded-md bg-white p-6 shadow-md">

      Welcome Back

      <!-- Error message -->
      <div v-if="error" role="alert" class="rounded-md border border-red-300 bg-red-50 px-3 py-2 text-sm text-red-800">
        {{ error }}
      </div>

      <!-- Success message -->
      <div v-if="success" role="status"
        class="rounded-md border border-green-300 bg-green-50 px-3 py-2 text-sm text-green-800">
        {{ success }}
      </div>

      <div>
        <label for="username" class="mb-1 block text-sm font-medium text-gray-700">Email</label>
        <input type="username" id="username" v-model="form.username" required
          class="w-full rounded-md border border-gray-300 px-3 py-2 text-xl focus:border-green-600 focus:outline-none focus:ring-1 focus:ring-green-600" />
      </div>

      <div>
        <label for="password" class="mb-1 block text-sm font-medium text-gray-700">Password</label>
        <input type="password" id="password" v-model="form.password" required
          class="w-full rounded-md border border-gray-300 px-3 py-2 text-xl focus:border-green-600 focus:outline-none focus:ring-1 focus:ring-green-600" />
      </div>

      <button type="submit" class="w-full rounded-md bg-green-700 py-2 font-medium text-white hover:bg-green-800">
        Submit
      </button>
    </form>
  </div>
</template>
