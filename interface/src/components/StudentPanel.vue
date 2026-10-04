<script setup>
import { ref, onMounted } from 'vue';
import { api } from '../api/client.ts';
import QuizPanel from './QuizPanel.vue';

// Dashboard response:
//   { current_topics: [{ topic_id, name, level }], unlocked_topics: [{ topic_id, name }] }

const MAX_LEVEL = 3; // keep in sync with MAX_LEVEL in vidhyarthi.py

const current = ref([]);
const unlocked = ref([]);
const loading = ref(true);
const error = ref('');
const activeTopic = ref(null);

async function loadDashboard() {
  loading.value = true;
  error.value = '';
  try {
    const res = await api.get('/api/v1/student/dashboard');
    current.value = res.current_topics;
    unlocked.value = res.unlocked_topics;
  } catch (e) {
    error.value = e.message;
  } finally {
    loading.value = false;
  }
}

function openQuiz(topic) {
  activeTopic.value = { topic_id: topic.topic_id, name: topic.name };
}

// Levels and unlocked topics may have changed after a quiz, so reload.
function closeQuiz() {
  activeTopic.value = null;
  loadDashboard();
}

onMounted(loadDashboard);

// TODO: quick access buttons for siddhi and chintan pages
</script>

<template>
  <QuizPanel v-if="activeTopic" :topic="activeTopic" @close="closeQuiz" />

  <section v-else class="dashboard">
    <h1>Your learning dashboard</h1>

    <p v-if="loading" class="muted">Loading your topics…</p>

    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <button class="btn-secondary" @click="loadDashboard">Try again</button>
    </div>

    <template v-else>
      <h2>Practice your topics</h2>
      <div v-if="current.length" class="grid">
        <button
          v-for="t in current"
          :key="t.topic_id"
          class="topic-card"
          @click="openQuiz(t)"
        >
          <span class="topic-name">{{ t.name }}</span>
          <span class="pips" :aria-label="`Level ${t.level} of ${MAX_LEVEL}`">
            <span
              v-for="n in MAX_LEVEL"
              :key="n"
              class="pip"
              :class="{ filled: n <= t.level }"
            ></span>
          </span>
          <span class="cta">Take a test →</span>
        </button>
      </div>
      <p v-else class="muted">
        Nothing in progress yet. Start with one of the unlocked topics below.
      </p>

      <h2>Unlocked next</h2>
      <div v-if="unlocked.length" class="grid">
        <button
          v-for="t in unlocked"
          :key="t.topic_id"
          class="topic-card new"
          @click="openQuiz(t)"
        >
          <span class="topic-name">{{ t.name }}</span>
          <span class="badge">New</span>
          <span class="cta">Start →</span>
        </button>
      </div>
      <p v-else class="muted">
        No new topics to unlock right now. Keep practising to open more.
      </p>
    </template>
  </section>
</template>

<style scoped>
.dashboard { max-width: 900px; margin: 0 auto; padding: 1rem; }
h1 { margin-bottom: 1.5rem; }
h2 { margin: 1.75rem 0 0.75rem; font-size: 1.15rem; }
.muted { opacity: 0.7; }
.error { color: #c0392b; background: #c0392b14; padding: 0.8rem 1rem; border-radius: 8px; }

.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 0.9rem; }

.topic-card {
  display: flex; flex-direction: column; align-items: flex-start; gap: 0.6rem;
  padding: 1rem; text-align: left; cursor: pointer; color: inherit; font: inherit;
  background: transparent; border: 1px solid #8885; border-radius: 12px;
  transition: transform 0.15s, border-color 0.15s;
}
.topic-card:hover { transform: translateY(-2px); border-color: #3b82f6; }
.topic-card.new { border-style: dashed; }
.topic-name { font-weight: 600; font-size: 1.05rem; }
.cta { margin-top: auto; color: #3b82f6; font-size: 0.9rem; }

.pips { display: flex; gap: 4px; }
.pip { width: 22px; height: 6px; border-radius: 3px; background: #8884; }
.pip.filled { background: #3b82f6; }

.badge { font-size: 0.7rem; padding: 2px 8px; border-radius: 999px; background: #22c55e22; color: #16a34a; }

.btn-secondary { padding: 0.45rem 0.9rem; border-radius: 8px; border: 1px solid #8886; background: transparent; color: inherit; cursor: pointer; }
</style>