import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import "@fontsource/space-grotesk/600.css";
import "@fontsource/space-grotesk/700.css";
import App from "./App.tsx";
import { Router } from "./router.tsx";
import { EnvProvider } from "./env.tsx";
import "./styles.css";

const queryClient = new QueryClient({
  defaultOptions: { queries: { staleTime: 60_000, refetchOnWindowFocus: false } },
});

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <Router>
        <EnvProvider>
          <App />
        </EnvProvider>
      </Router>
    </QueryClientProvider>
  </StrictMode>,
);
