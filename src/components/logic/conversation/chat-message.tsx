// This file implements the half of the conversation module that takes the user's input, inheriting the required functions and variables to do so from <conversation>

"use client";
import React, { FC } from "react";

import { Label, SubmitButton, TextInput } from "@ui";

export const ChatMessage: FC<{
  handleSubmit: Function;
  modelVars: {
    model: string;
    system?: string;
  };
  input: string;
  handleInputChange: React.ChangeEventHandler;
  placeholder: string;
}> = ({ handleSubmit, modelVars, input, handleInputChange, placeholder }) => {
  return (
    <div>
      <form
        onSubmit={(event) =>
          handleSubmit(event, {
            body: modelVars,
          })
        }
        autoComplete="off"
      >
        <Label label="chat-bar" border={false}>
          <TextInput
            id="chat-bar"
            value={input}
            onChange={handleInputChange}
            placeholder={placeholder}
            border={false}
          />
          <SubmitButton />
        </Label>
      </form>
    </div>
  );
};
