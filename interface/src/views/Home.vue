<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const topic = ref('');

// Sends the student to the quiz page with the chosen starting topic.
// Adjust the route name/path to match your router.
const startQuiz = () => {
  router.push({ path: '/quiz', query: { topic: topic.value.trim() } });
};

const steps = [
  { title: 'Pick a topic', text: 'Tell Ganitagya where you want to start.' },
  { title: 'Answer questions', text: 'Each answer decides which question comes next.' },
  { title: 'See your report', text: 'Get a list of your strong and weak topics.' },
];
</script>

<template>
  <div class="min-h-screen bg-gray-100">
    <!-- Top bar -->
    <header class="bg-white shadow-md">
      <nav class="mx-auto flex max-w-4xl items-center justify-between px-4 py-3">
        <RouterLink to="/" class="text-xl font-semibold text-gray-800">Ganitagya</RouterLink>
        <div class="flex items-center gap-2">
          <RouterLink to="/auth" class="rounded-md px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100">
            Log in
          </RouterLink>
          <RouterLink to="/auth"
            class="rounded-md bg-green-700 px-4 py-2 text-sm font-medium text-white hover:bg-green-800">
            Create account
          </RouterLink>
        </div>
      </nav>
    </header>

    <main class="mx-auto max-w-4xl space-y-6 p-4">
      <!-- Hero: the main action is starting a quiz -->
      <section class="rounded-md bg-white p-6 shadow-md">
        <h1 class="text-3xl font-semibold text-gray-800">Find out what you know</h1>
        <p class="mt-2 max-w-prose text-gray-600">
          Take a quiz that adapts to your answers, then see which topics you are strong
          in and which ones need more practice.
        </p>

        <form @submit.prevent="startQuiz" class="mt-6 flex flex-col gap-3 sm:flex-row">
          <div class="flex-1">
            <label for="topic" class="mb-1 block text-sm font-medium text-gray-700">
              Starting topic
            </label>
            <input id="topic" v-model="topic" type="text" required placeholder="For example: Algebra"
              class="w-full rounded-md border border-gray-300 px-3 py-2 text-xl focus:border-green-600 focus:outline-none focus:ring-1 focus:ring-green-600" />
          </div>
          <button type="submit"
            class="rounded-md bg-green-700 px-6 py-2 font-medium text-white hover:bg-green-800 sm:self-end">
            Start quiz
          </button>
        </form>
        <p class="mt-3 text-sm text-gray-500">You need to log in before the quiz begins.</p>
      </section>

      <!-- How it works: a real sequence, so numbering is meaningful -->
      <section class="rounded-md bg-white p-6 shadow-md">
        <h2 class="text-xl font-semibold text-gray-800">How it works</h2>
        <ol class="mt-4 grid gap-4 sm:grid-cols-3">
          <li v-for="(step, i) in steps" :key="step.title" class="rounded-md border border-gray-200 p-4">
            <span class="text-sm font-medium text-green-700">Step {{ i + 1 }}</span>
            <h3 class="mt-1 font-medium text-gray-800">{{ step.title }}</h3>
            <p class="mt-1 text-sm text-gray-600">{{ step.text }}</p>
          </li>
        </ol>
      </section>

    </main>

    <footer class="py-6 text-center text-sm text-gray-500">Ganitagya</footer>
  </div>
</template>
