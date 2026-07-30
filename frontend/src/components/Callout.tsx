import type { ReactNode } from "react";

type CalloutKind = "info" | "warn" | "success";

// A small inline learning callout used within pages to explain what the learner
// is seeing at the exact moment they see it.
export function Callout({
  kind = "info",
  title,
  children,
}: {
  kind?: CalloutKind;
  title: string;
  children: ReactNode;
}) {
  return (
    <div className={`callout callout--${kind}`} role="note">
      <div className="callout__title">{title}</div>
      <div className="callout__body">{children}</div>
    </div>
  );
}
