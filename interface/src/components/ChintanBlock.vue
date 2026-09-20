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
            class="rounded-xl border border-slate-200 bg-white px-4 py-3 dark:border-slate-800 dark:bg-slate-900"
          >
            <div class="flex flex-wrap items-center justify-between gap-3">
              <div class="flex items-center gap-2 text-sm sm:text-base flex-wrap">
                <span class="token token-num">{{ s.left }}</span>
                <span class="token token-op">{{ s.op }}</span>
                <span class="token token-num">{{ s.right }}</span>
                <span class="text-slate-400">→</span>
                <span class="token token-comp settle">{{ s.name }}</span>
              </div>
              <div class="flex items-center gap-3 shrink-0">
                <span class="text-xs sm:text-sm text-slate-500 dark:text-slate-400">{{ s.expr }}</span>
                <button
                  type="button"
                  class="blocks-btn"
                  :class="{ 'blocks-btn-on': activeName === s.name }"
                  :aria-expanded="activeName === s.name"
                  :aria-controls="'blocks-' + s.name"
                  @click="toggleBlocks(s.name)"
                >
                  <svg class="h-3.5 w-3.5" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true">
                    <rect x="1.5" y="1.5" width="5.5" height="5.5" rx="1.2" />
                    <rect x="9" y="1.5" width="5.5" height="5.5" rx="1.2" />
                    <rect x="1.5" y="9" width="5.5" height="5.5" rx="1.2" />
                    <rect x="9" y="9" width="5.5" height="5.5" rx="1.2" />
                  </svg>
                  {{ activeName === s.name ? 'Hide blocks' : 'See blocks' }}
                </button>
              </div>
            </div>

            <!-- Block view for this one component -->
            <div
              v-if="activeName === s.name"
              :id="'blocks-' + s.name"
              class="mt-4 border-t border-slate-200 pt-4 dark:border-slate-800"
            >
              <!-- Out of scope -->
              <div
                v-if="sceneMessage"
                role="status"
                class="rounded-lg border border-amber-300 bg-amber-50 px-4 py-3 text-sm text-amber-800 dark:border-amber-700/60 dark:bg-amber-950/40 dark:text-amber-300"
              >
                <p class="font-semibold">Can't draw this step with blocks</p>
                <p class="mt-1">{{ sceneMessage }}</p>
                <p class="mt-1 text-xs opacity-80">Blocks work for whole numbers from 0 to {{ MAX_BLOCKS }}.</p>
              </div>

              <!-- Scene -->
              <template v-else-if="scene && frame">
                <div class="stage-box rounded-xl border border-slate-200 bg-slate-50 p-3 dark:border-slate-800 dark:bg-slate-950/60">
                  <div
                    class="stage"
                    role="img"
                    :aria-label="frame.title + '. ' + frame.caption"
                    :style="{ '--w': STAGE_W, '--h': scene.height }"
                  >
                    <TransitionGroup name="ghost" tag="div" class="absolute inset-0 pointer-events-none">
                      <span
                        v-for="g in ghostCells"
                        :key="g.key"
                        class="ghost"
                        :style="posStyle(g.x, g.y)"
                      />
                    </TransitionGroup>

                    <TransitionGroup name="lbl" tag="div" class="absolute inset-0 pointer-events-none">
                      <span
                        v-for="l in frame.labels"
                        :key="l.id + '|' + l.text"
                        class="stage-label"
                        :class="'lbl-' + l.tone"
                        :style="posStyle(l.x, l.y)"
                      >{{ l.text }}</span>
                    </TransitionGroup>

                    <div class="absolute inset-0 pointer-events-none" aria-hidden="true">
                      <span
                        v-for="(st, i) in frame.blocks"
                        :key="i"
                        class="blk"
                        :class="'blk-' + st.tone"
                        :style="blockStyle(st)"
                      />
                    </div>
                  </div>
                </div>

                <div class="mt-3 flex flex-wrap items-start justify-between gap-x-4 gap-y-3">
                  <div class="min-w-0 flex-1 basis-56" aria-live="polite">
                    <p class="text-sm font-bold text-slate-900 dark:text-slate-100">{{ frame.title }}</p>
                    <p class="mt-0.5 text-sm text-slate-500 dark:text-slate-400">{{ frame.caption }}</p>
                  </div>

                  <div class="flex items-center gap-2">
                    <button type="button" class="ctl-btn" :disabled="frameIdx === 0" @click="prev">← Back</button>
                    <button type="button" class="ctl-btn" :disabled="frameIdx >= scene.frames.length - 1" @click="next">Next →</button>
                    <button type="button" class="ctl-btn" @click="replayBlocks">↺ Replay</button>
                  </div>
                </div>

                <div v-if="scene.frames.length > 1" class="mt-3 flex items-center gap-1.5">
                  <button
                    v-for="(f, i) in scene.frames"
                    :key="i"
                    type="button"
                    class="step-dot"
                    :class="{ 'step-dot-on': i === frameIdx, 'step-dot-done': i < frameIdx }"
                    :aria-label="'Go to step ' + (i + 1) + ': ' + f.title"
                    :aria-current="i === frameIdx ? 'step' : undefined"
                    @click="goTo(i)"
                  />
                </div>
              </template>
            </div>
          </div>
        </TransitionGroup>
      </section>

      <!-- Final answer (evaluated client-side — parse() itself only decomposes) -->
      <section
        v-if="showAnswer"
        class="mt-10 rounded-2xl border border-emerald-300 bg-white p-6 sm:p-8 pop-answer dark:border-emerald-700 dark:bg-slate-900"
      >
        <p class="text-xs uppercase tracking-wide text-slate-500 dark:text-slate-400">
          Final expression: {{ result?.expression }}
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
        <p class="mt-3">
          Press <span class="font-semibold text-slate-700 dark:text-slate-300">See blocks</span> on any component to
          watch that single operation happen with blocks: adding piles them together, subtracting takes some away,
          multiplying repeats a group, and dividing cuts the pile into equal groups. The block view only handles
          whole numbers from 0 to {{ MAX_BLOCKS }}, and says so when a step goes beyond that.
        </p>
      </section>

    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, watch, onBeforeUnmount } from 'vue'
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
  activeName.value = null
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
    activeName.value = null
    animationDone.value = false
    error.value = e instanceof Error ? e.message : 'Something went wrong parsing that.'
  }
}

