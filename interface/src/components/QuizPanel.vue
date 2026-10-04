<script setup>
import { ref, computed, onMounted } from 'vue';
import { api } from '../api/client.ts';

const props = defineProps({
  // { topic_id: Number, name: String }
  topic: { type: Object, required: true },
});
const emit = defineEmits(['close']);

const BASE = '/api/v1/siddhi/quiz';

// Response shapes (from the backend)
//   start : { topic, questions: [str], progress: { generated, total } }
//   next  : { completed, previous_result: [0|1], questions?, progress?, report? }
//   end   : { completed, report: { strong_topics: [str], weak_topics: [str] } }

const loading = ref(true);
const error = ref('');
const questions = ref([]);
const answers = ref([]); // NOTE: <input type="number"> + v-model gives numbers (or ''), not strings
const progress = ref({ generated: 0, total: 0 });
const lastResult = ref([]);
const finished = ref(false);
const endedEarly = ref(false);
const report = ref(null);

const isActive = computed(() => questions.value.length > 0 && !finished.value);

function isWholeNumber(value) {
  if (value === null || value === undefined) return false;
  if (String(value).trim() === '') return false;
  return Number.isInteger(Number(value));
}

const canSubmit = computed(
  () => isActive.value && !loading.value && answers.value.every(isWholeNumber)
);

const firstNumber = computed(() => progress.value.generated - questions.value.length + 1);
const percent = computed(() =>
  progress.value.total
    ? Math.round(((firstNumber.value - 1) / progress.value.total) * 100)
    : 0
);
const lastCorrect = computed(() => lastResult.value.reduce((a, b) => a + b, 0));

function loadBatch(qs, p) {
  questions.value = qs;
  answers.value = qs.map(() => '');
  progress.value = p;
}

async function start() {
  loading.value = true;
  error.value = '';
  try {
    const res = await api.post(`${BASE}/start`, { topic_id: props.topic.topic_id });
    loadBatch(res.questions, res.progress);
  } catch (e) {
    error.value = e.message;
  } finally {
    loading.value = false;
  }
}

async function submit() {
  if (!canSubmit.value) return;
  loading.value = true;
  error.value = '';
  try {
    const res = await api.post(`${BASE}/next`, {
      answers: answers.value.map((a) => Number(a)),
    });
    lastResult.value = res.previous_result;

    if (res.completed) {
      report.value = res.report ?? null;
      questions.value = [];
      finished.value = true;
    } else {
      loadBatch(res.questions ?? [], res.progress ?? progress.value);
    }
  } catch (e) {
    // for a 400 (wrong answer count) the quiz stays active on the server, inputs are kept
    error.value = e.message;
  } finally {
    loading.value = false;
  }
}

async function endQuiz() {
  loading.value = true;
  error.value = '';
  try {
    const res = await api.post(`${BASE}/end`);
    report.value = res.report;
    questions.value = [];
    endedEarly.value = true;
    finished.value = true;
  } catch (e) {
    error.value = e.message;
  } finally {
    loading.value = false;
  }
}

// Leaving mid-quiz tells the server to drop it; errors don't block leaving.
async function leave() {
  if (isActive.value) {
    try {
      await api.post(`${BASE}/end`);
    } catch {
      /* ignore */
    }
  }
  emit('close');
}

onMounted(start);
</script>

