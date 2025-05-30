export default (phase, { defaultConfig }) => {
  const env = process.env.NODE_ENV;
  /**
   * @type {import("next").NextConfig}
   */
  if (env === "production") {
    return {
      // output: "export",
      // assetPrefix: `/ccohen2/clue_llm/ui`,
      // basePath: `/ccohen2/clue_llm/ui`,
      // distDir: "../ui",
    };
  } else {
    return {
      async rewrites() {
        return [
          {
            source: "/query",
            destination: "http://localhost:8080/query", // Proxy to Backend
          },
        ];
      },
    };
  }
};
