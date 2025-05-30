// This is used to select a specific model for testing, or simply to set the model randomly if in the production environment.

"use client";
import { FC, useState } from "react";
import { Dices } from "lucide-react";

import { selection } from "@interfaces";
import { FunctionButton } from "@ui";

export const Selector: FC<{
  label?: string;
  values: selection[];
  target: string;
  setFunc: Function;
  disabled?: Boolean;
}> = ({ label = "", values, target, setFunc, disabled = false }) => {
  const handleRandomize = () => {
    const randIndex = Math.floor(Math.random() * values.length);
    setFunc(values[randIndex].value);
  };

  if (!disabled && values.length > 1) {
    return (
      <div className="flex flex-row items-center justify-start">
        {/* Keeps the label and selector in a single line. */}
        <p className="text-sm select-none text-right dark:text-zinc-100">
          {label}
        </p>
        <select
          className="
            text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block p-2.5 mx-2
            bg-zinc-100 text-zinc-900 dark:text-zinc-100 dark:bg-zinc-800 dark:focus:ring-blue-500 dark:focus:border-blue-500
            disabled:bg-zinc-500 disabled:border-zinc-500 disabled:text-zinc-300
            disabled:dark:text-zinc-300"
          value={target}
          onChange={(e) => setFunc(e.target.value)}
        >
          {/* choose between one of several options */}
          {values.map((item, index) => (
            <option key={index} value={item.value}>
              {item.label}
            </option>
          ))}
        </select>
        <FunctionButton
          background={false}
          onClick={handleRandomize}
          labeled={false}
        >
          <Dices size={20} className="text-black dark:text-zinc-100" />
        </FunctionButton>
      </div>
    );
  } else {
    return <p className="text-sm select-none text-left dark:text-zinc-100">
      Chatting with {target}
    </p>
  }
};
