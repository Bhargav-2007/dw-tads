export const shortcuts = [
  ["Ctrl / Cmd + K", "Open command palette"],
  ["/", "Search actors"],
  ["F", "Toggle focus mode"],
  ["Esc", "Close dialog / leave focus mode"],
  ["↑ / ↓", "Navigate results"],
  ["Enter", "Open selected result"],
  ["?", "Keyboard help"],
];
export const isEditing = (target: EventTarget | null) =>
  target instanceof HTMLElement &&
  (target.isContentEditable ||
    Boolean(target.closest('input,textarea,select,[role="dialog"]')));
