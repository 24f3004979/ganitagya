<script setup>
import Navigation from '../components/Navigation.vue';
import { ref } from 'vue';

const userInfo = ref({ name: '' })
// Emit handle

const handleUserFetched = (userData) => {
  userInfo.value = userData
}

</script>

<template>
  <div>
    <Navigation />
  </div>
</template>
