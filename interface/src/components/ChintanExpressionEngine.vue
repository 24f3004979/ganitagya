<template>
  <div class="min-h-screen bg-white font-mono dark:bg-slate-950">

    <main class="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8 py-12 sm:py-16">

      <section>
        <h1 class="text-3xl sm:text-4xl font-bold tracking-tight text-slate-900 dark:text-slate-100">
          Chintan
        </h1>
        <p class="mt-2 text-sm sm:text-base text-slate-500 dark:text-slate-400">
          Type an expression. Watch it fold down, one operation at a time, into a single answer.
        </p>

        <form @submit.prevent="solve" class="mt-6 flex flex-col sm:flex-row gap-3">
          <input
            v-model="input"
            @keydown.enter.prevent="solve"
            type="text"
            placeholder="2*2+2*2"
            aria-label="Arithmetic expression"
            class="flex-1 rounded-lg border border-slate-200 bg-white px-4 py-3 text-lg tracking-wide text-slate-900 outline-none focus:ring-2 focus:ring-sky-500 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
          />
          <button
            type="submit"
            class="rounded-lg bg-sky-600 px-6 py-3 font-semibold text-white transition-transform hover:bg-sky-700 active:scale-95"
          >
            Break it down
          </button>
        </form>

        <p v-if="error" class="mt-3 text-sm text-red-600 dark:text-red-400">{{ error }}</p>
        <p v-else class="mt-3 text-xs text-slate-500 dark:text-slate-400">
          Digits and + − × ÷ only, no brackets yet — Chintan resolves ×/÷ first, then +/−, left to right.
        </p>
      </section>

      <!-- Token strip (display only — the engine itself works on the raw string) -->
      <section v-if="tokensShown.length" class="mt-10 flex flex-wrap items-center gap-2">
        <span
          v-for="(t, i) in tokensShown"
          :key="'tok-' + i"
          class="token"
          :class="isOperator(t) ? 'token-op' : 'token-num'"
        >{{ t }}</span>
      </section>

      <!-- Resolution steps, in components_dictionary insertion order -->
      <section v-if="visibleSteps.length" class="mt-8 space-y-3">
        <TransitionGroup name="step">
          <div
            v-for="s in visibleSteps"
            :key="s.name"
            class="rounded-xl border border-slate-200 bg-white px-4 py-3 flex items-center justify-between gap-3 dark:border-slate-800 dark:bg-slate-900"
          >
            <div class="flex items-center gap-2 text-sm sm:text-base flex-wrap">
              <span class="token token-num">{{ s.left }}</span>
              <span class="token token-op">{{ s.op }}</span>
              <span class="token token-num">{{ s.right }}</span>
              <span class="text-slate-400">→</span>
              <span class="token token-comp settle">{{ s.name }}</span>
            </div>
            <span class="text-xs sm:text-sm text-slate-500 dark:text-slate-400 shrink-0">{{ s.expr }}</span>
          </div>
        </TransitionGroup>
      </section>

      <!-- Final answer (evaluated client-side — parse() itself only decomposes) -->
      <section
        v-if="showAnswer"
        class="mt-10 rounded-2xl border border-emerald-300 bg-white p-6 sm:p-8 pop-answer dark:border-emerald-700 dark:bg-slate-900"
      >
        <p class="text-xs uppercase tracking-wide text-slate-500 dark:text-slate-400">
          Final expression: {{ result.expression }}
        </p>
        <p class="mt-2 text-4xl sm:text-5xl font-bold text-emerald-600 dark:text-emerald-400">
          {{ formattedAnswer }}
        </p>
        <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">from {{ input }}</p>
      </section>

      <!-- components_dictionary -->
      <section v-if="result && showAnswer" class="mt-8">
        <button
          @click="showDict = !showDict"
          class="text-sm font-semibold flex items-center gap-1 text-sky-600 hover:text-sky-700"
        >
          {{ showDict ? 'Hide' : 'Show' }} components_dictionary
          <svg
            class="h-4 w-4 transition-transform"
            :class="showDict ? 'rotate-90' : 'rotate-0'"
            fill="none" viewBox="0 0 24 24" stroke="currentColor"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </button>
        <div v-show="showDict" class="mt-3 rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm overflow-x-auto dark:border-slate-800 dark:bg-slate-900">
          <pre class="text-slate-800 dark:text-slate-200">{{ dictPretty }}</pre>
        </div>
      </section>

      <section v-if="result && animationDone" class="mt-6">
        <button @click="replay" class="text-sm font-medium text-slate-500 hover:text-slate-700 dark:hover:text-slate-300">
          ↺ Replay the breakdown
        </button>
      </section>

      <section id="how" class="mt-20 pt-8 border-t border-slate-200 dark:border-slate-800 text-sm text-slate-500 dark:text-slate-400">
        <p>
          Chintan resolves multiplication and division first, left to right, then addition and subtraction —
          same order you learned in school, just no brackets yet. Each pair it resolves becomes a
          <span class="text-amber-600 dark:text-amber-400 font-semibold">component</span>, and later steps
          can reference earlier ones, until only one component is left.
        </p>
      </section>

    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'
