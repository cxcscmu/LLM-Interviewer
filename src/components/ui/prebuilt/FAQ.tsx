import { FC } from "react";
import Popup from "reactjs-popup";

import { FunctionButton } from "@ui";
import { ArrowBigRight, ArrowBigRightDash, Download } from "lucide-react";

export const FAQ: FC<{}> = () => {
  const toggle = (
    <div className="fixed top-5 right-5">
      <FunctionButton labeled={false}>FAQ</FunctionButton>
    </div>
  );

  return (
    <Popup
      trigger={toggle}
      modal
      overlayStyle={{ background: "rgba(0,0,0,0.5)" }}
    >
      <div className="bg-white dark:bg-zinc-800 w-[50vw] h-[65vh] object-center opacity-95 rounded-lg p-5 shadow-lg overflow-scroll">
        <div className="relative flex flex-col gap-2 px-5 py-3 text-black dark:text-zinc-100 ">
          {/* <Logo /> */}
          <strong className="text-3xl">Instructions</strong>
          <p className="mt-3">
            CLUE - which stands for Chatbot-Led User Experience interviews - was a research project conducted at CMU, studying whether or not chatbots could potentially serve as a replacement or supplement to human interviewers. This repo replicates that experiment in miniature, as a local project.
          </p>
          <p>
            To begin, {"you'll"} first need to set up the project and its required environment variables. Instructions on how to do so are found in the README.md on this github repo, <a href="https://github.com/cxcscmu/CLUE-LLM-open/blob/main/README.md" className="underline hover:font-bold">here</a>.
          </p>
          <p>
            In the initial chat page, you will send the first message after selecting a model after from the selector, which displays the models you have enabled during the setup period. After sending at least 3 messages, you can click the {" "} <ArrowBigRightDash className="inline" /> button to continue on to the interview portion of the project.
          </p>
          <p>
            In the final page of the project, you will speak with a virtual
            interviewer about your conversation in the previous page. Here, the interviewer will send the first message, and should lead the conversation. Once again, after sending at least 3 messages, you can hit the {" "} <Download className="inline" /> button to conclude the interview.
          </p>
          <p>
            When you click the {" "} <Download className="inline" /> button to end the interview, the program will allow you to save a .json file of your conversation to your computer. Be sure to put this in an accessible place, as you'll need it to use CLUE-LLM!
          </p>
        </div>
      </div>
    </Popup>
  );
};
