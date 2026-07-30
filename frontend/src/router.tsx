// Tiny dependency-free hash router for this SPA. Hash routing needs no server
// fallback (the browser only ever requests "/"), and removes the react-router
// dependency entirely.
import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";

function currentPath(): string {
  const hash = window.location.hash.replace(/^#/, "");
  return hash.length > 0 ? hash : "/";
}

interface RouterValue {
  path: string;
  navigate: (to: string) => void;
}

const RouterContext = createContext<RouterValue | undefined>(undefined);

export function Router({ children }: { children: ReactNode }) {
  const [path, setPath] = useState<string>(currentPath);

  useEffect(() => {
    const onHashChange = () => setPath(currentPath());
    window.addEventListener("hashchange", onHashChange);
    return () => window.removeEventListener("hashchange", onHashChange);
  }, []);

  const navigate = (to: string) => {
    window.location.hash = to;
  };

  return <RouterContext value={{ path, navigate }}>{children}</RouterContext>;
}

export function useRouter(): RouterValue {
  const ctx = useContext(RouterContext);
  if (!ctx) {
    throw new Error("useRouter must be used within <Router>");
  }
  return ctx;
}

function isActive(path: string, to: string, end: boolean): boolean {
  return end ? path === to : path === to || path.startsWith(`${to}/`);
}

export function NavLink({
  to,
  end = false,
  className,
  children,
}: {
  to: string;
  end?: boolean;
  className?: (active: boolean) => string;
  children: ReactNode;
}) {
  const { path } = useRouter();
  const active = isActive(path, to, end);
  return (
    <a href={`#${to}`} className={className ? className(active) : undefined}>
      {children}
    </a>
  );
}
