// This is the initial landing page, which directs you to the chat session.

"use client";
import React, { ReactElement } from "react";
import { useState } from "react";
import { useRouter } from "next/navigation";

import {
  Centered,
  FAQ,
  FunctionButton,
  Label,
  Logo,
  Stacked,
  SubmitButton,
  Subtitle,
  TextInput,
} from "@ui";
import { setHistory } from "@utils";
import { ArrowBigRightDash } from "lucide-react";

export default function Home(): ReactElement {
  const router = useRouter();

  return (
    <Centered>
      <Stacked>
        <Subtitle>Welcome to CLUE-LLM!</Subtitle>
          <center>
          <span className="text-center dark:text-zinc-100 m-2">
            To select and chat with an LLM, click this button:
          </span>
          <FunctionButton
            labeled={false}
            onClick={() => router.push("/session")}
            >
              <ArrowBigRightDash className="self-center inline" size={20} />
          </FunctionButton>
          </center>
      </Stacked>
      <Logo />
      <FAQ />
    </Centered>
  );
}
