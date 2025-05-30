import { ReactNode, FC } from "react";

export const Subtitle: FC<{
  children: ReactNode;
}> = ({ children }) => {
  return (
    <div className="text-center font-medium text-2xl text-black dark:text-white relative">
      {children}
    </div>
  );
};
