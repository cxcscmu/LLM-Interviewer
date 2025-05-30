// This page implements the chat that the user initially has with the chatbot. After sending at least 5 messages, it allows you to continue to the interview.

"use client";
import React, { ReactElement } from "react";

import { Conversation } from "@logic";
import { Footer, Logo, FAQ, Centered, Stacked } from "@ui";
import { getHistory, sessionModels } from "@utils";

export default function Home(): ReactElement {
  return (
    <Centered>
      <Stacked>
        <Conversation
          placeholder="Chat with me!"
          logLabel="session"
          skipLabel="Continue to the interview page after sending at least a few messages."
          nextPage="/interview"
          modelsList={sessionModels}
        />
        <Footer />
        <FAQ />
      </Stacked>
      <Logo />
    </Centered>
  );
}