function replay() {
  if (!result.value) return
  animRunId++
  animate(result.value.steps, animRunId)
}

/* ─────────────────────────────────────────────────────────────────────────
   Block view — visualises ONE component (a op b) at a time.

   Every scene is a list of frames. All frames of a scene describe the same
   set of blocks (same ids, same order), only their position / tone / opacity
   change, so CSS transitions do all the animating: a block that "moves" is
   just the same element with a new target position in the next frame.
   Coordinates are in "cells" (one block plus its gap); CSS turns cells into
   pixels with a --u variable that follows the container width.
   ───────────────────────────────────────────────────────────────────────── */

type OpSymbol = '+' | '-' | '*' | '/'
type Tone = 'a' | 'b' | 'result' | 'remove'

interface BlockState { x: number; y: number; tone: Tone; opacity: number; scale: number; delay: number }
interface Board { id: string; x: number; y: number; cols: number; slots: number }
interface BlockLabel { id: string; x: number; y: number; text: string; tone: Tone | 'plain' }
interface Frame { title: string; caption: string; blocks: BlockState[]; boards: Board[]; labels: BlockLabel[] }
interface Scene { op: OpSymbol; a: number; b: number; result: number; frames: Frame[]; height: number }

const MAX_BLOCKS = 100
const COLS = 10                       // a full board is 10 wide, so 100 = a 10 × 10 grid
const GAP5 = 0.45                     // small extra gap after the 5th column, makes counting easier
const BOARD_W = COLS + GAP5
const BOARD_GAP = 1.5
const STAGE_W = BOARD_W * 2 + BOARD_GAP
const LABEL_H = 1.7                   // room above a board for its label

const GLYPH: Record<OpSymbol, string> = { '+': '+', '-': '−', '*': '×', '/': '÷' }

const range = (n: number) => Array.from({ length: n }, (_, i) => i)
const roundUp10 = (n: number) => Math.max(COLS, Math.ceil(n / COLS) * COLS)

function fmt(n: number): string {
  return Number.isInteger(n) ? String(n) : String(parseFloat(n.toFixed(4)))
}

