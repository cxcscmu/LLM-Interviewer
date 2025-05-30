# LLM-Interviewer: CLUE

**Chatbot-Led User Experience (CLUE) Interviewer**

## Getting Started

### Prerequisites

- Node.js (v18 or later recommended)
- npm or yarn
- Python (>=3.12 recommended)

### Installation

#### Dependencies

First, clone the project and install dependencies.

```bash
git clone https://github.com/cxcscmu/LLM-Interviewer
cd LLM-Interviewer
npm install  # or yarn install
```

To install dependencies for the frontend, run
```bash
npm install  # or yarn install
```

To install dependencies for the insighter, run
```bash
pip install -r insighter/requirements.txt
```

#### API Keys

Next, create a .env file. This file will contain API keys for each LLM service you want to use, in the format `API_KEY_NAME=apikey`. A list of implemented services and the name of their expected API key follows:

- OpenAI's gpt models (gpt-4o and gpt-4o-mini): OPENAI_API_KEY
- Anthropic's models through Amazon Bedrock (Claude 3.5 Sonnet, Haiku, and Opus): BEDROCK_API_KEY
- Google's Gemini models (1.5 Flash and Pro): GOOGLE_GENERATIVE_AI_API_KEY
- Meta's Llama model through Amazon Bedrock (3.3 70b Instruct): BEDROCK_API_KEY
- Amazon's models through Amason Bedrock (Nova Pro, Lite, and Micro): BEDROCK_API_KEY
- Deepseek's models through TogetherAI (R1 and V3): TOGETHER_AI_API_KEY

We use https://github.com/aws-samples/bedrock-access-gateway for inference on models available on Amazon Bedrock via the OpenAI Python SDK. Follow the instructions on the repo README to generate `BEDROCK_API_KEY` and `BEDROCK_BASE_URL`.

The only required API keys are the OpenAI key and the Bedrock access gateway keys, as CLUE-LLM uses gpt-4o as its interviewer, and the Insighter uses Anthropic models through Bedrock at different points. You will need to provide your own API keys.

If you have additional keys, you can enable the models which use that key by opening the `/src/utils/constants/interview-system.ts` file and un-commenting the appropriate lines in the `sessionModels` list.

#### Adding New Models

For advanced users, additional models can be added through adding new cases to the switch statement in `/src/app/api/chat/route.ts` and adding new constants to the `sessionModels` list in `/src/utils/constants/interview-system.ts`. Be sure to implement the system on both sides - failing to add a case statement will result in the model not responding to messages, while failing to add a constant will result in the model not being selectable either manually or through the randomize button.

### Running CLUE

```bash
npm run build
npm start
```

Open http://localhost:3000 to see the application.

## How to Use

### Step 1: Chat

The application will open to a front page, from which you can continue to the chat session. There, you can either choose a model to speak to from the drop-down selector, or use the dice button to select one randomly.

Once you've chosen a model, start chatting by sending a message about whatever you like. After you've begun your chat, the model selection will freeze, so that you can't change models in the middle of a conversation.

After speaking with the model for a short time, you'll be able to click a continue button below the chat box. This will direct you to the interview page.

### Step 2: Be Interviewed

When you arrive on the interview page, the interviewer will open a conversation and ask you questions about your prior conversation. Allow the interviewing model to guide the conversation - it has a specific system prompt instructing it on how to do so, which can be viewed in `src/utils/constants/interview-system.ts`.

After the interviewer has finished speaking with you, click the download button to save a JSON log of your conversations. Please keep these in the `insighter/logs` folder, as the insighter portion of CLUE expects logs to be found there.

### Step 3: Repeat

Go through the above steps multiple times - perhaps with different models, or asking some friends to speak with the models - as CLUE-Insighter requires multiple logs to run properly. We recommend a minimum of 15 lengthy conversation logs, but the more the better!

### Step 4: Insighter

Once you hae enough log files, you can run the insighter. To do so, enter the insighter folder through your terminal and run `main.py`. Be sure that you've copied your environment file to this folder as well as installed the dependencies from `requirements.txt` before you do so!

`main.py` will go through the following steps, in sequence:

1. Compile conversations into one file.
2. Decide which logs have enough interaction between the user and models to be useful for its analysis and split the filtered logs into chat and interview logs.
3. Compute statistics about the chat and interview logs.
4. Generate dimension classifications of the questions asked and numerical ratings of the opinions expressed by the users in the interview logs.
5. Calculate the average ratings for each dimension per session.
6. Perform topic analyses on the chat sessions
7. Perform topic analyses interview sessions.
8. Create plots of top topics.
9. Create plots of rating correlations.