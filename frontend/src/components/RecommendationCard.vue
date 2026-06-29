// RecommendationCard.vue

<script setup lang="ts">
import type {AiResponse} from "../types/aiTypes";

defineProps<{
  recommendation: AiResponse["recommendation"];
}>();
</script>

<template>
  <section v-if="recommendation" class="sub-card">
    <h2>추천 행동</h2>
    <p class="action">{{ recommendation.action }}</p>
    <p>{{ recommendation.reason }}</p>
  </section>
</template>