/** Position of slot i on a board whose top-left corner is (ox, oy). */
function slot(i: number, ox: number, oy: number, cols = COLS) {
  const c = i % cols
  const r = Math.floor(i / cols)
  return { x: ox + c + (cols === COLS && c >= 5 ? GAP5 : 0), y: oy + r }
}

const shown = (p: { x: number; y: number }, tone: Tone, delay = 0, opacity = 1): BlockState =>
  ({ x: p.x, y: p.y, tone, opacity, scale: 1, delay })

const hiddenAt = (p: { x: number; y: number }, tone: Tone = 'a'): BlockState =>
  ({ x: p.x, y: p.y, tone, opacity: 0, scale: 0.4, delay: 0 })

const mkBoard = (id: string, x: number, y: number, slots: number, cols = COLS): Board =>
  ({ id, x, y, cols, slots })

const labelAbove = (id: string, x: number, y: number, text: string, tone: BlockLabel['tone'] = 'plain'): BlockLabel =>
  ({ id, x, y: y - 1.45, text, tone })

/** Small per-block delay so a group of blocks moves as a ripple, not all at once. */
const stagger = (index: number, count: number, span = 700) =>
  Math.round(index * Math.min(45, span / Math.max(count, 1)))

function sceneHeight(frames: Frame[]): number {
  let h = LABEL_H
  for (const f of frames) {
    for (const b of f.boards) h = Math.max(h, b.y + Math.ceil(b.slots / b.cols))
    for (const s of f.blocks) h = Math.max(h, s.y + 1)
  }
  return h + 0.4
}

/** Returns a plain-language reason if this step can't be drawn, otherwise null. */
function scopeProblem(a: number, b: number, op: OpSymbol): string | null {
  for (const n of [a, b]) {
    if (!Number.isFinite(n)) return "An earlier step couldn't be worked out (probably a divide by zero)."
    if (!Number.isInteger(n)) return `${fmt(n)} isn't a whole number, and blocks can only show whole numbers.`
    if (n < 0) return `${fmt(n)} is negative, and blocks can't go below zero.`
    if (n > MAX_BLOCKS) return `${fmt(n)} is more than ${MAX_BLOCKS}, and the block grid stops at ${MAX_BLOCKS}.`
  }
  switch (op) {
    case '+':
      if (a + b > MAX_BLOCKS) return `${a} + ${b} makes ${a + b}, which is past the ${MAX_BLOCKS}-block grid.`
      break
    case '-':
      if (b > a) return `${a} − ${b} would drop below zero, and a pile can't hold fewer than no blocks.`
      break
    case '*':
      if (a * b > MAX_BLOCKS) return `${a} × ${b} makes ${a * b}, which is past the ${MAX_BLOCKS}-block grid.`
      break
    case '/':
      if (b === 0) return "Blocks can't be split into 0 groups."
      if (a % b !== 0) return `${a} ÷ ${b} doesn't split evenly (it's ${fmt(a / b)}), and blocks can't be cut into pieces.`
      break
  }
  return null
}

/* ── Addition: two piles slide together into one bigger pile ── */
function buildAdd(a: number, b: number): Frame[] {
  const r = a + b
  const y0 = LABEL_H
  const xB = BOARD_W + BOARD_GAP
  const ids = range(r)

  const start = ids.map((i) => (i < a ? shown(slot(i, 0, y0), 'a') : shown(slot(i - a, xB, y0), 'b')))
  const joined = ids.map((i) =>
    i < a ? shown(slot(i, 0, y0), 'a') : shown(slot(i, 0, y0), 'b', stagger(i - a, b))
  )
  const total = ids.map((i) => shown(slot(i, 0, y0), 'result', Math.min(i * 8, 500)))

  return [
    {
      title: 'Two piles',
      caption: `${a} blocks on the left and ${b} on the right.`,
      blocks: start,
      boards: [mkBoard('A', 0, y0, roundUp10(a)), mkBoard('B', xB, y0, roundUp10(b))],
      labels: [labelAbove('A', 0, y0, String(a), 'a'), labelAbove('B', xB, y0, String(b), 'b')]
    },
    {
      title: 'Push them together',
      caption: `Slide the ${b} onto the end of the ${a}. Nothing is lost, the pile just gets bigger.`,
      blocks: joined,
      boards: [mkBoard('A', 0, y0, roundUp10(r))],
      labels: [labelAbove('A', 0, y0, `${a} + ${b}`)]
    },
    {
      title: 'Count the pile',
      caption: `${r} blocks in total, so ${a} + ${b} = ${r}.`,
      blocks: total,
      boards: [mkBoard('A', 0, y0, roundUp10(r))],
      labels: [labelAbove('A', 0, y0, String(r), 'result')]
    }
  ]
}

