<script setup lang="ts">
import {ref} from "vue";
import axios from "axios";

type AiResponse = {
  station_name: string;
  message: string;
  intent: string;
  intents: string[];
  matched_text: string;
  score: number;
  distance: number;
  confidence: string;
  answer: string;
  ai_tip?: {
    title: string;
    content: string;
    category: string;
    score: number;
  };
  recommendation?: {
    priority: string;
    action: string;
    reason: string;
    score: number;
    similarity_score: number;
  };
};

const question = ref<string>("");
const result = ref<AiResponse | null>(null);
const loading = ref<boolean>(false);
const error = ref<string>("");

const askAI = async () => {
  if (!question.value.trim()) {
    error.value = "질문을 입력해주세요.";
    return;
  }

  loading.value = true;
  error.value = "";
  result.value = null;

  try {
    const requestBody = {
      station_name: "시청",
      message: question.value,
    };

    console.log("REQUEST BODY:", requestBody);

    const response = await axios.post<AiResponse>(
      "http://127.0.0.1:8000/ai/ask",
      requestBody,
      {
        headers: {
          "Content-Type": "application/json",
        },
      },
    );

    result.value = response.data;
  } catch (err: any) {
    console.log("API ERROR:", err);
    console.log("STATUS:", err.response?.status);
    console.log("DATA:", err.response?.data);

    if (err.response) {
      error.value = `서버 오류: ${err.response.status} / ${JSON.stringify(err.response.data)}`;
    } else {
      error.value = "서버 응답 없음: CORS 또는 주소 문제";
    }
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

      <textarea
        v-model="question"
        placeholder="예: 잠실역 수유실이랑 엘리베이터 알려줘"
      />

      <button @click="askAI" :disabled="loading">
        {{ loading ? "확인 중..." : "AI에게 물어보기" }}
      </button>

      <p v-if="error" class="error">{{ error }}</p>

      <section v-if="result" class="result">
        <h2>AI 답변</h2>
        <p>{{ result.answer }}</p>

        <div class="debug">
          <span>intent: {{ result.intent }}</span>
          <span>confidence: {{ result.confidence }}</span>
          <span>score: {{ result.score }}</span>
        </div>
      </section>
    </section>
  </main>
</template>

<style scoped>
.page {
  min-height: 100vh;
  background: #fff7f2;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.card {
  width: 100%;
  max-width: 430px;
  background: white;
  border-radius: 28px;
  padding: 28px;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.08);
}

.badge {
  display: inline-block;
  background: #ffe2d2;
  color: #ff7a45;
  padding: 8px 12px;
  border-radius: 999px;
  font-size: 14px;
  font-weight: 700;
}

h1 {
  font-size: 26px;
  line-height: 1.35;
  margin: 20px 0;
  color: #222;
}

textarea {
  width: 100%;
  height: 120px;
  border: 1px solid #eee;
  border-radius: 18px;
  padding: 16px;
  font-size: 16px;
  resize: none;
  box-sizing: border-box;
}

button {
  width: 100%;
  margin-top: 14px;
  border: none;
  border-radius: 16px;
  padding: 16px;
  background: #ff8a5b;
  color: white;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
}

button:disabled {
  opacity: 0.6;
}

.result {
  margin-top: 24px;
  padding: 18px;
  background: #f8f8f8;
  border-radius: 18px;
}

.result h2 {
  margin: 0 0 10px;
  font-size: 18px;
}

.result p {
  line-height: 1.6;
}

.debug {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-top: 12px;
  font-size: 13px;
  color: #777;
}

.error {
  margin-top: 12px;
  color: #e5484d;
}
</style>
