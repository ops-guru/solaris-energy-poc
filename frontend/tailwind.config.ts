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
          background: "#eeeeee",
          surface: "#f9f8f4",
          card: "#ffffff",
          charcoal: "#171616",
          accent: "#414345",
          accentLight: "#939393",
          border: "#d6d6d6",
          user: "#3d5360",
        },
        opsguru: {
          background: "#02091c",
          surface: "#08152e",
          panel: "#0c1f41",
          card: "#132952",
          border: "rgba(255,255,255,0.18)",
          accent: "#6ce8ff",
          accentAlt: "#8df4ff",
          user: "#1b3e7a",
          text: "#f4f7ff",
          muted: "#c2d6ff",
        },
      },
      fontFamily: {
        sans: ["var(--font-body)", "sans-serif"],
        display: ["var(--font-heading)", "sans-serif"],
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
