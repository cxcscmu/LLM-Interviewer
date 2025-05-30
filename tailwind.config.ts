import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "gradient-conic":
          "conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))",
      },
      colors: {
        blue: {
          500: "#2F80ED",
        },
      },
      boxShadow: {
        inner: "inset 4px 6px 6px -1px rgb(0 0 0 / 0.2)",
        round: "inset 2px 3px 4px -1px rgb(200 200 200 / 0.5)",
        md: "2px 4px 4px -1px rgb(0 0 0 / 0.4)",
      },
    },
  },
  plugins: [require("@tailwindcss/typography")],
};
export default config;
