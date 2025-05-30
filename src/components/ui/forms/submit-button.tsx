// This file implements a simple submit button to go with text fields, using the slightly more-complex FunctionButton component.

import { FC } from "react";
import { ArrowBigRight } from "lucide-react";

import { FunctionButton } from "@ui";

export const SubmitButton: FC<{
  disabled?: boolean;
}> = ({ disabled = false }) => {
  return (
    <FunctionButton submit={true} disabled={disabled}>
      <ArrowBigRight className="text-white dark:text-black" size={16} />
    </FunctionButton>
  );
};
