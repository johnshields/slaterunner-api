/**
 * DOM helpers
 * Side-effecting browser utilities.
 */

export function icons() {
  if (window.lucide) window.lucide.createIcons();
}

export function toast(message, type = "success") {
  const el = document.createElement("div");
  el.className = `toast toast-${type}`;
  el.textContent = message;
  document.body.appendChild(el);
  requestAnimationFrame(() => el.classList.add("show"));
  setTimeout(() => {
    el.classList.remove("show");
    setTimeout(() => el.remove(), 300);
  }, 2200);
}
