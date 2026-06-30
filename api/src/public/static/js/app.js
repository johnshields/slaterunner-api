// Uptime Badge updater
async function syncUptime() {
    try {
        const response = await fetch('/api');
        const data = await response.json();

        if (data.uptime_seconds !== undefined) {
            document.getElementById('uptime-badge').textContent =
                `Uptime: ${data.uptime_seconds}s`;
        }
    } catch {
        document.getElementById('uptime-badge').textContent = 'Uptime: error';
    }
}

// JSON syntax highlighter for endpoint responses
function syntaxHighlight(json) {
    if (typeof json !== 'string') {
        json = JSON.stringify(json, null, 2);
    }
    json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    return json.replace(
        /("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g,
        match => {
            let cls = 'json-number';
            if (/^"/.test(match)) {
                cls = /:$/.test(match) ? 'json-key' : 'json-string';
            } else if (/true|false/.test(match)) {
                cls = 'json-boolean';
            } else if (/null/.test(match)) {
                cls = 'json-null';
            }
            return `<span class="${cls}">${match}</span>`;
        }
    );
}

// Endpoint status loader
async function showEndpointStatus(endpoint, resultId, headerId) {
    const resultDiv = document.getElementById(resultId);
    const header = document.getElementById(headerId);

    try {
        header.style.display = 'block';
        resultDiv.innerHTML = 'Loading...';
        resultDiv.style.display = 'block';

        const response = await fetch(endpoint);
        const data = await response.json();

        resultDiv.innerHTML = syntaxHighlight(data);
    } catch (error) {
        resultDiv.textContent = `Error: ${error.message}`;
        resultDiv.style.display = 'block';
    }
}

// Shortcuts for /api endpoint
const showApiStatus    = () => showEndpointStatus('/api', 'api-result', 'api-header');

// Toggle expand/collapse for sections
function toggleSection(id) {
    const el = document.getElementById(id);
    el.style.display = (el.style.display === 'none') ? 'block' : 'none';
}

// Run uptime once on load, then refresh every 30 seconds
document.addEventListener('DOMContentLoaded', () => {
    syncUptime();
    setInterval(syncUptime, 30000);
});
