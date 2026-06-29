// AnswerCard.vue

<script setup lang="ts">
import type {AiResponse} from "../types/aiTypes";

defineProps<{
  result: AiResponse;
}>();
</script>

<template>
  <section class="result">
    <h2>AI 답변</h2>
    <p>{{ result.answer }}</p>

    <div class="debug">
      <span>intent: {{ result.intent }}</span>
      <span>confidence: {{ result.confidence }}</span>
      <span>score: {{ result.score }}</span>
    </div>
  </section>
</template>
