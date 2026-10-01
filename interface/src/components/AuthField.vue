<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  modelValue: { type: String, default: '' },
  label: { type: String, required: true },
  id: { type: String, required: true },
  type: { type: String, default: 'text' },
  error: { type: String, default: '' },
  autocomplete: { type: String, default: 'off' },
  placeholder: { type: String, default: '' },
})
const emit = defineEmits(['update:modelValue'])

const show = ref(false)
const isPassword = props.type === 'password'
const inputType = computed(() => (isPassword && show.value ? 'text' : props.type))
</script>

<template>
  <div>
    <label :for="id" class="mb-1.5 block text-sm font-semibold text-slate-700 dark:text-slate-300">{{ label }}</label>

    <div class="relative">
      <input
        :id="id"
        :type="inputType"
        :value="modelValue"
        :autocomplete="autocomplete"
        :placeholder="placeholder"
        :aria-invalid="!!error"
        :aria-describedby="error ? id + '-error' : undefined"
        @input="emit('update:modelValue', $event.target.value)"
        class="w-full rounded-xl border bg-white px-4 py-3 text-base text-slate-900 placeholder-slate-400 outline-none
               transition-all duration-200 focus:-translate-y-0.5 focus:ring-4
               dark:bg-slate-900 dark:text-white dark:placeholder-slate-600"
        :class="[
          isPassword && 'pr-12',
          error
            ? 'border-red-500 focus:ring-red-500/20'
            : 'border-slate-300 focus:border-indigo-500 focus:ring-indigo-500/20 dark:border-slate-700 dark:focus:border-indigo-400',
        ]"
      />

      <button
        v-if="isPassword"
        type="button"
        @click="show = !show"
        :aria-label="show ? 'Hide password' : 'Show password'"
        :aria-pressed="show"
        class="absolute right-2 top-1/2 grid h-9 w-9 -translate-y-1/2 place-items-center rounded-lg text-slate-500
               transition-colors hover:text-slate-900 dark:hover:text-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-indigo-500"
      >
        <svg v-if="!show" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12z" /><circle cx="12" cy="12" r="3" />
        </svg>
        <svg v-else class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M17.9 17.9A10.9 10.9 0 0112 20C5 20 1 12 1 12a18 18 0 015.1-5.9M9.9 4.2A10.7 10.7 0 0112 4c7 0 11 8 11 8a18 18 0 01-2.2 3.2M1 1l22 22" />
        </svg>
      </button>
    </div>

    <Transition name="err">
      <p v-if="error" :id="id + '-error'" role="alert" class="mt-1.5 text-sm text-red-600 dark:text-red-400">{{ error }}</p>
    </Transition>
  </div>
</template>

<style scoped>
.err-enter-active, .err-leave-active { transition: all 0.25s ease; }
.err-enter-from, .err-leave-to { opacity: 0; transform: translateY(-4px); }
</style>
