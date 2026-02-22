document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('analysisForm');
    const runBtn = document.getElementById('runBtn');
    const btnText = document.querySelector('.btn-text');
    const btnLoader = document.getElementById('btnLoader');
    const reportContainer = document.getElementById('reportContainer');
    const reportStatus = document.getElementById('reportStatus');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // 1. Get values
        const objective = document.getElementById('objective').value;
        const horizon = document.getElementById('horizon').value;
        const risk = document.getElementById('risk').value;
        const query = document.getElementById('query').value;

        // 2. Loading State UI
        btnText.style.display = 'none';
        btnLoader.style.display = 'block';
        runBtn.disabled = true;

        reportStatus.textContent = "Processing logic & querying graph...";
        reportStatus.className = "status-badge";
        reportContainer.innerHTML = `
            <div class="empty-state">
                <div class="loader-spinner" style="width: 40px; height: 40px; border-width: 3px; margin-bottom: 20px; border-top-color: var(--accent-primary);"></div>
                <p>Orchestrating M&A Deal Analysis...</p>
                <p style="font-size: 0.8rem; color: var(--text-muted); margin-top: 10px;">Graph Retrieval -> Synergy Models -> LLM Synthesis -> Output Validation</p>
            </div>
        `;

        try {
            // 3. Make API Call
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: query,
                    objective: objective,
                    horizon: parseInt(horizon),
                    risk: risk
                })
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'API request failed');
            }

            const data = await response.json();

            // 4. Update UI with Results
            if (data.status === "success") {
                reportStatus.textContent = "VERIFIED (Node Traceable)";
                reportStatus.className = "status-badge verified";
            } else {
                reportStatus.textContent = "VALIDATION FAILED (No Citations)";
                reportStatus.className = "status-badge failed";
            }

            // Render Markdown
            reportContainer.innerHTML = `<div class="markdown-body">${marked.parse(data.markdown_report)}</div>`;

        } catch (error) {
            console.error('Analysis error:', error);
            reportStatus.textContent = "SYSTEM ERROR";
            reportStatus.className = "status-badge failed";
            reportContainer.innerHTML = `
                <div class="empty-state" style="color: var(--danger);">
                    <div class="empty-icon" style="opacity: 1;">⚠️</div>
                    <h3>Execution Failed</h3>
                    <p style="margin-top: 10px;">${error.message}</p>
                    <p style="font-size: 0.8rem; color: var(--text-muted); margin-top: 10px;">Check your Ollama connection or Neo4j settings.</p>
                </div>
            `;
        } finally {
            // Restore button
            btnText.style.display = 'block';
            btnLoader.style.display = 'none';
            runBtn.disabled = false;
        }
    });
});
