import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Solaris Energy brand colors
        solaris: {
          primary: "#0066CC", // Energy blue
          secondary: "#00CC66", // Green accent
          dark: "#171616", // Dark text
          gray: {
            light: "#EEEEEE", // Background
            medium: "#CCCCCC",
            dark: "#666666",
          },
        },
      },
      fontFamily: {
        sans: ['"Source Sans Pro"', "sans-serif"],
      },
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "gradient-conic":
          "conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))",
      },
    },
  },
  plugins: [],
};
export default config;
