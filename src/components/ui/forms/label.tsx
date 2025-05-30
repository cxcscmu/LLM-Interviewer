//This file is a simple label collection for its children.

"use client";
import { ReactNode, FC } from "react";

export const Label: FC<{
  children: ReactNode;
  label: string;
  border?: boolean;
}> = ({ children, label, border = true }) => {
  return (
    <label
      className={`relative flex items-center justify-center rounded-lg mb-4 focus-within:border-zinc-300 min-w-96 ${border ? "border border-zinc-300 focus-within:border-zinc-300 py-2 px-2 gap-2" : ""}`}
      htmlFor={label}
    >
      {children}
    </label>
  );
};
