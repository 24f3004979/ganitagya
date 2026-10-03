<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { api } from '../api/client.ts';

const router = useRouter();
const user = ref('');
const fall = ref('');

onMounted(async () => {
  try {
    // TODO: Back end needs to protect its routes and also have unified request handler for token verification
    user.value = await api.get<string>('/api/v1/me');
  } catch (error) {
    fall.value = "Something went wrong";
    router.push('/auth');
  }
})
</script>

<template>
  <div v-if="fall">
    {{ fall }}
  </div>
  <div v-if="user">
    Hello {{ user }} , What we are going to learn today ?
  </div>
</template>