import { ExpressionEngine } from '../../../chintan/src/Arithmatic.ts'

interface Step {
  name: string
  left: string
  op: string
  right: string
  expr: string
}

interface ChintanResult {
  components_dictionary: Record<string, string>
  component_list: string[]
  expression: string
  steps: Step[]
  tokens: string[]
}

const isMobileMenuOpen = ref(false)
const input = ref('2*2+2*2')
const error = ref('')
const result = ref<ChintanResult | null>(null)
const visibleSteps = ref<Step[]>([])
const showDict = ref(false)
const animationDone = ref(false)
let animRunId = 0

const OPERAND = String.raw`[A-Za-z_]\w*|\d+(?:\.\d+)?`
const STEP_RE = new RegExp(`^(${OPERAND})([+\\-*/])(${OPERAND})$`)

// Front-end guard so the engine only ever sees a shape it was built for —
// digits and + - * / only, proper number/operator alternation, no brackets.
function validateAndClean(raw: string): string {
  const cleaned = raw.replace(/\s+/g, '')
  if (!cleaned) throw new Error('Enter an expression first.')
  if (/[()[\]{}]/.test(cleaned)) throw new Error("Brackets aren't supported yet — plain left-to-right expressions only.")
  const pattern = /^\d+(?:\.\d+)?([+\-*/]\d+(?:\.\d+)?)*$/
  if (!pattern.test(cleaned)) throw new Error('Only digits and + - * / are allowed, alternating between numbers and operators.')
  return cleaned
}

function tokenizeForDisplay(cleaned: string): string[] {
  return cleaned.match(/(\d+\.?\d*)|([+\-*/])/g) || []
}

// components_dictionary preserves insertion order for string keys, so this
// walks it in exactly the order parse() built it, reconstructing left/op/right
// from each value (which is just left+op+right concatenated by the engine).
function buildSteps(dict: Record<string, string>): Step[] {
  return Object.entries(dict).map(([name, expr]) => {
    const m = expr.match(STEP_RE)
    if (!m) return { name, left: '', op: '', right: '', expr }
    return { name, left: m[1], op: m[2], right: m[3], expr }
  })
}

function isOperator(t: string) {
  return /[+\-*/]/.test(t)
}

