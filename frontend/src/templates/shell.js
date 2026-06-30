/**
 * Static app shell markup
 * Dynamic regions (#nav-rail, #record-list, #detail-pane) are filled by the
 * controller after mount.
 */
export function shellTemplate() {
  return `
    <div class="topbar">
      <span class="logo">SlateRunner</span>
      <div class="meta">
        <span class="badge" id="version-badge">v--</span>
        <span class="badge" id="uptime-badge">Uptime: --</span>
        <button class="btn-icon" id="logout" title="Lock"><i data-lucide="log-out"></i></button>
      </div>
    </div>
    <div class="body">
      <div class="nav-rail" id="nav-rail"></div>
      <div class="list-pane">
        <div class="list-header">
          <span id="list-count">--</span>
          <div class="list-actions">
            <button class="btn-icon" id="page-prev" title="Previous page"><i data-lucide="chevron-left"></i></button>
            <button class="btn-icon" id="page-next" title="Next page"><i data-lucide="chevron-right"></i></button>
            <button class="btn-icon" id="refresh" title="Refresh"><i data-lucide="refresh-cw"></i></button>
          </div>
        </div>
        <div id="record-list"></div>
      </div>
      <div class="detail-pane" id="detail-pane"></div>
    </div>
  `;
}
