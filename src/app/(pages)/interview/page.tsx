// This page implements the chat that will interview the user about their previous conversation.

"use client";
import React, { ReactElement, useState } from "react";

import { conversation } from "@interfaces";
import { Conversation } from "@logic";
import { Footer, Subtitle, Logo, FAQ, Centered, Stacked, FunctionButton } from "@ui";
import {
  getHistory,
  interviewModels,
  startMessage,
  systemPrompt,
} from "@utils";
import { DownloadCloud, DownloadIcon } from "lucide-react";

const handleDownload = (history: conversation) => {
  const jsonStr = JSON.stringify(history, null, 2); // pretty-print with 2 spaces
  const blob = new Blob([jsonStr], { type: "application/json" });
  const url = URL.createObjectURL(blob);

  const link = document.createElement('a');
  link.href = url;
  link.download = `chatlog-${history.interviewEnd}.json`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);

  // Free up memory
  URL.revokeObjectURL(url);
};

export default function Home(): ReactElement {
  const hist = getHistory();

  return (
    <Centered>
      <Logo />
      <Stacked>
        <Subtitle>Be interviewed about the previous conversation.</Subtitle>
        <Conversation
          placeholder="Respond here."
          system={systemPrompt}
          logLabel="interview"
          initialMessages={startMessage(hist)}
          skipLabel="Save your conversation after finishing it."
          nextPage="/"
          modelsList={interviewModels}
          skipFunction={() => handleDownload(getHistory())}
          skipIcon={<DownloadIcon size={20}/>}
        />
        <Footer />
        <FAQ />
      </Stacked>
    </Centered>
  );
}
