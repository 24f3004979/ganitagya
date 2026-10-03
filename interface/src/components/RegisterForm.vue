<script setup>
import { ref } from 'vue';

const form = ref({ email: '', password: '' });
const repass = ref('');
const error = ref('');
const success = ref('');

const Register = async () => {
  error.value = '';
  success.value = '';

  if (repass.value !== form.value.password) {
    error.value = 'Passwords do not match.';
    repass.value = ''; // clear only the confirm field
    return;
  }

  try {
    const response = await fetch('http://localhost:8000/api/v1/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form.value),
    });

    const data = await response.json();

    if (response.ok) {
      success.value = data.message;
      form.value = { email: '', password: '' };
      repass.value = '';
    } else {
      // FastAPI: 'detail' is a string for HTTPException, an array for 422 validation errors
      error.value =
        typeof data.detail === 'string'
          ? data.detail
          : 'Please check your input and try again.';
    }
  } catch (e) {
    console.error('Registration request failed:', e);
    error.value = 'Could not reach the server. Please try again.';
  }
};
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-transparent p-4">
    <form @submit.prevent="Register" class="w-full max-w-sm space-y-4 rounded-md bg-white p-6 shadow-md">
      Register
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
        <label for="email" class="mb-1 block text-sm font-medium text-gray-700">Email</label>
        <input type="email" id="email" v-model="form.email" required
          class="w-full rounded-md border border-gray-300 px-3 py-2 text-xl focus:border-green-600 focus:outline-none focus:ring-1 focus:ring-green-600" />
      </div>

      <div>
        <label for="password" class="mb-1 block text-sm font-medium text-gray-700">Password</label>
        <input type="password" id="password" v-model="form.password" required
          class="w-full rounded-md border border-gray-300 px-3 py-2 text-xl focus:border-green-600 focus:outline-none focus:ring-1 focus:ring-green-600" />
      </div>

      <div>
        <label for="repassword" class="mb-1 block text-sm font-medium text-gray-700">Confirm password</label>
        <input type="password" id="repassword" v-model="repass" required
          class="w-full rounded-md border border-gray-300 px-3 py-2 text-xl focus:border-green-600 focus:outline-none focus:ring-1 focus:ring-green-600" />
      </div>

      <button type="submit" class="w-full rounded-md bg-green-700 py-2 font-medium text-white hover:bg-green-800">
        Submit
      </button>
    </form>
  </div>
</template>
