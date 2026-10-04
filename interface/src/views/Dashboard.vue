<script setup>
import Navigation from '../components/Navigation.vue';
import StudentPanel from '../components/StudentPanel.vue';
import CourseBlock from '../components/CourseBlock.vue';

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
    <CourseBlock/>
    <StudentPanel/>
  </div>
</template>