/* ── Subtraction: take some blocks out of the pile ── */
function buildSub(a: number, b: number): Frame[] {
  const r = a - b
  const y0 = LABEL_H
  const xT = BOARD_W + BOARD_GAP
  const ids = range(a)
  const kept = (i: number) => i < r

  const boardA = mkBoard('A', 0, y0, roundUp10(a))
  const boardT = mkBoard('T', xT, y0, roundUp10(b))

  const f0 = ids.map((i) => shown(slot(i, 0, y0), 'a'))
  const f1 = ids.map((i) => shown(slot(i, 0, y0), kept(i) ? 'a' : 'remove'))
  const f2 = ids.map((i) =>
    kept(i) ? shown(slot(i, 0, y0), 'a') : shown(slot(i - r, xT, y0), 'remove', stagger(i - r, b))
  )
  const f3 = ids.map((i) =>
    kept(i)
      ? shown(slot(i, 0, y0), 'result', Math.min(i * 8, 500))
      : shown(slot(i - r, xT, y0), 'remove', 0, 0.25)
  )

  return [
    {
      title: 'Start with the pile',
      caption: `${a} blocks.`,
      blocks: f0,
      boards: [boardA],
      labels: [labelAbove('A', 0, y0, String(a), 'a')]
    },
    {
      title: `Mark ${b} to take away`,
      caption: b === 0 ? 'Taking away 0 leaves the pile as it is.' : `The last ${b} blocks are the ones that go.`,
      blocks: f1,
      boards: [boardA],
      labels: [labelAbove('A', 0, y0, `${a} − ${b}`)]
    },
    {
      title: 'Take them away',
      caption: b === 0 ? 'Nothing moves.' : `The ${b} marked blocks leave the pile and wait on the right.`,
      blocks: f2,
      boards: b > 0 ? [boardA, boardT] : [boardA],
      labels: [
        labelAbove('A', 0, y0, String(r), 'a'),
        ...(b > 0 ? [labelAbove('T', xT, y0, `taken away: ${b}`, 'remove')] : [])
      ]
    },
    {
      title: 'What is left',
      caption: `${r} blocks are left in the pile, so ${a} − ${b} = ${r}.`,
      blocks: f3,
      boards: b > 0 ? [boardA, boardT] : [boardA],
      labels: [
        labelAbove('A', 0, y0, String(r), 'result'),
        ...(b > 0 ? [labelAbove('T', xT, y0, `taken away: ${b}`, 'remove')] : [])
      ]
    }
  ]
}

/* ── Multiplication: one group of b, repeated a times ── */
function buildMul(a: number, b: number): Frame[] {
  const r = a * b
  const y0 = LABEL_H

  if (r === 0) {
    return [
      {
        title: 'Nothing to stack',
        caption: a === 0
          ? `0 groups of ${b} is no blocks at all, so ${a} × ${b} = 0.`
          : `${a} groups of 0 is no blocks at all, so ${a} × ${b} = 0.`,
        blocks: [],
        boards: [mkBoard('M', 0, y0, COLS)],
        labels: [labelAbove('M', 0, y0, '0', 'result')]
      }
    ]
  }

  const ids = range(r)
  const group = (i: number) => Math.floor(i / b)
  const tone = (i: number): Tone => (group(i) % 2 === 0 ? 'a' : 'b')
  const step = a > 1 ? Math.min(260, Math.round(1300 / (a - 1))) : 0
  const board = mkBoard('M', 0, y0, roundUp10(r))

  const f0 = ids.map((i) =>
    group(i) === 0 ? shown(slot(i, 0, y0), 'a') : hiddenAt(slot(i % b, 0, y0), tone(i))
  )
  const f1 = ids.map((i) => shown(slot(i, 0, y0), tone(i), group(i) * step))
  const f2 = ids.map((i) => shown(slot(i, 0, y0), 'result', Math.min(i * 8, 500)))

  return [
    {
      title: `One group of ${b}`,
      caption: `${a} × ${b} means ${a} groups of ${b}. Here is a single group.`,
      blocks: f0,
      boards: [board],
      labels: [labelAbove('M', 0, y0, `1 group of ${b}`, 'a')]
    },
    {
      title: `Make ${a} groups`,
      caption: a === 1
        ? 'There is only one group, so there is nothing to copy.'
        : `Copy the group until there are ${a} of them. Alternating colors show where each group sits.`,
      blocks: f1,
      boards: [board],
      labels: [labelAbove('M', 0, y0, `${a} groups of ${b}`)]
    },
    {
      title: 'Count everything',
      caption: `${r} blocks in all, so ${a} × ${b} = ${r}. Multiplying is adding the same group again and again.`,
      blocks: f2,
      boards: [board],
      labels: [labelAbove('M', 0, y0, String(r), 'result')]
    }
  ]
}

