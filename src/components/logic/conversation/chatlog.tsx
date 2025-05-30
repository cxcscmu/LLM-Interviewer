"use client";
import { FC, useEffect, useRef, useState } from "react";
import clsx from "clsx";
import { Message } from "ai";
import ReactMarkdown from "react-markdown";
import Image from "next/image";
import { Accordion, AccordionItem } from "@ui";

export const Chatlog: FC<{ chatLog: Message[] }> = ({ chatLog }) => {
  const chatEndRef = useRef<null | HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatLog]);

  if (chatLog.length) {
    return (
      <div
        className={`
        fixed top-16 pr-3 md:w-2/3 w-full r-7 pb-10 ${
          process.env.NODE_ENV === "development"
            ? "bottom-[calc(12.5rem)]"
            : "bottom-[calc(10rem)]"
        } outline-none rounded-lg overflow-y-auto
        bg-white
        dark:bg-zinc-900 dark:border-zinc-700`}
      >
        {chatLog.map((item) => {
          if (!item.content || typeof item.content !== "string") return null;

          const fullThinkMatch = item.content.match(
            /<think>([\s\S]*?)<\/think>/,
          );
          const openThinkMatch = item.content.match(/<think>([\s\S]*)/);
          const reasoning = fullThinkMatch
            ? fullThinkMatch[1].trim()
            : openThinkMatch
              ? openThinkMatch[1].trim()
              : "";
          const messageContent = fullThinkMatch
            ? item.content.replace(/<think>[\s\S]*?<\/think>/g, "").trim()
            : openThinkMatch
              ? ""
              : item.content.trim();

          return (
            <div>
              {item.content && (
                <div className="flex flex-row">
                  {item.role !== "user" && (
                    <div className="h-10 mt-3 mr-2">
                      <Image
                        width={32}
                        height={32}
                        src="/images/cmu-scotty.png"
                        className="dark:hidden"
                        alt="Scotty Logo"
                      />
                      <Image
                        width={32}
                        height={32}
                        src="/images/cmu-scotty-dark.png"
                        className="hidden dark:block"
                        alt="Scotty Logo"
                      />
                    </div>
                  )}
                  <div
                    className={clsx("w-fit max-w-[75%]", {
                      "ml-auto text-right": item.role === "user",
                    })}
                  >
                    {reasoning && (
                      <Accordion type="single" collapsible>
                        <AccordionItem
                          value="Reasoning"
                          className="min-w-16 text-black dark:text-zinc-100"
                        >
                          <div className="px-5 py-2 text-sm bg-zinc-100 dark:bg-zinc-800 rounded-xl text-black dark:text-zinc-100">
                            <ReactMarkdown>{reasoning}</ReactMarkdown>
                          </div>
                        </AccordionItem>
                      </Accordion>
                    )}
                    {messageContent && (
                      <div className="my-2 px-5 py-2 outline-none border border-zinc-100 rounded-xl bg-zinc-100 dark:border-zinc-800 dark:bg-zinc-800 text-black dark:text-zinc-100">
                        <ReactMarkdown>{messageContent}</ReactMarkdown>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          );
        })}
        <div ref={chatEndRef}></div>
      </div>
    );
  }
};
