import type { AstroIntegration } from "astro";

export function mermaid(): AstroIntegration {
  return {
    name: "moonin-mermaid",
    hooks: {
      "astro:config:setup": ({ injectScript }) => {
        injectScript("page", 'import "/src/scripts/mermaid-client.ts";');
      },
    },
  };
}