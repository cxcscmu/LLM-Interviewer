import { FC, useState } from "react";
import { ChevronRight, ChevronDown } from "lucide-react";
import clsx from "clsx";

export const Accordion: FC<{
  children: React.ReactNode;
  type?: "single" | "multiple";
  collapsible?: boolean;
}> = ({ children }) => {
  return <div className="rounded-lg">{children}</div>;
};

export const AccordionItem: FC<{
  value: string;
  className?: string;
  children: React.ReactNode;
}> = ({ value, className, children }) => {
  const [isOpen, setIsOpen] = useState(true);

  return (
    <div className={className}>
      <div
        className="p-3 font-semibold text-lg cursor-pointer flex items-center justify-start space-x-2"
        onClick={() => setIsOpen(!isOpen)}
      >
        <span>{value}</span>
        {isOpen ? <ChevronDown size={20} /> : <ChevronRight size={20} />}
      </div>
      <div className={clsx("transition-all", isOpen ? "" : "max-h-0")}>
        {isOpen && children}
      </div>
    </div>
  );
};
