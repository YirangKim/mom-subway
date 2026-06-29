// ai.ts

export type AiResponse = {
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
