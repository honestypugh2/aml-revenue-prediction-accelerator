import { createContext, useContext, useState, type ReactNode } from "react";
import type { EnvName } from "./api/types";

interface EnvContextValue {
  env: EnvName;
  setEnv: (env: EnvName) => void;
}

const EnvContext = createContext<EnvContextValue | undefined>(undefined);

export function EnvProvider({ children }: { children: ReactNode }) {
  const [env, setEnv] = useState<EnvName>("dev");
  return <EnvContext value={{ env, setEnv }}>{children}</EnvContext>;
}

export function useEnv(): EnvContextValue {
  const ctx = useContext(EnvContext);
  if (!ctx) {
    throw new Error("useEnv must be used within an EnvProvider");
  }
  return ctx;
}
