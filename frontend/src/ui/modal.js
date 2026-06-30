import { icons } from "../utils.js";
import { modalTemplate } from "../templates/modal.js";

/**
 * Modal
 * Owns the overlay DOM lifecycle: mount, dismiss (close button, cancel,
 * overlay click, Escape) and the inline error line.
 */
export class Modal {
  #escHandler = (e) => {
    if (e.key === "Escape") this.close();
  };

  open({ title, body, confirmLabel, danger = false, onConfirm }) {
    this.close();

    const root = document.createElement("div");
    root.id = "modal-root";
    root.innerHTML = modalTemplate({ title, body, confirmLabel, danger });
    document.body.appendChild(root);
    icons();

    const overlay = document.querySelector("#modal-overlay");
    overlay.addEventListener("click", (e) => {
      if (e.target === overlay) this.close();
    });
    document.querySelector("#modal-close").addEventListener("click", () => this.close());
    document.querySelector("#modal-cancel").addEventListener("click", () => this.close());
    document.querySelector("#modal-confirm").addEventListener("click", () => onConfirm?.());
    document.addEventListener("keydown", this.#escHandler);
  }

  close() {
    document.removeEventListener("keydown", this.#escHandler);
    document.querySelector("#modal-root")?.remove();
  }

  setError(message) {
    const el = document.querySelector("#modal-error");
    if (el) el.textContent = message;
  }

  get body() {
    return document.querySelector(".modal-body");
  }
}
