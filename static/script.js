document.addEventListener('DOMContentLoaded', () => {

    // ── State ────────────────────────────────────────────────────────────────
    let selectedDealType = 'acquisition';
    let companyAText = '';
    let companyBText = '';
    let currentReports = {};
    let activeTab = 'risk_analysis';

    // ── Navigation (view switching) ───────────────────────────────────────────
    const views = { analysis: 'view-analysis', graph: 'view-graph', risk: 'view-risk' };
    const viewTitles = {
        analysis: 'Deal Analysis Engine',
        graph: 'Knowledge Graph',
        risk: 'Risk Models',
    };

    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const target = item.dataset.view;
            document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
            item.classList.add('active');
            Object.values(views).forEach(id => {
                document.getElementById(id).style.display = 'none';
            });
            document.getElementById(views[target]).style.display = '';
            document.getElementById('viewTitle').textContent = viewTitles[target];
        });
    });

    // ── Deal Type Toggle ──────────────────────────────────────────────────────
    function updateRoleTags(type) {
        const tagA = document.getElementById('roleTagA');
        const tagB = document.getElementById('roleTagB');
        if (type === 'merger') {
            tagA.textContent = 'Merger Company';
            tagB.textContent = 'Merger Company';
            tagA.className = 'role-tag role-merger';
            tagB.className = 'role-tag role-merger';
        } else {
            tagA.textContent = 'Acquirer';
            tagB.textContent = 'Acquiree';
            tagA.className = 'role-tag role-acquirer';
            tagB.className = 'role-tag role-acquiree';
        }
    }

    document.querySelectorAll('.deal-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            selectedDealType = btn.dataset.type;
            document.querySelectorAll('.deal-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            updateRoleTags(selectedDealType);
        });
    });

    // Set initial role tags
    updateRoleTags('acquisition');

    // ── File Upload Logic ─────────────────────────────────────────────────────
    function setupUpload(company) {
        const fileInput = document.getElementById(`fileInput${company}`);
        const uploadBtn = document.getElementById(`uploadBtn${company}`);
        const spinner = document.getElementById(`spinner${company}`);
        const statusEl = document.getElementById(`status${company}`);
        const fileNameEl = document.getElementById(`fileName${company}`);
        const dropZone = document.getElementById(`dropZone${company}`);

        fileInput.addEventListener('change', () => {
            const file = fileInput.files[0];
            if (file) {
                fileNameEl.textContent = file.name;
                uploadBtn.disabled = false;
                dropZone.classList.add('has-file');
                statusEl.textContent = '';
                statusEl.className = 'upload-status';
            }
        });

        dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('drag-over'); });
        dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('drag-over');
            if (e.dataTransfer?.files.length) {
                fileInput.files = e.dataTransfer.files;
                fileInput.dispatchEvent(new Event('change'));
            }
        });

        uploadBtn.addEventListener('click', async () => {
            const file = fileInput.files[0];
            if (!file) return;
            const btnTextEl = uploadBtn.querySelector('.btn-text');
            btnTextEl.style.display = 'none';
            spinner.style.display = 'block';
            uploadBtn.disabled = true;
            statusEl.textContent = 'Extracting text…';
            statusEl.className = 'upload-status extracting';

            const formData = new FormData();
            formData.append('company', company.toLowerCase());
            formData.append('file', file);

            try {
                const res = await fetch('/api/upload-docs', { method: 'POST', body: formData });
                if (!res.ok) { const e = await res.json(); throw new Error(e.detail || 'Upload failed'); }
                const data = await res.json();
                if (company === 'A') companyAText = data.extracted_text;
                else companyBText = data.extracted_text;
                statusEl.innerHTML = `✅ Extracted <strong>${data.char_count.toLocaleString()}</strong> chars`;
                statusEl.className = 'upload-status success';
                dropZone.classList.add('uploaded');
            } catch (err) {
                statusEl.textContent = `❌ ${err.message}`;
                statusEl.className = 'upload-status error';
                uploadBtn.disabled = false;
            } finally {
                btnTextEl.style.display = 'block';
                spinner.style.display = 'none';
            }
        });
    }

    setupUpload('A');
    setupUpload('B');

    // ── Report Tabs ───────────────────────────────────────────────────────────
    function initTabs() {
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                activeTab = btn.dataset.tab;
                document.querySelectorAll('.tab-btn').forEach(b => b.classList.toggle('active', b === btn));
                renderActiveReport();
            });
        });
    }

    function renderActiveReport() {
        const content = currentReports[activeTab];
        if (content) {
            document.getElementById('reportContainer').innerHTML =
                `<div class="markdown-body">${marked.parse(content)}</div>`;
        }
    }

    // ── Analysis Form ─────────────────────────────────────────────────────────
    document.getElementById('analysisForm').addEventListener('submit', async (e) => {
        e.preventDefault();

        // Collect checked objectives
        const checkedObjectives = [...document.querySelectorAll('input[name="objective"]:checked')]
            .map(cb => cb.value);
        if (checkedObjectives.length === 0) {
            alert('Please select at least one Strategic Objective.');
            return;
        }
        const objectiveStr = checkedObjectives.join(', ');

        const horizon = document.getElementById('horizon').value;
        const risk = document.getElementById('risk').value;
        const query = document.getElementById('query').value;

        const companyNameA = document.getElementById('companyNameA').value.trim() || 'Company A';
        const companyNameB = document.getElementById('companyNameB').value.trim() || 'Company B';

        const roleA = selectedDealType === 'merger' ? 'Merger Company' : 'Acquirer';
        const roleB = selectedDealType === 'merger' ? 'Merger Company' : 'Acquiree';

        // Loading state
        const runBtn = document.getElementById('runBtn');
        const btnText = runBtn.querySelector('.btn-text');
        const btnLoader = document.getElementById('btnLoader');
        btnText.style.display = 'none';
        btnLoader.style.display = 'block';
        runBtn.disabled = true;

        const reportTabs = document.getElementById('reportTabs');
        reportTabs.style.display = 'none';

        const reportStatus = document.getElementById('reportStatus');
        const reportContainer = document.getElementById('reportContainer');

        reportStatus.textContent = 'Generating reports…';
        reportStatus.className = 'status-badge';
        reportContainer.innerHTML = `
            <div class="empty-state">
                <div class="loader-spinner" style="width:40px;height:40px;border-width:3px;margin-bottom:20px;border-top-color:var(--accent-primary);"></div>
                <p>Orchestrating ${selectedDealType.charAt(0).toUpperCase() + selectedDealType.slice(1)} Analysis…</p>
                <p style="font-size:0.8rem;color:var(--text-muted);margin-top:10px;">
                    ${companyNameA} (${roleA}) &nbsp;↔&nbsp; ${companyNameB} (${roleB})
                </p>
                <p style="font-size:0.75rem;color:var(--text-muted);margin-top:6px;">
                    Document Parsing → Graph Retrieval → LLM × 4 Reports → Validation
                </p>
            </div>`;

        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    query,
                    objective: objectiveStr,
                    horizon: parseInt(horizon),
                    risk,
                    deal_type: selectedDealType,
                    company_a_name: companyNameA,
                    company_b_name: companyNameB,
                    company_a_role: roleA,
                    company_b_role: roleB,
                    company_a_text: companyAText,
                    company_b_text: companyBText,
                }),
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'API request failed');
            }

            const data = await response.json();
            currentReports = data.reports || {};

            reportTabs.style.display = 'flex';
            initTabs();

            activeTab = 'risk_analysis';
            document.querySelectorAll('.tab-btn').forEach(b =>
                b.classList.toggle('active', b.dataset.tab === activeTab));
            renderActiveReport();

            reportStatus.textContent = data.status === 'success' ? 'ANALYSIS COMPLETE' : 'VALIDATION FAILED';
            reportStatus.className = `status-badge ${data.status === 'success' ? 'verified' : 'failed'}`;

        } catch (error) {
            console.error('Analysis error:', error);
            reportTabs.style.display = 'none';
            reportStatus.textContent = 'SYSTEM ERROR';
            reportStatus.className = 'status-badge failed';
            reportContainer.innerHTML = `
                <div class="empty-state" style="color:var(--danger);">
                    <div class="empty-icon" style="opacity:1;">⚠️</div>
                    <h3>Execution Failed</h3>
                    <p style="margin-top:10px;">${error.message}</p>
                    <p style="font-size:0.8rem;color:var(--text-muted);margin-top:10px;">Check your Ollama connection or Neo4j settings.</p>
                </div>`;
        } finally {
            btnText.style.display = 'block';
            btnLoader.style.display = 'none';
            runBtn.disabled = false;
        }
    });
});
