<template>
  <div class="min-h-screen bg-white font-mono dark:bg-slate-950">
    <main class="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8 py-12 sm:py-16">
      <header class="flex items-start justify-between gap-4">
        <div>
          <h1 class="text-3xl sm:text-4xl font-bold tracking-tight text-slate-900 dark:text-slate-100">Quiz</h1>
          <p class="mt-2 text-sm sm:text-base text-slate-500 dark:text-slate-400">
            Solve each set. Get most right and the next set gets harder; miss most and the topic steps back.
          </p>
        </div>
        <button type="button" class="text-sm font-medium text-slate-500 hover:text-slate-700 dark:hover:text-slate-300" @click="onLogout">
          Log out
        </button>
      </header>

      <p v-if="error" role="alert" class="mt-6 text-sm text-red-600 dark:text-red-400">{{ error }}</p>

      <!-- 1. Pick a topic -->
      <form v-if="phase === 'idle'" @submit.prevent="start" class="mt-8 flex flex-col sm:flex-row gap-3">
        <input
          v-model.trim="topic"
          type="text"
          placeholder="Topic, e.g. addition"
          aria-label="Quiz topic"
          class="flex-1 rounded-lg border border-slate-200 bg-white px-4 py-3 text-lg text-slate-900 outline-none focus:ring-2 focus:ring-sky-500 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
        />
        <button
          type="submit"
          :disabled="loading || !topic"
          class="rounded-lg bg-sky-600 px-6 py-3 font-semibold text-white transition-transform hover:bg-sky-700 active:scale-95 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {{ loading ? 'Starting…' : 'Start quiz' }}
        </button>
      </form>

      <!-- 2. Answer the current set -->
      <form v-else-if="phase === 'active'" @submit.prevent="submit" class="mt-8">
        <p class="text-sm text-slate-500 dark:text-slate-400">
          Set {{ setNumber }} · topic: <span class="font-semibold text-slate-700 dark:text-slate-300">{{ topic }}</span>
        </p>

        <ol class="mt-4 space-y-3">
          <li
            v-for="(q, i) in questions"
            :key="setNumber + '-' + i"
            class="flex flex-wrap items-center gap-3 rounded-xl border border-slate-200 bg-white px-4 py-3 dark:border-slate-800 dark:bg-slate-900"
          >
            <span class="token token-num">{{ q }}</span>
            <span class="text-slate-400">=</span>
            <input
              v-model="answers[i]"
              type="text"
              inputmode="numeric"
              :aria-label="'Answer for ' + q"
              placeholder="?"
              class="w-28 rounded-lg border border-slate-200 bg-white px-3 py-2 text-lg text-slate-900 outline-none focus:ring-2 focus:ring-sky-500 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100"
            />
          </li>
        </ol>

        <div class="mt-5 flex flex-wrap items-center gap-3">
          <button
            type="submit"
            :disabled="loading"
            class="rounded-lg bg-sky-600 px-6 py-3 font-semibold text-white transition-transform hover:bg-sky-700 active:scale-95 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {{ loading ? 'Checking…' : 'Submit answers' }}
          </button>
          <button type="button" class="text-sm font-medium text-slate-500 hover:text-slate-700 dark:hover:text-slate-300" @click="abandon">
            Quit quiz
          </button>
        </div>
      </form>

      <!-- 3. Report -->
      <section v-else class="mt-8 rounded-2xl border border-emerald-300 bg-white p-6 sm:p-8 dark:border-emerald-700 dark:bg-slate-900">
        <h2 class="text-2xl font-bold text-emerald-600 dark:text-emerald-400">Quiz complete</h2>

        <div class="mt-4 grid gap-4 sm:grid-cols-2">
          <div>
            <p class="text-sm font-semibold text-slate-700 dark:text-slate-300">Strong topics</p>
            <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">
              {{ report.strong.length ? report.strong.join(', ') : 'None yet. Keep practicing.' }}
            </p>
          </div>
          <div>
            <p class="text-sm font-semibold text-slate-700 dark:text-slate-300">Needs work</p>
            <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">
              {{ report.weak.length ? report.weak.join(', ') : 'Nothing flagged.' }}
            </p>
          </div>
        </div>

        <button
          type="button"
          class="mt-6 rounded-lg bg-sky-600 px-6 py-3 font-semibold text-white transition-transform hover:bg-sky-700 active:scale-95"
          @click="reset"
        >
          Start another quiz
        </button>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { request, ENDPOINTS } from '../api/client'
import { useAuth } from '../composables/useAuth'

const router = useRouter()
const { state, logout } = useAuth()

const phase = ref<'idle' | 'active' | 'done'>('idle')
const topic = ref('')
const questions = ref<string[]>([])
const answers = ref<string[]>([])
const setNumber = ref(0)
const loading = ref(false)
const error = ref('')
const report = reactive<{ strong: string[]; weak: string[] }>({ strong: [], weak: [] })

function loadSet(qs: string[]) {
  questions.value = qs
  answers.value = qs.map(() => '')
  setNumber.value += 1
}

// Every call goes through here so errors land in one banner and the button always unlocks.
async function run(fn: () => Promise<void>) {
  error.value = ''
  loading.value = true
  try {
    await fn()
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Something went wrong.'
  } finally {
    loading.value = false
  }
}

const sid = () => {
  if (state.studentId === null) throw new Error('Your student profile is missing. Log in again.')
  return state.studentId
}

function start() {
  return run(async () => {
    const res = await request(ENDPOINTS.quizStart, { method: 'POST', body: { student_id: sid(), topic: topic.value } })
    setNumber.value = 0
    loadSet(res.questions)
    phase.value = 'active'
  })
}

function submit() {
  // The backend expects whole numbers, one per question, in order.
  const parsed = answers.value.map((a) => (a.trim() === '' ? NaN : Number(a)))
  if (parsed.some((n) => !Number.isInteger(n))) {
    error.value = 'Answer every question with a whole number.'
    return
  }
  return run(async () => {
    const res = await request(ENDPOINTS.quizAnswer, { method: 'POST', body: { student_id: sid(), answers: parsed } })
    if (res.status === 'complete') {
      report.strong = res.report['strong topics'] ?? []
      report.weak = res.report['weak topics'] ?? []
      phase.value = 'done'
    } else {
      loadSet(res.questions)
    }
  })
}

function abandon() {
  return run(async () => {
    await request(ENDPOINTS.quizAbandon(sid()), { method: 'DELETE' })
    reset()
  })
}

function reset() {
  phase.value = 'idle'
  questions.value = []
  answers.value = []
  error.value = ''
}

function onLogout() {
  logout()
  router.push('/login')
}
</script>

<style scoped>
@reference "tailwindcss";
.token {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 2.25rem;
  padding: .4rem .65rem;
  border-radius: .5rem;
  font-weight: 600;
  font-size: 1.05rem;
}
.token-num { @apply bg-slate-100 text-slate-900 dark:bg-slate-800 dark:text-slate-100; }
</style>
