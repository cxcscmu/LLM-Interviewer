// This file implements a button that runs a given function. It can optionally take a a child to be displayed, or will display a simple squircle otherwise.

import { FC, MouseEventHandler, ReactNode } from "react";
import { Squircle } from "lucide-react";
import clsx from "clsx";

export const FunctionButton: FC<{
  children?: ReactNode;
  onClick?: MouseEventHandler;
  submit?: boolean;
  disabled?: boolean;
  labeled?: boolean;
  background?: boolean;
}> = ({
  children,
  onClick = () => {},
  submit = false,
  disabled = false,
  labeled = true,
  background = true,
}) => {
  if (children === undefined) {
    children = <Squircle size={16} />;
  }

  return (
    <button
      type={submit ? "submit" : "button"}
      className={clsx(
        "w-auto py-1 px-2 active:enabled:scale-95 hover:enabled:scale-105 border overflow-hidden relative rounded-xl disabled:opacity-50  text-zinc-100 fill-white",
        {
          "dark:bg-zinc-50 dark:border-white dark:text-zinc-900 dark:fill-zinc-50":
            !labeled,
        },
        {
          "bg-zinc-950 dark:bg-zinc-50": background,
        },
        {
          "border-none dark:bg-zinc-800": !background,
        },
      )}
      onClick={onClick}
      disabled={disabled}
    >
      <div className="select-none">{children}</div>
    </button>
  );
};
