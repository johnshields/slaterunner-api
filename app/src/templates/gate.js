/**
 * Login gate
 * Token prompt shown until a valid token is entered.
 * Uses the SlateRunner header/badge/panel language.
 */
export function gateTemplate() {
  return `
    <div class="login-wrapper">
      <div class="login-card">
        <h1>SlateRunner</h1>
        <p class="login-tagline">RESTful FastAPI for fixing it in post.</p>
        <div class="login-error" id="gate-error">Invalid token</div>
        <input type="password" id="gate-input" spellcheck="false" autocomplete="off" />
        <button class="gate-exec" type="button" id="gate-exec">
          <i data-lucide="terminal"></i> Login
        </button>
      </div>
    </div>
  `;
}