<template>
  <section class="quiz">
    <header class="quiz-head">
      <button class="btn-link" @click="leave">← Back to dashboard</button>
      <h2>{{ topic.name }}</h2>
    </header>

    <p v-if="error" class="error">{{ error }}</p>

    <!-- loading first batch -->
    <p v-if="loading && !isActive && !finished" class="muted">Preparing your questions…</p>

    <!-- active quiz -->
    <div v-else-if="isActive" class="card">
      <div class="progress">
        <div class="progress-bar" :style="{ width: percent + '%' }"></div>
      </div>
      <p class="muted">
        Questions {{ firstNumber }}–{{ progress.generated }} of {{ progress.total }}
      </p>

      <p v-if="lastResult.length" class="feedback">
        Last round: {{ lastCorrect }} / {{ lastResult.length }} correct
      </p>

      <ol class="questions" :key="progress.generated">
        <li v-for="(q, i) in questions" :key="i">
          <code class="expr">{{ q }}</code>
          <span class="eq">=</span>
          <input
            v-model="answers[i]"
            type="number"
            step="1"
            inputmode="numeric"
            placeholder="?"
            :disabled="loading"
            @keyup.enter="submit"
          />
        </li>
      </ol>

      <div class="actions">
        <button class="btn" :disabled="!canSubmit" @click="submit">
          {{ loading ? 'Checking…' : 'Submit answers' }}
        </button>
        <button class="btn-secondary" :disabled="loading" @click="endQuiz">End quiz</button>
      </div>
      <p class="hint">Answers must be whole numbers.</p>
    </div>

    <!-- report -->
    <div v-else-if="finished" class="card">
      <h3>{{ endedEarly ? 'Quiz ended' : 'Quiz complete' }}</h3>
      <p v-if="lastResult.length && !endedEarly" class="feedback">
        Last round: {{ lastCorrect }} / {{ lastResult.length }} correct
      </p>

      <div v-if="report" class="report">
        <div>
          <h4>Strong topics</h4>
          <ul v-if="report.strong_topics.length">
            <li v-for="t in report.strong_topics" :key="t">{{ t }}</li>
          </ul>
          <p v-else class="muted">None yet</p>
        </div>
        <div>
          <h4>Needs practice</h4>
          <ul v-if="report.weak_topics.length">
            <li v-for="t in report.weak_topics" :key="t">{{ t }}</li>
          </ul>
          <p v-else class="muted">None</p>
        </div>
      </div>

      <button class="btn" @click="emit('close')">Back to dashboard</button>
    </div>
  </section>
</template>

<style scoped>
.quiz { max-width: 640px; margin: 0 auto; padding: 1rem; }
.quiz-head { display: flex; flex-direction: column; gap: 0.25rem; margin-bottom: 1rem; }
.quiz-head h2 { margin: 0; }
.card { border: 1px solid #8884; border-radius: 12px; padding: 1.25rem; }
.muted { opacity: 0.7; font-size: 0.9rem; }
.hint { opacity: 0.6; font-size: 0.8rem; margin: 0.75rem 0 0; }
.error { color: #c0392b; background: #c0392b14; padding: 0.6rem 0.8rem; border-radius: 8px; }
.feedback { font-weight: 600; margin: 0.5rem 0; }

.progress { height: 6px; background: #8883; border-radius: 3px; overflow: hidden; margin-bottom: 0.5rem; }
.progress-bar { height: 100%; background: #3b82f6; transition: width 0.3s; }

.questions { list-style: none; padding: 0; margin: 1rem 0; display: flex; flex-direction: column; gap: 0.75rem; }
.questions li { display: flex; align-items: center; gap: 0.6rem; }
.expr { font-size: 1.1rem; flex: 1; overflow-x: auto; white-space: nowrap; }
.eq { opacity: 0.6; }
.questions input { width: 110px; padding: 0.4rem 0.6rem; border: 1px solid #8886; border-radius: 8px; font-size: 1rem; background: transparent; color: inherit; }

.actions { display: flex; gap: 0.75rem; flex-wrap: wrap; }
.btn, .btn-secondary { padding: 0.55rem 1rem; border-radius: 8px; font-size: 0.95rem; cursor: pointer; border: 1px solid transparent; }
.btn { background: #3b82f6; color: white; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-secondary { background: transparent; border-color: #8886; color: inherit; }
.btn-link { background: none; border: none; padding: 0; color: #3b82f6; cursor: pointer; text-align: left; font-size: 0.9rem; }

.report { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin: 1rem 0; }
.report h4 { margin: 0 0 0.4rem; }
.report ul { margin: 0; padding-left: 1.1rem; }
</style>