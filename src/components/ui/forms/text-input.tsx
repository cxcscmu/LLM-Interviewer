// This file implements a simple text input, along with an option to display or not display a text submit button.

"use client";

import { FC } from "react";

export const TextInput: FC<{
  id: string;
  value: string;
  onChange: React.ChangeEventHandler;
  placeholder?: string;
  disabled?: boolean;
  disabledPlaceholder?: string;
  border?: boolean;
}> = ({
  id,
  value,
  onChange,
  placeholder = "Type here...",
  disabled = false,
  disabledPlaceholder = "",
  border = true,
}) => {
  return (
    <input
      id={id}
      value={value}
      onChange={onChange}
      placeholder={disabled ? disabledPlaceholder : placeholder}
      autoFocus
      disabled={disabled}
      className={`
        pr-6 w-full rounded-md flex-1 outline-none bg-zinc-100 text-black dark:text-white dark:bg-zinc-800 placeholder-zinc-500 dark:placeholder-zinc-300
        disabled:opacity-50 disabled:select-none disabled:placeholder-zinc-400 
      ${border ? "px-2" : ""}`}
    />
  );
};