/* ── Division: cut the pile into b equal groups ── */
function buildDiv(a: number, b: number): Frame[] {
  const y0 = LABEL_H

  if (a === 0) {
    return [
      {
        title: 'Nothing to split',
        caption: `${b} groups of 0 blocks: every group is empty, so 0 ÷ ${b} = 0.`,
        blocks: [],
        boards: [mkBoard('A', 0, y0, COLS)],
        labels: [labelAbove('A', 0, y0, '0', 'result')]
      }
    ]
  }

  const q = a / b                                       // blocks per group
  const ids = range(a)
  const group = (i: number) => Math.floor(i / q)
  const within = (i: number) => i % q
  const tone = (i: number): Tone => (group(i) % 2 === 0 ? 'a' : 'b')

  // How each finished group is laid out, and where the groups sit on the stage.
  const cc = q <= 5 ? q : q <= 20 ? 5 : COLS            // columns inside one group
  const cw = cc === COLS ? BOARD_W : cc                 // width of one group
  const ch = Math.ceil(q / cc)                          // height of one group
  const gap = q <= 2 ? 0.9 : 1.3
  const perRow = Math.max(1, Math.floor((STAGE_W + gap) / (cw + gap)))
  const usedCols = Math.min(b, perRow)
  const offX = (STAGE_W - (usedCols * (cw + gap) - gap)) / 2
  const origin = (g: number) => ({
    x: offX + (g % perRow) * (cw + gap),
    y: y0 + Math.floor(g / perRow) * (ch + gap)
  })
  const clusterBoards = range(b).map((g) => {
    const o = origin(g)
    return mkBoard('g' + g, o.x, o.y, q, cc)
  })
  const clusterPos = (i: number) => {
    const o = origin(group(i))
    return slot(within(i), o.x, o.y, cc)
  }
  const dealDelay = Math.min(90, Math.round(700 / b))

  const boardA = mkBoard('A', 0, y0, roundUp10(a))

  return [
    {
      title: `Start with ${a}`,
      caption: `All ${a} blocks in one pile.`,
      blocks: ids.map((i) => shown(slot(i, 0, y0), 'a')),
      boards: [boardA],
      labels: [labelAbove('A', 0, y0, String(a), 'a')]
    },
    {
      title: `Cut into ${b} equal groups`,
      caption: `Dividing by ${b} means ${b} groups that are all the same size, ${q} blocks each. The colors show where the cuts fall.`,
      blocks: ids.map((i) => shown(slot(i, 0, y0), tone(i))),
      boards: [boardA],
      labels: [labelAbove('A', 0, y0, `${a} ÷ ${b}`)]
    },
    {
      title: 'Pull the groups apart',
      caption: `${b} groups, ${q} block${q === 1 ? '' : 's'} in each.`,
      blocks: ids.map((i) => shown(clusterPos(i), tone(i), group(i) * dealDelay)),
      boards: clusterBoards,
      labels: [{ id: 'top', x: offX, y: 0.15, text: `${b} groups of ${q}`, tone: 'plain' }]
    },
    {
      title: 'One group is the answer',
      caption: `Each group holds ${q}, so ${a} ÷ ${b} = ${q}.`,
      blocks: ids.map((i) =>
        group(i) === 0 ? shown(clusterPos(i), 'result') : shown(clusterPos(i), tone(i), 0, 0.22)
      ),
      boards: clusterBoards,
      labels: [{ id: 'top', x: offX, y: 0.15, text: `each group holds ${q}`, tone: 'result' }]
    }
  ]
}

