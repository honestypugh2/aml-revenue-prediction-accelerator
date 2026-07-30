import { NavLink } from "../router.tsx";
import { useEnv } from "../env.tsx";
import type { EnvName } from "../api/types";

const LINKS = [
  { to: "/", label: "Overview", end: true },
  { to: "/train", label: "Train & Compare" },
  { to: "/learn", label: "Learn" },
  { to: "/checks", label: "Knowledge Checks" },
];

export function Nav() {
  const { env, setEnv } = useEnv();
  return (
    <nav className="nav" aria-label="Primary">
      <div className="nav__brand">
        <span className="nav__logo" aria-hidden>
          ◆
        </span>
        <span>Revenue Prediction Accelerator</span>
      </div>

      <ul className="nav__links">
        {LINKS.map((l) => (
          <li key={l.to}>
            <NavLink to={l.to} end={l.end} className={(active) => (active ? "active" : "")}>
              {l.label}
            </NavLink>
          </li>
        ))}
      </ul>

      <label className="nav__env">
        <span>Environment</span>
        <select value={env} onChange={(e) => setEnv(e.target.value as EnvName)}>
          <option value="dev">dev</option>
          <option value="test">test</option>
          <option value="prod">prod</option>
        </select>
      </label>
    </nav>
  );
}
