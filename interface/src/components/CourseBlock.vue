<script setup>
import { onMounted, ref } from 'vue';
import { api } from '../api/client.ts'

const graph = ref(null);

onMounted(async () => {
  try {
    const response = await api.get("/api/v1/student/graph");
    graph.value = response;
    console.log(response);
  } catch (err) {
    console.error(err);
  }
});
</script>

<template>
  Student graph information : {{  graph  }}
</template>