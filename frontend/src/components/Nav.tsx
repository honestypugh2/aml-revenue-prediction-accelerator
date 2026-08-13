import { useEffect, useState } from "react";
import { NavLink } from "../router.tsx";
import { useRouter } from "../router.tsx";
import { useEnv } from "../env.tsx";
import type { EnvName } from "../api/types";

const NAV_GROUPS = [
  {
    label: "Workflow",
    links: [
      { to: "/", label: "Build", end: true },
      { to: "/explore", label: "Explore" },
      { to: "/train", label: "Train" },
      { to: "/simulator", label: "Simulate" },
    ],
  },
  {
    label: "Learn & govern",
    links: [
      { to: "/success", label: "Success" },
      { to: "/readiness", label: "Readiness" },
      { to: "/learn", label: "Lessons" },
      { to: "/checks", label: "Checks" },
    ],
  },
];

export function Nav() {
  const { env, setEnv } = useEnv();
  const { path } = useRouter();
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => setMenuOpen(false), [path]);

  useEffect(() => {
    if (!menuOpen) return;
    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") setMenuOpen(false);
    };
    window.addEventListener("keydown", closeOnEscape);
    return () => window.removeEventListener("keydown", closeOnEscape);
  }, [menuOpen]);

  return (
    <nav className="nav" aria-label="Primary">
      <div className="nav__top">
        <div className="nav__brand">
          <span className="nav__logo" aria-hidden>
            ◆
          </span>
          <span>
            Revenue Prediction <span className="nav__brand-accent">Accelerator</span>
          </span>
        </div>
        <button
          type="button"
          className="nav__toggle"
          aria-expanded={menuOpen}
          aria-controls="primary-navigation-menu"
          aria-label={menuOpen ? "Close navigation menu" : "Open navigation menu"}
          onClick={() => setMenuOpen((open) => !open)}
        >
          <span aria-hidden>{menuOpen ? "×" : "☰"}</span>
        </button>
      </div>

      <div id="primary-navigation-menu" className={`nav__drawer ${menuOpen ? "is-open" : ""}`}>
        {NAV_GROUPS.map((group) => (
          <div className="nav__group" key={group.label}>
            <span className="nav__group-label">{group.label}</span>
            <ul className="nav__links">
              {group.links.map((link) => (
                <li key={link.to}>
                  <NavLink
                    to={link.to}
                    end={link.end}
                    className={(active) => (active ? "active" : "")}
                  >
                    {link.label}
                  </NavLink>
                </li>
              ))}
            </ul>
          </div>
        ))}

        <label className="nav__env">
          <span>Environment</span>
          <select value={env} onChange={(e) => setEnv(e.target.value as EnvName)}>
            <option value="dev">dev</option>
            <option value="test">test</option>
            <option value="prod">prod</option>
          </select>
        </label>
      </div>
    </nav>
  );
}
