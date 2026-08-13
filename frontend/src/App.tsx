import { useState } from "react";
import { useRouter } from "./router.tsx";
import { Nav } from "./components/Nav.tsx";
import { LearnPanel } from "./components/LearnPanel.tsx";
import { Build } from "./pages/Build.tsx";
import { Overview } from "./pages/Overview.tsx";
import { Train } from "./pages/Train.tsx";
import { Simulator } from "./pages/Simulator.tsx";
import { Success } from "./pages/Success.tsx";
import { Readiness } from "./pages/Readiness.tsx";
import { Learn } from "./pages/Learn.tsx";
import { KnowledgeChecks } from "./pages/KnowledgeChecks.tsx";
import type { Area } from "./api/types";

// Map the current route to a learning "area" so the contextual panel always
// shows guidance relevant to what the learner is doing.
function areaForPath(pathname: string): Area {
  if (pathname.startsWith("/explore")) return "data";
  if (pathname.startsWith("/train")) return "training";
  if (pathname.startsWith("/simulator")) return "predictions";
  if (pathname.startsWith("/success")) return "evaluation";
  if (pathname.startsWith("/readiness")) return "data";
  if (pathname.startsWith("/learn")) return "governance";
  if (pathname.startsWith("/checks")) return "evaluation";
  return "overview";
}

function Page({ path }: { path: string }) {
  if (path.startsWith("/explore")) return <Overview />;
  if (path.startsWith("/train")) return <Train />;
  if (path.startsWith("/simulator")) return <Simulator />;
  if (path.startsWith("/success")) return <Success />;
  if (path.startsWith("/readiness")) return <Readiness />;
  if (path.startsWith("/learn")) return <Learn />;
  if (path.startsWith("/checks")) return <KnowledgeChecks />;
  return <Build />;
}

export default function App() {
  const { path } = useRouter();
  const area = areaForPath(path);
  const [learningOpen, setLearningOpen] = useState(
    () => localStorage.getItem("contextual-learning-open") === "true",
  );

  function toggleLearning() {
    setLearningOpen((isOpen) => {
      localStorage.setItem("contextual-learning-open", String(!isOpen));
      return !isOpen;
    });
  }

  return (
    <div className="app">
      <Nav />
      <div className={`app__body${learningOpen ? " learning-is-open" : ""}`}>
        <main className="content">
          <Page path={path} />
        </main>
        <LearnPanel area={area} isOpen={learningOpen} onToggle={toggleLearning} />
      </div>
    </div>
  );
}
