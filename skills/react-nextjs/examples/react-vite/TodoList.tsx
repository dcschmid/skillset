// react-vite example — typed SPA feature (Vite + React 19 + TS strict).
// Idioms: derived state in render (no effect-copy), effect with cleanup for
// an external system, custom hook as the reuse unit. No Next.js idioms here.

import { useEffect, useMemo, useState } from "react";

export type Todo = { id: string; title: string; done: boolean };
export type Filter = "all" | "open" | "done";

// Storage read: unknown first, validate, typed out (typescript.md).
function readTodos(raw: string | null): Todo[] {
  if (!raw) return [];
  try {
    const parsed: unknown = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return parsed.filter(
      (t): t is Todo =>
        typeof t === "object" && t !== null &&
        typeof (t as Todo).id === "string" &&
        typeof (t as Todo).title === "string" &&
        typeof (t as Todo).done === "boolean",
    );
  } catch {
    return [];
  }
}

// Custom hook = the reuse boundary (react-core.md).
export function useTodos(storageKey = "todos") {
  const [todos, setTodos] = useState<Todo[]>(() =>
    readTodos(localStorage.getItem(storageKey)),
  );

  // External system (localStorage) sync: effect + cleanup honoring re-runs.
  useEffect(() => {
    const id = setTimeout(() => localStorage.setItem(storageKey, JSON.stringify(todos)), 200);
    return () => clearTimeout(id);
  }, [todos, storageKey]);

  const add = (title: string) =>
    setTodos((prev) => [...prev, { id: crypto.randomUUID(), title, done: false }]);
  const toggle = (id: string) =>
    setTodos((prev) => prev.map((t) => (t.id === id ? { ...t, done: !t.done } : t)));

  return { todos, add, toggle };
}

// Derived data during render — NOT useState+useEffect (react-core.md table).
export function TodoList({ todos, filter }: { todos: Todo[]; filter: Filter }) {
  const visible = useMemo(
    () => todos.filter((t) => (filter === "open" ? !t.done : filter === "done" ? t.done : true)),
    [todos, filter],
  );
  return (
    <ul>
      {visible.map((t) => (
        <li key={t.id}>{t.title}</li>
      ))}
    </ul>
  );
}
