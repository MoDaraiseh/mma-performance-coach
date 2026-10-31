import { useEffect, useRef } from "react";

export function useDialog(open: boolean, onClose: () => void) {
  const ref = useRef<HTMLElement>(null);
  const close = useRef(onClose);
  close.current = onClose;
  useEffect(() => {
    if (!open || !ref.current) return;
    const previous = document.activeElement as HTMLElement | null;
    const selector =
      'button:not(:disabled), input:not(:disabled), select:not(:disabled), textarea:not(:disabled), a[href], summary, [tabindex="0"]';
    const dialog = ref.current;
    const inactive: { element: HTMLElement; inert: boolean }[] = [];
    let current: HTMLElement = dialog;
    while (current.parentElement && current !== document.body) {
      for (const sibling of current.parentElement.children) {
        if (
          sibling instanceof HTMLElement &&
          sibling !== current &&
          !["SCRIPT", "STYLE", "LINK"].includes(sibling.tagName)
        ) {
          inactive.push({ element: sibling, inert: Boolean(sibling.inert) });
          sibling.inert = true;
        }
      }
      current = current.parentElement;
    }
    dialog.querySelector<HTMLElement>(selector)?.focus();
    const keydown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.preventDefault();
        close.current();
      }
      if (e.key !== "Tab") return;
      const controls = [...dialog.querySelectorAll<HTMLElement>(selector)];
      const first = controls[0],
        last = controls.at(-1);
      if (
        e.shiftKey &&
        (document.activeElement === first ||
          !dialog.contains(document.activeElement))
      ) {
        e.preventDefault();
        last?.focus();
      } else if (
        !e.shiftKey &&
        (document.activeElement === last ||
          !dialog.contains(document.activeElement))
      ) {
        e.preventDefault();
        first?.focus();
      }
    };
    document.addEventListener("keydown", keydown);
    const overflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", keydown);
      document.body.style.overflow = overflow;
      inactive.forEach(({ element, inert }) => {
        element.inert = inert;
      });
      previous?.focus();
    };
  }, [open]);
  return ref;
}