function buildScene(op: OpSymbol, a: number, b: number): Scene {
  let frames: Frame[]
  let res: number
  switch (op) {
    case '+': frames = buildAdd(a, b); res = a + b; break
    case '-': frames = buildSub(a, b); res = a - b; break
    case '*': frames = buildMul(a, b); res = a * b; break
    default:  frames = buildDiv(a, b); res = a / b; break
  }
  return { op, a, b, result: res, frames, height: sceneHeight(frames) }
}

/* ── Which component is open, and what it turns into ── */
const activeName = ref<string | null>(null)

const activeInfo = computed<{ scene: Scene | null; message: string | null }>(() => {
  const none = { scene: null, message: null }
  if (!result.value || !activeName.value) return none

  const dict = result.value.components_dictionary
  const m = dict[activeName.value]?.match(STEP_RE)
  if (!m) return { scene: null, message: "This component isn't a plain two-number step, so there is nothing to draw." }

  const op = m[2] as OpSymbol
  let a: number
  let b: number
  try {
    const memo: Record<string, number> = {}
    a = evaluateComponent(m[1], dict, memo)
    b = evaluateComponent(m[3], dict, memo)
  } catch {
    return { scene: null, message: "The numbers for this step couldn't be worked out." }
  }

  const problem = scopeProblem(a, b, op)
  if (problem) return { scene: null, message: problem }
  return { scene: buildScene(op, a, b), message: null }
})

const scene = computed(() => activeInfo.value.scene)
const sceneMessage = computed(() => activeInfo.value.message)

/* ── Playback: auto-advance through the frames, or step by hand ── */
const frameIdx = ref(0)
let playTimer: ReturnType<typeof setTimeout> | undefined

const frame = computed<Frame | null>(() => {
  const sc = scene.value
  if (!sc) return null
  return sc.frames[Math.min(frameIdx.value, sc.frames.length - 1)]
})

const prefersReducedMotion = () =>
  typeof window !== 'undefined' && !!window.matchMedia?.('(prefers-reduced-motion: reduce)').matches

function clearTimer() {
  if (playTimer) clearTimeout(playTimer)
  playTimer = undefined
}

// How long to stay on a frame: its own stagger has to finish, then a beat to read it.
function holdFor(f: Frame) {
  let longest = 0
  for (const s of f.blocks) if (s.delay > longest) longest = s.delay
  return 1500 + longest
}

function scheduleNext() {
  clearTimer()
  const sc = scene.value
  if (!sc || frameIdx.value >= sc.frames.length - 1) return
  playTimer = setTimeout(() => {
    frameIdx.value += 1
    scheduleNext()
  }, holdFor(sc.frames[frameIdx.value]))
}

function goTo(i: number) {
  clearTimer()
  frameIdx.value = i
}
function next() {
  if (scene.value) goTo(Math.min(frameIdx.value + 1, scene.value.frames.length - 1))
}
function prev() {
  goTo(Math.max(frameIdx.value - 1, 0))
}
function replayBlocks() {
  frameIdx.value = 0
  if (!prefersReducedMotion()) scheduleNext()
}

function toggleBlocks(name: string) {
  activeName.value = activeName.value === name ? null : name
}

// Whenever a different component is opened (or closed), start over from frame 1.
watch(scene, (sc) => {
  clearTimer()
  frameIdx.value = 0
  if (sc && sc.frames.length > 1 && !prefersReducedMotion()) scheduleNext()
})

onBeforeUnmount(clearTimer)

/* ── Turning frame data into styles ── */
const posStyle = (x: number, y: number) => ({
  transform: `translate(calc(var(--u) * ${x}), calc(var(--u) * ${y}))`
})

const blockStyle = (s: BlockState) => ({
  transform: `translate(calc(var(--u) * ${s.x}), calc(var(--u) * ${s.y})) scale(${s.scale})`,
  opacity: s.opacity,
  transitionDelay: `${s.delay}ms`
})

// Faint empty slots behind the blocks, so a pile reads as part of a grid.
const ghostCells = computed(() => {
  const f = frame.value
  if (!f) return []
  const out: { key: string; x: number; y: number }[] = []
  for (const b of f.boards) {
    for (let i = 0; i < b.slots; i++) {
      const p = slot(i, b.x, b.y, b.cols)
      out.push({ key: `${b.id}-${i}`, x: p.x, y: p.y })
    }
  }
  return out
})

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

