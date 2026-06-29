// AiTipCard.vue

<script setup lang="ts">
import type {AiResponse} from "../types/aiTypes";

defineProps<{
  aiTip: AiResponse["ai_tip"];
}>();
</script>

<template>
  <section v-if="aiTip" class="sub-card">
    <h2>{{ aiTip.title }}</h2>
    <p>{{ aiTip.content }}</p>
    <span class="meta">category: {{ aiTip.category }}</span>
  </section>
</template>
