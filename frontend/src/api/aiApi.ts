// aiApi.ts

import axios from "axios";
import type {AiResponse} from "../types/aiTypes";
import {API_BASE_URL} from "../constants/api";

export const askAi = async (
  stationName: string,
  message: string,
): Promise<AiResponse> => {
  const requestBody = {
    station_name: stationName,
    message,
  };

  const response = await axios.post<AiResponse>(
    `${API_BASE_URL}/ai/ask`,
    requestBody,
    {
      headers: {
        "Content-Type": "application/json",
      },
    },
  );

  return response.data;
};
