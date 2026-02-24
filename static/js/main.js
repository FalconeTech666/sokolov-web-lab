document.addEventListener('DOMContentLoaded', () => {
    const toggleBtn = document.getElementById('theme-toggle');
    const htmlElement = document.documentElement;

    if (toggleBtn) { 
        toggleBtn.addEventListener('click', () => {
            const currentTheme = htmlElement.getAttribute('data-theme') || 'light';
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

            htmlElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
        });
    }
});

const FASTAPI_BASE = '/fastapi';

async function handleApiCall(resultContainerId, method, endpoint, payload = null) {
    const resultContainer = document.getElementById(resultContainerId);
    if (!resultContainer) return;
    
    resultContainer.innerHTML = 'Загрузка...';
    
    try {
        const options = {
            method: method,
            headers: { 'Content-Type': 'application/json' }
        };
        if (payload && (method === 'POST' || method === 'PUT')) {
            options.body = typeof payload === 'string' ? payload : JSON.stringify(payload);
        }
        
        const response = await fetch(`${FASTAPI_BASE}${endpoint}`, options);
        let data;
        
        const contentType = response.headers.get("content-type");
        if (contentType && contentType.includes("application/json")) {
            data = await response.json();
        } else {
            data = await response.text();
        }
        
        const statusClass = response.ok ? 'status-ok' : 'status-error';
        
        resultContainer.innerHTML = `
            <div class="api-status ${statusClass}">HTTP ${response.status}</div>
            <pre style="white-space: pre-wrap; word-wrap: break-word; margin: 0;"><code>${JSON.stringify(data, null, 2)}</code></pre>
        `;
    } catch (error) {
        resultContainer.innerHTML = `
            <div class="api-status status-error">Ошибка сети</div>
            <pre><code>${error.message}</code></pre>
        `;
    }
}