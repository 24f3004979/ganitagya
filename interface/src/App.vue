<script setup lang="ts">
import {ref, onMounted} from 'vue'

const message = ref('loading ...')
const error = ref(null)

onMounted(async() => {
  try{
    const res = await fetch("/api/v1/ping")
    if (!res.ok) throw new Error(`HTTP Error Raised with status ${res.status}`)
    const data = await res.json()
    message.value = `Message from Backend System : ${data["message"]}`
  }catch (e) {
    error.value = e.message
  }
}
)

</script>

<template>
  <div>
    <h1> Ganitagya Scafholding structured </h1>
    <p v-if="error" > Error : {{ error }} </p>
    <p v-else> {{ message }} </p>
    </div>
</template>
