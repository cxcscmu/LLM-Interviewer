import { FC, ReactNode } from "react";

export const Stacked: FC<{
  children: ReactNode;
}> = ({ children }) => {
  return (
    <div className="rounded-lg relative flex flex-col gap-2 px-4 w-full md:w-2/3">
      {children}
    </div>
  );
};