/* ── Buttons ── */
.blocks-btn {
  @apply inline-flex items-center gap-1.5 rounded-md border border-slate-200 bg-white px-2.5 py-1 text-xs font-semibold text-slate-600 transition-colors
    hover:border-sky-300 hover:text-sky-700
    focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-sky-500
    dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300 dark:hover:border-sky-600 dark:hover:text-sky-300;
}
.blocks-btn-on { @apply border-sky-500 bg-sky-50 text-sky-700 dark:border-sky-500 dark:bg-sky-950 dark:text-sky-300; }

.ctl-btn {
  @apply rounded-md border border-slate-200 bg-white px-2.5 py-1 text-xs font-semibold text-slate-600 transition-colors
    hover:border-slate-300 hover:text-slate-900
    focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-sky-500
    disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:border-slate-200 disabled:hover:text-slate-600
    dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300 dark:hover:border-slate-600 dark:hover:text-slate-100;
}

.step-dot {
  @apply h-1.5 w-6 rounded-full bg-slate-200 transition-colors
    focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-sky-500
    dark:bg-slate-700;
}
.step-dot-done { @apply bg-sky-300 dark:bg-sky-800; }
.step-dot-on { @apply bg-sky-600 dark:bg-sky-400; }

/* ── Block stage ──
   .stage-box is a size container, so 100cqw is the stage's own width.
   One cell (--u) is that width split across the stage's fixed width in cells (--w),
   capped so blocks never get huge on wide screens. */
.stage-box { container-type: inline-size; }
.stage {
  --u: min(calc(100cqw / var(--w)), 30px);
  position: relative;
  margin-inline: auto;
  width: calc(var(--u) * var(--w));
  height: calc(var(--u) * var(--h));
}

.ghost,
.blk {
  position: absolute;
  left: calc(var(--u) * .07);
  top: calc(var(--u) * .07);
  width: calc(var(--u) * .86);
  height: calc(var(--u) * .86);
  border-radius: calc(var(--u) * .16);
}

.ghost { @apply border border-dashed border-slate-300 dark:border-slate-700; }
.ghost-enter-active,
.ghost-leave-active { transition: opacity .35s ease; }
.ghost-enter-from,
.ghost-leave-to { opacity: 0; }

.blk {
  box-shadow:
    inset 0 calc(var(--u) * -.08) 0 rgb(0 0 0 / .18),
    inset 0 calc(var(--u) * .05) 0 rgb(255 255 255 / .35);
  transition:
    transform .6s cubic-bezier(.22,1,.36,1),
    opacity .45s ease,
    background-color .45s ease;
  will-change: transform, opacity;
}
.blk-a { @apply bg-sky-500 dark:bg-sky-400; }
.blk-b { @apply bg-amber-500 dark:bg-amber-400; }
.blk-result { @apply bg-emerald-500 dark:bg-emerald-400; }
.blk-remove { @apply bg-rose-500 dark:bg-rose-400; }

.stage-label {
  position: absolute;
  left: 0;
  top: 0;
  white-space: nowrap;
  font-weight: 700;
  line-height: 1.2;
  font-size: clamp(11px, calc(var(--u) * .5), 15px);
}
.lbl-plain { @apply text-slate-500 dark:text-slate-400; }
.lbl-a { @apply text-sky-600 dark:text-sky-400; }
.lbl-b { @apply text-amber-600 dark:text-amber-400; }
.lbl-result { @apply text-emerald-600 dark:text-emerald-400; }
.lbl-remove { @apply text-rose-600 dark:text-rose-400; }
.lbl-enter-active { transition: opacity .3s ease .15s; }
.lbl-leave-active { transition: opacity .15s ease; }
.lbl-enter-from,
.lbl-leave-to { opacity: 0; }

@media (prefers-reduced-motion: reduce) {
  .token, .settle, .pop-answer, .step-enter-active { animation: none !important; transition: none !important; }
  .blk, .ghost-enter-active, .ghost-leave-active, .lbl-enter-active, .lbl-leave-active {
    transition: none !important;
  }
}
</style>
