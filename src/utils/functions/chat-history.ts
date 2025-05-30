"use client";
import { create } from "zustand";
import { persist } from "zustand/middleware";

import { conversation, conversationProperty, convUpdate } from "@/interfaces";

interface State {
  conv: conversation;
}

interface Action {
  setConv: (newConv: conversation) => void;
}

const useStore = create(
  persist<State & Action>(
    (set) => ({
      conv: JSON.parse(
        JSON.stringify({
          sessionModel: "",
          session: [],
          interviewModel: "",
          interview: [],
        }),
      ) as conversation,
      setConv: (newConv: conversation) => set(() => ({ conv: newConv })),
    }),
    { name: "conversation-store" },
  ),
);

export const getHistory = (): conversation => {
  const { conv } = useStore.getState();
  return conv;
};

export const setHistory = (newHist: conversation): void => {
  useStore.setState({ conv: newHist });
};