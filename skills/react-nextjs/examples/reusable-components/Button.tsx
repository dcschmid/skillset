// reusable-components — composition over configuration (react-core.md,
// styling-design-systems.md). Variants as data; slots over boolean props;
// tokens, not hex; tokens live in one CSS file (styling module idiom).

import type { ReactNode } from "react";

// Variant maps beat prop multiplication (react-core.md composition rule).
const toneClass = {
  neutral: "btn btn--neutral",
  accent: "btn btn--accent",
} as const;

export type ButtonProps = {
  tone?: keyof typeof toneClass;
  children: ReactNode;
  onClick?: () => void;
  disabled?: boolean;
};

// Presentation-pure leaf: no fetching, no store imports (architecture.md).
export function Button({ tone = "neutral", onClick, disabled, children }: ButtonProps) {
  return (
    <button type="button" onClick={onClick} disabled={disabled} className={toneClass[tone]}>
      {children}
    </button>
  );
}

// Composition: Card accepts named slots via children patterns instead of
// twelve props. Consumer assembles; Card owns the frame only.
export function Card({ children }: { children: ReactNode }) {
  return <div className="card">{children}</div>;
}
export function CardHeader({ title, actions }: { title: ReactNode; actions?: ReactNode }) {
  return (
    <header className="card__header">
      <h3>{title}</h3>
      {actions}
    </header>
  );
}

/* tokens.css (the portable layer, styling-design-systems.md):
   .btn { padding: var(--space-2) var(--space-4); border-radius: var(--radius-sm); }
   .btn--neutral { background: var(--color-surface); color: var(--color-ink); }
   .btn--accent  { background: var(--color-accent); color: var(--color-on-accent); }
   focus + disabled + reduced-motion states ship with the token file. */
