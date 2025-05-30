// This file pairs the chatlog and chat-message components together, and provides the information they require to function. useChat() is defined here to allow them to share information properly.

"use client";
import { FC, MouseEventHandler, ReactNode, useEffect, useState } from "react";
import { CoreMessage, Message } from "ai";
import { useChat } from "ai/react";
import { ArrowBigRightDash } from "lucide-react";
import clsx from "clsx";

import { Chatlog, ChatMessage, Selector } from "@logic";
import { getHistory, setHistory } from "@utils";
import { conversation, selection } from "@interfaces";
import { FunctionButton, Subtitle } from "@ui";
import next from "next";
import { useRouter } from "next/navigation";

export const Conversation: FC<{
  placeholder?: string;
  system?: string;
  logLabel: "session" | "interview";
  modelsList: selection[];
  initialMessages?: CoreMessage[];
  skipLabel: string;
  nextPage: string;
  skipFunction?: Function;
  skipIcon?: ReactNode;
}> = ({
  placeholder = "Type here...",
  system,
  modelsList,
  logLabel,
  initialMessages = [],
  skipLabel,
  nextPage,
  skipFunction,
  skipIcon = <ArrowBigRightDash size={20} />
}) => {
  const { messages, input, handleInputChange, handleSubmit } = useChat({
    initialMessages: initialMessages as Message[],
  });

  const [LLM, setLLM] = useState(modelsList[0].value);

  const router = useRouter()

  useEffect(() => {
    const updateHist = async () => {
      const hist = getHistory();

      const newHist: conversation = {
        ...hist,
        ...(logLabel === "session" && {
          session: messages,
          sessionModel: LLM,
          sessionStart: hist.sessionStart ? hist.sessionStart : new Date(),
          sessionEnd: new Date(),
        }),
        ...(logLabel === "interview" && {
          interview: messages,
          interviewModel: LLM,
          interviewStart: hist.interviewStart
            ? hist.interviewStart
            : new Date(),
          interviewEnd: new Date(),
        }),
      };

      setHistory(newHist);
    };

    updateHist();
  }, [messages, LLM, logLabel]);

  const modelVars = {
    model: LLM,
    ...(system && { system: system }),
  };

  const skip = (
    <label className="flex">
      <div
        className={clsx(
          "my-auto ml-auto mr-1 text-xs text-right select-none opacity-50",
          "text-zinc-500",
          "dark:text-zinc-300",
          {
            "hover:text-zinc-700 hover:dark:text-zinc-200 opacity-100":
              Boolean(messages.length > initialMessages.length + 5),
          },
        )}
      >
        {skipLabel}
      </div>
      <FunctionButton
        onClick={() => {
          if (skipFunction) {skipFunction()}
          else {router.push(nextPage)}
        }}
        disabled={Boolean(messages.length <= initialMessages.length + 5)}
        labeled={false}
      >
        {skipIcon}
      </FunctionButton>
    </label>
  );

  return (
    <div>
      {messages.length == 0 && (
        <Subtitle>Choose a model and chat!</Subtitle>
      )}
      <Chatlog chatLog={messages} />
      <div className={messages.length == 0 ? ""
        : "fixed bottom-10 w-full pr-7 md:w-2/3"}
      >
        <div className="p-5 bg-zinc-100 dark:bg-zinc-800 rounded-xl mt-3 mb-2">
          <ChatMessage
            handleSubmit={handleSubmit}
            modelVars={modelVars}
            input={input}
            handleInputChange={handleInputChange}
            placeholder={placeholder}
          />
          <Selector
            label="Model:"
            values={modelsList}
            target={LLM}
            setFunc={setLLM}
            disabled={Boolean(messages.length > initialMessages.length)}
          />
        </div>
        {skip}
      </div>
    </div>
  );
};
