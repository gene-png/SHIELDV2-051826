import type { Config } from "tailwindcss";

// SHIELD design tokens — sourced from reference-docs/SHIELDv2_Design_Mockup.html
// USWDS-aligned palette. Self-hosted, no CDN (Master Spec §4).
const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "../../packages/design-system/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: "#1B3A5B",
        "gov-blue": "#005EA2",
        success: "#2E7D32",
        warning: "#F57C00",
        danger: "#C62828",
        accent: "#6F42C1",
        n: {
          50: "#F8FAFC",
          100: "#F1F5F9",
          200: "#E2E8F0",
          300: "#CBD5E1",
          400: "#94A3B8",
          500: "#64748B",
          600: "#475569",
          700: "#334155",
          800: "#1E293B",
          900: "#0F172A",
        },
      },
      fontFamily: {
        sans: [
          "-apple-system",
          "BlinkMacSystemFont",
          '"Segoe UI"',
          "Inter",
          '"Source Sans Pro"',
          "system-ui",
          "sans-serif",
        ],
      },
      borderRadius: {
        card: "8px",
        control: "6px",
        pill: "12px",
      },
      boxShadow: {
        card: "0 1px 2px rgba(15,23,42,0.04), 0 2px 4px rgba(15,23,42,0.03)",
      },
    },
  },
  plugins: [],
};

export default config;
