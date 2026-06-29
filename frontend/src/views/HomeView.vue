<script setup lang="ts">
import {ref} from "vue";
import type {AiResponse} from "../types/aiTypes";
import {askAi} from "../api/aiApi";

import SearchBox from "../components/SearchBox.vue";
import AnswerCard from "../components/AnswerCard.vue";
import AiTipCard from "../components/AiTipCard.vue";
import RecommendationCard from "../components/RecommendationCard.vue";

const stationName = ref<string>("");
const question = ref<string>("");
const result = ref<AiResponse | null>(null);
const loading = ref<boolean>(false);
const error = ref<string>("");

const handleAskAI = async () => {
  if (!stationName.value.trim()) {
    error.value = "역 이름을 입력해주세요.";
    return;
  }

  if (!question.value.trim()) {
    error.value = "질문을 입력해주세요.";
    return;
  }

  loading.value = true;
  error.value = "";
  result.value = null;

  try {
    result.value = await askAi(stationName.value, question.value);
  } catch (err: any) {
    console.log("API ERROR:", err);
    console.log("STATUS:", err.response?.status);
    console.log("DATA:", err.response?.data);

    error.value = "AI 서버 요청에 실패했습니다.";
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <main class="page">
    <section class="card">
      <p class="badge">momsubway AI</p>

      <h1>아이와 함께 지하철 이동,<br />무엇을 도와드릴까요?</h1>

      <SearchBox
        v-model:station-name="stationName"
        v-model:question="question"
        :loading="loading"
        @submit="handleAskAI"
      />

      <p v-if="error" class="error">{{ error }}</p>

      <AnswerCard v-if="result" :result="result" />

      <RecommendationCard
        v-if="result?.recommendation"
        :recommendation="result.recommendation"
      />

      <AiTipCard v-if="result?.ai_tip" :ai-tip="result.ai_tip" />
    </section>
  </main>
</template>
