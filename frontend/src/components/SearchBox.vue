// SearchBox.vue

<script setup lang="ts">
defineProps<{
  stationName: string;
  question: string;
  loading: boolean;
}>();

const emit = defineEmits<{
  "update:stationName": [value: string];
  "update:question": [value: string];
  submit: [];
}>();
</script>

<template>
  <section>
    <input
      :value="stationName"
      placeholder="역 이름을 입력해주세요. 예: 시청"
      @input="
        emit('update:stationName', ($event.target as HTMLInputElement).value)
      "
    />

    <textarea
      :value="question"
      placeholder="예: 수유실 알려줘"
      @input="
        emit('update:question', ($event.target as HTMLTextAreaElement).value)
      "
    />

    <button @click="emit('submit')" :disabled="loading">
      {{ loading ? "확인 중..." : "AI에게 물어보기" }}
    </button>
  </section>
</template>
