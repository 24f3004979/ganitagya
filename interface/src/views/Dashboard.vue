<script setup>
import Navigation from '../components/Navigation.vue';
import StudentPanel from '../components/StudentPanel.vue';
import StudenttGraph from '../components/StudentGraph.vue';

import { ref } from 'vue';

const userInfo = ref({ name: '' })
// Emit handle

const handleUserFetched = (userData) => {
  userInfo.value = userData
}

</script>

<template>
  <div class='h-screen w-screen'>
    <Navigation />
    <div class="h-full flex justify-center items-center">
      <StudentPanel/>
    </div>
  </div>
</template>
