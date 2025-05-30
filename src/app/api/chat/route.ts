// This file implements the local API call for chatting with a textbot and its immediate needs:
// The tool a bot needs in order to view a prior conversation;
// The POST request that determines which model is being used and makes the call to an external API.

import { createOpenAI, openai } from "@ai-sdk/openai";
import { google } from "@ai-sdk/google";
import { createTogetherAI } from "@ai-sdk/togetherai";
import { LanguageModel, streamText } from "ai";

// Helps prevent the request from timing out.
export const maxDuration = 300;

export async function POST(req: Request) {
  const { messages, model, system } = await req.json();
  let result;

  // Implements switching between models
  switch (model) {
    // Models that go through the Google SDK.
    case "gemini-2.0-flash-exp":
    case "gemini-1.5-flash":
    case "gemini-1.5-pro":
      result = streamText({
        model: google(model),
        messages: messages,
        system: system,
      });
      break;
    // Models that go through the OpenAI SDK.
    case "gpt-4o":
    case "gpt-4o-mini":
      result = streamText({
        model: openai(model),
        messages: messages,
        system: system,
      });
      break;
    // Models on TogetherAI
    case "deepseek-ai/DeepSeek-R1":
    case "deepseek-ai/DeepSeek-V3":
      const togetherai = createTogetherAI({
        apiKey: process.env.TOGETHER_AI_API_KEY,
      });
      result = streamText({
        model: togetherai(model) as LanguageModel,
        messages: messages,
        system: system,
      });
      break;
    // Bedrock models through a custom API
    case "us.meta.llama3-3-70b-instruct-v1:0":
    case "us.anthropic.claude-3-opus-20240229-v1:0":
    case "us.anthropic.claude-3-5-haiku-20241022-v1:0":
    case "us.anthropic.claude-3-5-sonnet-20241022-v2:0":
    case "us.amazon.nova-pro-v1:0":
    case "us.amazon.nova-lite-v1:0":
    case "us.amazon.nova-micro-v1:0":
      const bedrock_api = process.env.BEDROCK_API_KEY;
      const bedrock = createOpenAI({
        baseURL: process.env.BEDROCK_BASE_URL,
        apiKey: bedrock_api,
      });
      result = streamText({
        model: bedrock(model),
        messages: messages,
        system: system,
      });
      break;
  }

  if (result) {
    return result.toDataStreamResponse();
  } else console.log("No model was provided.");
}
