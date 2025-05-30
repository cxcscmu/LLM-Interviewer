// This file is essentially just a list of the models (their value strings, with an internal label) to implement the choice of LLMs.

import { selection } from "@interfaces";

// Models from OpenAI
const OPENAI_GPT_4o: selection = {
  value: "gpt-4o",
  label: "OpenAI: ChatGPT",
};
const OPENAI_GPT_4o_mini: selection = {
  value: "gpt-4o-mini",
  label: "OpenAI: ChatGPT Mini",
};

// Models from Anthropic
const Anthropic_Claude_Sonnet: selection = {
  value: "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
  label: "Anthropic: Claude 3.5 Sonnet",
};
const Anthropic_Claude_Haiku: selection = {
  value: "us.anthropic.claude-3-5-haiku-20241022-v1:0",
  label: "Anthropic: Claude 3.5 Haiku",
};
const Anthropic_Claude_Opus: selection = {
  value: "us.anthropic.claude-3-opus-20240229-v1:0",
  label: "Anthropic: Claude 3.5 Opus",
};

// Models from Google
const Gemini_1_5_Flash: selection = {
  value: "gemini-1.5-flash",
  label: "Google: Gemini 1.5 Flash",
};
const Gemini_1_5_Pro: selection = {
  value: "gemini-1.5-pro",
  label: "Google: Gemini 1.5 Pro",
};

// Models from Meta
const Llama3_3_70b_Instruct: selection = {
  value: "us.meta.llama3-3-70b-instruct-v1:0",
  label: "Meta: Llama 3.3 70b Instruct",
};

// Models from Amazon
const Amazon_Nova_Pro: selection = {
  value: "us.amazon.nova-pro-v1:0",
  label: "Amazon: Nova Pro",
};
const Amazon_Nova_Lite: selection = {
  value: "us.amazon.nova-lite-v1:0",
  label: "Amazon: Nova Lite",
};
const Amazon_Nova_Micro: selection = {
  value: "us.amazon.nova-micro-v1:0",
  label: "Amazon: Nova Micro",
};

// Models from Deepseek
const Deepseek_V3: selection = {
  value: "deepseek-ai/DeepSeek-V3", // on togetherai
  label: "DeepSeek V3",
};

const Deepseek_R1: selection = {
  value: "deepseek-ai/DeepSeek-R1", // on togetherai
  label: "DeepSeek R1",
};

export const sessionModels: selection[] = [
  OPENAI_GPT_4o,
  // OPENAI_GPT_4o_mini
  Anthropic_Claude_Sonnet,
  // Anthropic_Claude_Haiku,
  // Anthropic_Claude_Opus
  // Gemini_1_5_Flash,
  // Gemini_1_5_Pro
  // Llama3_3_70b_Instruct,
  // Amazon_Nova_Pro,
  // Amazon_Nova_Lite
  // Amazon_Nova_Micro
  // Deepseek_R1,
  // Deepseek_V3,
];

export const interviewModels: selection[] = [
  OPENAI_GPT_4o,
];
