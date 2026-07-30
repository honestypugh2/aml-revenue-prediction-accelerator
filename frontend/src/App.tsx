import { useRouter } from "./router.tsx";
import { Nav } from "./components/Nav.tsx";
import { LearnPanel } from "./components/LearnPanel.tsx";
import { Overview } from "./pages/Overview.tsx";
import { Train } from "./pages/Train.tsx";
import { Learn } from "./pages/Learn.tsx";
import { KnowledgeChecks } from "./pages/KnowledgeChecks.tsx";
import type { Area } from "./api/types";

// Map the current route to a learning "area" so the contextual panel always
// shows guidance relevant to what the learner is doing.
function areaForPath(pathname: string): Area {
  if (pathname.startsWith("/train")) return "training";
  if (pathname.startsWith("/learn")) return "governance";
  if (pathname.startsWith("/checks")) return "evaluation";
  return "overview";
}

function Page({ path }: { path: string }) {
  if (path.startsWith("/train")) return <Train />;
  if (path.startsWith("/learn")) return <Learn />;
  if (path.startsWith("/checks")) return <KnowledgeChecks />;
  return <Overview />;
}

export default function App() {
  const { path } = useRouter();
  const area = areaForPath(path);

  return (
    <div className="app">
      <Nav />
      <div className="app__body">
        <main className="content">
          <Page path={path} />
        </main>
        <LearnPanel area={area} />
      </div>
    </div>
  );
}