// parse() only decomposes — it never computes a numeric value, so this
// walks the dictionary itself to get an answer for display.
function evaluateComponent(name: string, dict: Record<string, string>, memo: Record<string, number>): number {
  if (memo[name] !== undefined) return memo[name]
  if (/^\d+\.?\d*$/.test(name)) return parseFloat(name)
  const expr = dict[name]
  const m = expr.match(STEP_RE)
  if (!m) throw new Error(`Couldn't evaluate ${name}.`)
  const l = evaluateComponent(m[1], dict, memo)
  const r = evaluateComponent(m[3], dict, memo)
  let v: number
  switch (m[2]) {
    case '+': v = l + r; break
    case '-': v = l - r; break
    case '*': v = l * r; break
    case '/': v = l / r; break
    default: throw new Error(`Unknown operator ${m[2]}`)
  }
  memo[name] = v
  return v
}

const tokensShown = computed(() => (result.value ? result.value.tokens : []))
const showAnswer = computed(() => animationDone.value && !!result.value)

const formattedAnswer = computed(() => {
  if (!result.value) return ''
  const memo: Record<string, number> = {}
  const finalName = result.value.expression
  const val = /^component_\d+$/.test(finalName)
    ? evaluateComponent(finalName, result.value.components_dictionary, memo)
    : parseFloat(finalName)
  if (!isFinite(val)) return 'undefined (divide by zero)'
  return Number.isInteger(val) ? val.toString() : val.toFixed(4).replace(/0+$/, '').replace(/\.$/, '')
})

const dictPretty = computed(() => {
  if (!result.value) return ''
  const lines = Object.entries(result.value.components_dictionary).map(([k, v]) => `  ${k}: '${v}'`)
  return `{\n${lines.join(',\n')}\n}`
})

async function animate(steps: Step[], myRun: number) {
  visibleSteps.value = []
  showDict.value = false
  animationDone.value = false
  await nextTick()
  for (const step of steps) {
    if (myRun !== animRunId) return
    await new Promise((r) => setTimeout(r, 550))
    if (myRun !== animRunId) return
    visibleSteps.value = [...visibleSteps.value, step]
  }
  if (myRun !== animRunId) return
  await new Promise((r) => setTimeout(r, 400))
  if (myRun !== animRunId) return
  animationDone.value = true
}

function solve() {
  error.value = ''
  animRunId++
  const myRun = animRunId
  try {
    const cleaned = validateAndClean(input.value)
    const engine = new ExpressionEngine(cleaned)
    const [components_dictionary, component_list, expression] = engine.parse()
    const steps = buildSteps(components_dictionary)
    const r: ChintanResult = {
      components_dictionary,
      component_list,
      expression,
      steps,
      tokens: tokenizeForDisplay(cleaned)
    }
    result.value = r
    animate(steps, myRun)
  } catch (e) {
    result.value = null
    visibleSteps.value = []
    animationDone.value = false
    error.value = e instanceof Error ? e.message : 'Something went wrong parsing that.'
  }
}

function replay() {
  if (!result.value) return
  animRunId++
  animate(result.value.steps, animRunId)
}

solve()
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
  font-size: .95rem;
}
.token-num { @apply bg-slate-100 text-slate-900 dark:bg-slate-800 dark:text-slate-100; }
.token-op  { @apply bg-sky-50 text-sky-600 font-bold dark:bg-sky-950 dark:text-sky-400; }
.token-comp { @apply bg-amber-50 text-amber-600 font-bold dark:bg-amber-950 dark:text-amber-400; }

.settle { animation: settle .5s ease .05s both; }
@keyframes settle {
  0% { transform: scale(1); }
  35% { transform: scale(1.08); }
  100% { transform: scale(1); }
}

.pop-answer { animation: popAnswer .5s cubic-bezier(.22,1,.36,1) both; }
@keyframes popAnswer {
  from { opacity: 0; transform: scale(.8) translateY(6px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}

.step-enter-active { transition: all .45s cubic-bezier(.22,1,.36,1); }
.step-enter-from { opacity: 0; transform: translateY(10px) scale(.96); }

@media (prefers-reduced-motion: reduce) {
  .token, .settle, .pop-answer, .step-enter-active { animation: none !important; transition: none !important; }
}
</style>
