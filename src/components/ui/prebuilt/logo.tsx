import React, { FC } from "react";
import Image from "next/image";

export const Logo: FC<{
  pageLabel?: string;
}> = ({ pageLabel }) => {
  const label: string = pageLabel ? `: ${pageLabel}` : "";
  const title = `CLUE-LLM${label}`;

  return (
    <a href="/" className="fixed gap-3 top-6 flex items-center justify-center cursor-default select-none cursor-pointer">
      {/* This keeps the three pieces aligned in a row. */}
      <div className="h-fit dark:text-zinc-100">
        {/* This div keeps the size of the icon reasonable */}
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
        {/* placeholder icon */}
      </div>
      <div className="text-center font-medium text-xl mr--1 md:text-2xl text-zinc-900 relative text-nowrap dark:text-zinc-100">
        {/* Sets the logo to be the right size. */}
        {title}
      </div>
      <div
        className="
            transform scale-75 origin-left border items-center rounded-lg px-2 py-1 text-xs font-medium
            bg-zinc-200 border-zinc-300 text-zinc-500
            dark:bg-zinc-700 dark:border-zinc-600 dark:text-zinc-400"
      >
        {/* adds an 'alpha' label in a little box */}
        alpha
      </div>
    </a>
  );
};
