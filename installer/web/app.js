// Shut The Front Door! - Installer JavaScript
// Handles the frontend logic for the browser-based installer

class InstallerApp {
    constructor() {
        this.currentScreen = 'welcome-screen';
        this.config = {};
        this.modules = [];
        this.deploymentStatus = {};
        this.isoPollingInterval = null;
        this.selectedISOsNeeded = [];
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadConfig();
        this.loadModules();
        this.updateStatusBar('Ready to start');
        
        // Hash routing: restore screen from URL hash on load
        const validScreens = ['ai-setup-screen', 'interview-screen', 'iso-screen', 'deployment-screen', 'completion-screen'];
        const hash = window.location.hash.replace('#', '');
        if (validScreens.includes(hash)) {
            this.showScreen(hash);
            if (hash === 'ai-setup-screen') this.checkAISetup();
            if (hash === 'iso-screen') this.loadISOs();
        }
    }
    
    bindEvents() {
        // Navigation buttons
        document.getElementById('start-setup')?.addEventListener('click', () => this.checkAISetup());
        document.getElementById('start-ai-setup')?.addEventListener('click', () => this.startAIProvisioning());
        document.getElementById('skip-ai-setup')?.addEventListener('click', () => {
            if (this.aiPollingInterval) clearInterval(this.aiPollingInterval);
            this.showScreen('interview-screen');
        });
        document.getElementById('back-welcome')?.addEventListener('click', () => this.showScreen('welcome-screen'));
        document.getElementById('save-config')?.addEventListener('click', () => this.saveConfiguration());
        // ISO screen
        document.getElementById('back-to-interview')?.addEventListener('click', () => this.showScreen('interview-screen'));
        document.getElementById('iso-continue')?.addEventListener('click', () => this.showScreen('deployment-screen'));
        document.getElementById('refresh-drives')?.addEventListener('click', () => this.loadUSBDrives());
        document.getElementById('flash-usb-btn')?.addEventListener('click', () => this.flashISO());
        document.getElementById('flash-iso-select')?.addEventListener('change', () => this.updateFlashButton());
        document.getElementById('usb-drive-select')?.addEventListener('change', () => this.updateFlashButton());
        document.getElementById('back-interview')?.addEventListener('click', () => this.showScreen('interview-screen'));
        document.getElementById('start-deployment')?.addEventListener('click', () => this.startDeployment());
        
        // Chat functionality
        document.getElementById('send-chat')?.addEventListener('click', () => this.sendChatMessage());
        document.getElementById('chat-input')?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendChatMessage();
        });
        
        // OS picker filter pills
        document.querySelectorAll('.os-filter-pill').forEach(pill => {
            pill.addEventListener('click', () => this.filterOSCards(pill.dataset.filter, pill));
        });

        // Completion actions
        document.getElementById('download-configs')?.addEventListener('click', () => this.downloadConfigs());
        document.getElementById('view-guide')?.addEventListener('click', () => this.viewGuide());
    }
    
    showScreen(screenId) {
        // Hide all screens
        document.querySelectorAll('.screen').forEach(screen => {
            screen.classList.remove('active');
        });
        
        // Show target screen
        document.getElementById(screenId)?.classList.add('active');
        this.currentScreen = screenId;
        
        // Sync URL hash (skip welcome so the URL stays clean on first load)
        if (screenId !== 'welcome-screen') {
            window.location.hash = screenId;
        } else {
            history.replaceState(null, '', window.location.pathname);
        }
        
        // Update status
        const statusMessages = {
            'welcome-screen': 'Welcome to Shut The Front Door!',
            'ai-setup-screen': 'Setting up AI assistant',
            'interview-screen': 'Configuring your privacy network',
            'iso-screen': 'Hardware provisioning',
            'deployment-screen': 'Deploying services',
            'completion-screen': 'Installation complete'
        };
        
        if (screenId === 'iso-screen') this.loadISOs();
        
        this.updateStatusBar(statusMessages[screenId] || 'Ready');
    }
    
    async checkAISetup() {
        try {
            const response = await fetch('/api/ai/status');
            if (response.ok) {
                const status = await response.json();
                if (status.status === 'success' || status.status === 'ready') {
                    // AI is ready, skip straight to interview
                    this.showScreen('interview-screen');
                } else if (status.status === 'running') {
                    // Already running
                    this.showScreen('ai-setup-screen');
                    this.monitorAIPolling();
                } else {
                    // idle or error
                    this.showScreen('ai-setup-screen');
                    
                    // Display hardware info if available
                    if (status.hardware) {
                        const hw = status.hardware;
                        const hwText = document.getElementById('ai-hardware-info');
                        if (hwText) {
                            if (hw.tier === 'fallback') {
                                hwText.innerHTML = `⚠️ Your system doesn't meet the requirements for local AI (${hw.memory_gb}GB RAM). We recommend skipping this step.`;
                            } else {
                                hwText.innerHTML = `System check passed: <strong>${hw.memory_gb}GB RAM</strong>. <br>Recommended Model: <strong>${hw.model}</strong>`;
                            }
                        }
                    }
                }
            } else {
                this.showScreen('interview-screen'); // Fallback if API fails
            }
        } catch (error) {
            console.error('Failed to check AI status:', error);
            this.showScreen('interview-screen'); // Fallback
        }
    }

    async startAIProvisioning() {
        const startBtn = document.getElementById('start-ai-setup');
        const skipBtn = document.getElementById('skip-ai-setup');
        const statusText = document.getElementById('ai-status-text');
        
        if (startBtn) startBtn.disabled = true;
        if (skipBtn) skipBtn.disabled = true;
        
        try {
            const response = await fetch('/api/ai/provision', { method: 'POST' });
            if (response.ok) {
                this.monitorAIPolling();
            } else {
                if (statusText) statusText.textContent = "Failed to start AI setup.";
                if (startBtn) startBtn.disabled = false;
                if (skipBtn) skipBtn.disabled = false;
            }
        } catch (e) {
            console.error(e);
            if (statusText) statusText.textContent = "Network error starting AI setup.";
            if (startBtn) startBtn.disabled = false;
            if (skipBtn) skipBtn.disabled = false;
        }
    }

    monitorAIPolling() {
        if (this.aiPollingInterval) {
            clearInterval(this.aiPollingInterval);
        }
        
        const stepMap = {
            'checking_ollama':   'step-ollama',
            'installing_ollama': 'step-ollama',
            'checking_model':    'step-model',
            'downloading_model': 'step-model',
            'ready':             'step-ready'
        };
        
        const markStep = (currentStep) => {
            const order = ['step-ollama', 'step-model', 'step-ready'];
            const activeId = stepMap[currentStep];
            const activeIdx = order.indexOf(activeId);
            order.forEach((id, i) => {
                const el = document.getElementById(id);
                if (!el) return;
                el.className = 'ai-step-line ' + (i < activeIdx ? 'done' : i === activeIdx ? 'active' : 'pending');
            });
        };
        
        const updateUI = (status) => {
            const progressBar = document.getElementById('ai-progress-bar');
            const statusText = document.getElementById('ai-status-text');
            const startBtn = document.getElementById('start-ai-setup');
            const skipBtn = document.getElementById('skip-ai-setup');
            
            if (progressBar) progressBar.style.width = `${status.progress || 0}%`;
            if (statusText) {
                statusText.textContent = status.message || status.step || 'Running...';
                statusText.className = 'ai-glow-text';
            }
            if (status.step) markStep(status.step);
            
            if (status.status === 'success') {
                clearInterval(this.aiPollingInterval);
                markStep('ready');
                document.getElementById('step-ready').className = 'ai-step-line done';
                if (statusText) {
                    statusText.textContent = 'AI Assistant ready — continuing...';
                    statusText.className = 'ai-glow-text success';
                }
                setTimeout(() => this.showScreen('interview-screen'), 1500);
            } else if (status.status === 'error') {
                clearInterval(this.aiPollingInterval);
                if (statusText) {
                    statusText.textContent = `Error: ${status.error}`;
                    statusText.className = 'ai-glow-text error';
                }
                if (startBtn) startBtn.disabled = false;
                if (skipBtn) skipBtn.disabled = false;
            }
        };

        this.aiPollingInterval = setInterval(async () => {
            try {
                const res = await fetch('/api/ai/status');
                if (res.ok) {
                    const status = await res.json();
                    updateUI(status);
                }
            } catch (e) {
                console.error("Polling error", e);
            }
        }, 1000);
    }
    
    async loadConfig() {
        try {
            const response = await fetch('/api/config');
            if (response.ok) {
                this.config = await response.json();
                this.populateForm();
            }
        } catch (error) {
            console.error('Failed to load config:', error);
        }
    }
    
    async loadModules() {
        try {
            const response = await fetch('/api/modules');
            if (response.ok) {
                this.modules = await response.json();
                this.renderModules();
            }
        } catch (error) {
            console.error('Failed to load modules:', error);
        }
    }
    
    populateForm() {
        // Populate form fields with existing config
        Object.keys(this.config).forEach(key => {
            const element = document.querySelector(`[name="${key}"]`);
            if (element) {
                if (element.type === 'checkbox') {
                    element.checked = this.config[key].includes(element.value);
                } else {
                    element.value = this.config[key] || '';
                }
            }
        });
    }
    
    async saveConfiguration() {
        const formData = new FormData(document.getElementById('interview-form'));
        const config = {};
        
        // Collect form data
        for (let [key, value] of formData.entries()) {
            if (key === 'services') {
                if (!config.services) config.services = [];
                config.services.push(value);
            } else if (key !== 'bypass_aussie' && key !== 'bypass_global') {
                config[key] = value;
            }
        }
        
        // Streaming preferences logic (checkboxes)
        config.bypass_aussie = true; // Always on
        config.bypass_global = formData.has('bypass_global');
        
        // Capture selected ISOs
        this.selectedISOsNeeded = [];
        document.querySelectorAll('input[name="iso_needed"]:checked').forEach(cb => {
            this.selectedISOsNeeded.push(cb.value);
        });
        config.iso_needed = this.selectedISOsNeeded;
        
        try {
            const response = await fetch('/api/config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(config)
            });
            
            if (response.ok) {
                this.config = config;
                // Go to ISO screen if user wants to provision hardware, else straight to deployment
                if (this.selectedISOsNeeded.length > 0) {
                    this.showScreen('iso-screen');
                } else {
                    this.showScreen('deployment-screen');
                }
                this.updateStatusBar('Configuration saved');
            } else {
                this.showError('Failed to save configuration');
            }
        } catch (error) {
            console.error('Failed to save config:', error);
            this.showError('Network error while saving configuration');
        }
    }
    
    filterOSCards(filter, activePill) {
        // Update active pill
        document.querySelectorAll('.os-filter-pill').forEach(p => p.classList.remove('active'));
        activePill.classList.add('active');

        // Show/hide cards
        document.querySelectorAll('.os-card').forEach(card => {
            if (filter === 'all' || card.dataset.tier === filter) {
                card.classList.remove('hidden');
            } else {
                card.classList.add('hidden');
            }
        });
    }

    // ─── ISO Provisioning ──────────────────────────────────────────────────

    async loadISOs() {
        try {
            const res = await fetch('/api/isos/available');
            if (!res.ok) return;
            const isos = await res.json();

            // Filter to only the ones the user selected (or show all if none selected)
            const needed = this.selectedISOsNeeded.length > 0
                ? isos.filter(iso => this.selectedISOsNeeded.includes(iso.id))
                : isos;

            this.renderISOList(needed);
            this.loadUSBDrives();

            // Start polling if any are already downloading
            const anyActive = needed.some(i => i.download?.status === 'downloading');
            if (anyActive) this.startISOPolling();
        } catch (e) {
            console.error('Failed to load ISOs:', e);
        }
    }

    renderISOList(isos) {
        const container = document.getElementById('iso-list');
        if (!container) return;

        container.innerHTML = isos.map(iso => {
            const dl = iso.download || {};
            const status = dl.status || 'idle';
            const progress = dl.progress || 0;
            const message = dl.message || '';
            const badgeLabels = { idle: 'Not downloaded', downloading: 'Downloading...', complete: '✓ Ready', error: '✗ Error' };

            return `
            <div class="iso-card" id="iso-card-${iso.id}">
                <div class="iso-card-meta">
                    <div class="iso-role">${iso.role}</div>
                    <strong>${iso.name}</strong>
                    <p>${iso.description}</p>
                </div>
                <div class="iso-card-actions">
                    <span class="iso-card-size">${iso.size_gb} GB</span>
                    <span class="iso-status-badge ${status}" id="iso-badge-${iso.id}">${badgeLabels[status] || status}</span>
                    <button class="btn btn-small ${status === 'complete' ? 'btn-secondary' : 'btn-primary'}"
                            id="iso-btn-${iso.id}"
                            onclick="window._app.startISODownload('${iso.id}')"
                            ${status === 'downloading' ? 'disabled' : ''}>
                        ${status === 'complete' ? '↺ Re-download' : status === 'downloading' ? 'Downloading...' : '⬇ Download'}
                    </button>
                </div>
                <div class="iso-progress-wrap ${status === 'downloading' ? 'visible' : ''}" id="iso-progress-wrap-${iso.id}">
                    <div class="iso-progress-bar-track">
                        <div class="iso-progress-bar-fill" id="iso-progress-${iso.id}" style="width:${progress}%"></div>
                    </div>
                    <div class="iso-progress-label" id="iso-progress-label-${iso.id}">${message}</div>
                </div>
            </div>`;
        }).join('');

        this.refreshFlashDropdown(isos);
    }

    async startISODownload(isoId) {
        const btn = document.getElementById(`iso-btn-${isoId}`);
        const badge = document.getElementById(`iso-badge-${isoId}`);
        const wrap = document.getElementById(`iso-progress-wrap-${isoId}`);
        if (btn) { btn.disabled = true; btn.textContent = 'Downloading...'; }
        if (badge) { badge.className = 'iso-status-badge downloading'; badge.textContent = 'Downloading...'; }
        if (wrap) wrap.classList.add('visible');

        try {
            await fetch('/api/isos/download', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ iso_id: isoId })
            });
            this.startISOPolling();
        } catch (e) {
            console.error('Download start error:', e);
        }
    }

    startISOPolling() {
        if (this.isoPollingInterval) return;
        this.isoPollingInterval = setInterval(() => this.pollISOProgress(), 1500);
    }

    async pollISOProgress() {
        try {
            const res = await fetch('/api/isos/status');
            if (!res.ok) return;
            const states = await res.json();
            let anyDownloading = false;

            Object.entries(states).forEach(([isoId, state]) => {
                this.updateISOCard(isoId, state);
                if (state.status === 'downloading') anyDownloading = true;
            });

            if (!anyDownloading) {
                clearInterval(this.isoPollingInterval);
                this.isoPollingInterval = null;
                // Refresh the flash dropdown with newly completed ISOs
                fetch('/api/isos/available')
                    .then(r => r.json())
                    .then(isos => this.refreshFlashDropdown(isos))
                    .catch(() => {});
            }
        } catch (e) {
            console.error('ISO polling error:', e);
        }
    }

    updateISOCard(isoId, state) {
        const badge = document.getElementById(`iso-badge-${isoId}`);
        const btn = document.getElementById(`iso-btn-${isoId}`);
        const wrap = document.getElementById(`iso-progress-wrap-${isoId}`);
        const fill = document.getElementById(`iso-progress-${isoId}`);
        const label = document.getElementById(`iso-progress-label-${isoId}`);
        if (!badge) return;

        const badgeLabels = { idle: 'Not downloaded', downloading: 'Downloading...', complete: '✓ Ready', error: '✗ Error' };
        badge.className = `iso-status-badge ${state.status}`;
        badge.textContent = badgeLabels[state.status] || state.status;

        if (fill) fill.style.width = `${state.progress || 0}%`;
        if (label) label.textContent = state.message || '';
        if (wrap) wrap.classList.toggle('visible', state.status === 'downloading');

        if (btn) {
            btn.disabled = state.status === 'downloading';
            if (state.status === 'complete') {
                btn.textContent = '↺ Re-download';
                btn.className = 'btn btn-small btn-secondary';
                document.getElementById('usb-flash-section').style.display = '';
            } else if (state.status === 'error') {
                btn.disabled = false;
                btn.textContent = '↺ Retry';
                btn.className = 'btn btn-small btn-primary';
            } else if (state.status !== 'downloading') {
                btn.textContent = '⬇ Download';
                btn.className = 'btn btn-small btn-primary';
            }
        }
    }

    refreshFlashDropdown(isos) {
        const select = document.getElementById('flash-iso-select');
        if (!select) return;
        const completed = isos.filter(i => i.download?.status === 'complete');
        select.innerHTML = completed.length
            ? `<option value="">Select a downloaded ISO...</option>` +
              completed.map(i => `<option value="${i.id}">${i.name}</option>`).join('')
            : `<option value="">No ISOs downloaded yet</option>`;

        if (completed.length > 0) {
            document.getElementById('usb-flash-section').style.display = '';
        }
        this.updateFlashButton();
    }

    async loadUSBDrives() {
        const select = document.getElementById('usb-drive-select');
        if (!select) return;
        select.innerHTML = '<option value="">Scanning...</option>';
        try {
            const res = await fetch('/api/usb/drives');
            if (!res.ok) { select.innerHTML = '<option value="">Could not detect drives</option>'; return; }
            const data = await res.json();
            const drives = data.drives || [];
            if (drives.length === 0) {
                select.innerHTML = '<option value="">No USB drives detected — insert one and click Refresh</option>';
            } else {
                select.innerHTML = `<option value="">Select a USB drive...</option>` +
                    drives.map(d => `<option value="${d.letter}">${d.letter} — ${d.label} (${d.size_gb} GB)</option>`).join('');
            }
        } catch (e) {
            select.innerHTML = '<option value="">Detection failed</option>';
        }
        this.updateFlashButton();
    }

    updateFlashButton() {
        const btn = document.getElementById('flash-usb-btn');
        const iso = document.getElementById('flash-iso-select')?.value;
        const drive = document.getElementById('usb-drive-select')?.value;
        if (btn) btn.disabled = !(iso && drive);
    }

    async flashISO() {
        const isoId = document.getElementById('flash-iso-select')?.value;
        const drive = document.getElementById('usb-drive-select')?.value;
        if (!isoId || !drive) return;

        const btn = document.getElementById('flash-usb-btn');
        btn.disabled = true;
        btn.textContent = 'Launching Rufus...';

        try {
            const res = await fetch('/api/usb/flash', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ iso_id: isoId, drive_letter: drive })
            });
            const result = await res.json();
            if (result.success) {
                this.updateStatusBar('Rufus launched — complete flashing in the Rufus window');
                btn.textContent = '✓ Rufus Launched';
                btn.className = 'btn btn-primary';
            } else {
                this.updateStatusBar(`Flash error: ${result.error}`);
                btn.textContent = '🖨️ Launch Rufus & Flash USB';
                btn.disabled = false;
            }
        } catch (e) {
            btn.textContent = '🖨️ Launch Rufus & Flash USB';
            btn.disabled = false;
        }
    }

    // ─── Module Deployment ─────────────────────────────────────────────────

    renderModules() {
        const container = document.getElementById('modules-list');
        if (!container) return;
        
        container.innerHTML = this.modules.map(module => `
            <div class="module-item" id="module-${module.id}">
                <div class="module-header">
                    <div class="module-title">${module.name}</div>
                    <div class="module-status ${this.deploymentStatus[module.id] || 'pending'}" id="status-${module.id}">
                        ${this.getStatusText(this.deploymentStatus[module.id] || 'pending')}
                    </div>
                </div>
                <div class="module-description">${module.description}</div>
                <div class="module-progress">
                    <div class="module-progress-bar" id="progress-${module.id}" style="width: 0%"></div>
                </div>
            </div>
        `).join('');
    }
    
    getStatusText(status) {
        const statusTexts = {
            'pending': 'Pending',
            'running': 'Installing...',
            'completed': '✓ Complete',
            'error': '✗ Failed'
        };
        return statusTexts[status] || 'Unknown';
    }
    
    async startDeployment() {
        const button = document.getElementById('start-deployment');
        button.disabled = true;
        button.innerHTML = '<span class="spinner"></span> Starting deployment...';
        
        this.updateStatusBar('Deployment started');
        
        // Get selected services
        const selectedServices = this.config.services || [];
        
        // Deploy each selected module
        for (const moduleId of selectedServices) {
            await this.deployModule(moduleId);
        }
        
        button.disabled = false;
        button.innerHTML = 'Start Deployment 🚀';
        
        // Show completion screen
        setTimeout(() => {
            this.showScreen('completion-screen');
            this.renderCompletionSummary();
        }, 1000);
    }
    
    async deployModule(moduleId) {
        this.updateModuleStatus(moduleId, 'running');
        this.updateStatusBar(`Installing ${this.getModuleName(moduleId)}...`);
        
        try {
            const response = await fetch(`/api/deploy/${moduleId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            if (response.ok) {
                const result = await response.json();
                this.updateModuleStatus(moduleId, 'completed');
                this.addChatMessage(`✅ ${this.getModuleName(moduleId)} installed successfully!`, 'ai');
            } else {
                const error = await response.json();
                this.updateModuleStatus(moduleId, 'error');
                this.addChatMessage(`❌ Failed to install ${this.getModuleName(moduleId)}: ${error.error}`, 'ai');
            }
        } catch (error) {
            console.error('Deployment error:', error);
            this.updateModuleStatus(moduleId, 'error');
            this.addChatMessage(`❌ Network error while installing ${this.getModuleName(moduleId)}`, 'ai');
        }
    }
    
    updateModuleStatus(moduleId, status) {
        this.deploymentStatus[moduleId] = status;
        
        const statusElement = document.getElementById(`status-${moduleId}`);
        const progressElement = document.getElementById(`progress-${moduleId}`);
        
        if (statusElement) {
            statusElement.className = `module-status ${status}`;
            statusElement.textContent = this.getStatusText(status);
        }
        
        if (progressElement) {
            const width = status === 'completed' ? 100 : 
                          status === 'running' ? 50 : 
                          status === 'error' ? 100 : 0;
            progressElement.style.width = `${width}%`;
            
            if (status === 'error') {
                progressElement.style.background = 'var(--error)';
            }
        }
    }
    
    getModuleName(moduleId) {
        const module = this.modules.find(m => m.id === moduleId);
        return module ? module.name : moduleId;
    }
    
    async sendChatMessage() {
        const input = document.getElementById('chat-input');
        const message = input.value.trim();
        
        if (!message) return;
        
        // Add user message
        this.addChatMessage(message, 'user');
        input.value = '';
        
        // Get AI response
        try {
            const response = await fetch('/api/ai/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message })
            });
            
            if (response.ok) {
                const result = await response.json();
                this.addChatMessage(result.response, 'ai');
            } else {
                this.addChatMessage('Sorry, I encountered an error. Please try again.', 'ai');
            }
        } catch (error) {
            console.error('Chat error:', error);
            this.addChatMessage('Network error. Please check your connection.', 'ai');
        }
    }
    
    addChatMessage(message, sender) {
        const container = document.getElementById('chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        messageDiv.textContent = message;
        
        container.appendChild(messageDiv);
        container.scrollTop = container.scrollHeight;
    }
    
    renderCompletionSummary() {
        const container = document.getElementById('completion-summary');
        if (!container) return;
        
        const completedModules = this.modules.filter(m => 
            this.deploymentStatus[m.id] === 'completed'
        );
        
        container.innerHTML = `
            <h3>🎉 Successfully Installed:</h3>
            <ul>
                ${completedModules.map(module => `
                    <li>
                        <strong>${module.name}</strong> - ${module.description}
                    </li>
                `).join('')}
            </ul>
            ${this.deploymentStatus.error ? `
                <div class="error-summary">
                    <h4>⚠️ Some services failed to install:</h4>
                    <p>You can retry these services later or check the logs for more information.</p>
                </div>
            ` : ''}
        `;
    }
    
    downloadConfigs() {
        // Create a zip file with configuration files
        // For now, just download the main config as JSON
        const dataStr = JSON.stringify(this.config, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = 'shut-the-front-door-config.json';
        link.click();
        
        URL.revokeObjectURL(url);
        this.updateStatusBar('Configuration downloaded');
    }
    
    viewGuide() {
        window.open('/guide/digital_resistance_guide.html', '_blank');
    }
    
    updateStatusBar(message) {
        document.getElementById('status-text').textContent = message;
        document.getElementById('progress-text').textContent = message;
    }
    
    showError(message) {
        this.updateStatusBar(`Error: ${message}`);
        this.addChatMessage(`❌ ${message}`, 'ai');
    }
}

// Initialize the app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window._app = new InstallerApp();
});

// Auto-refresh deployment status
setInterval(async () => {
    if (document.getElementById('deployment-screen').classList.contains('active')) {
        try {
            const response = await fetch('/api/status');
            if (response.ok) {
                const status = await response.json();
                // Update any live status information
                if (status.tracker_content) {
                    // Parse tracker content and update UI if needed
                }
            }
        } catch (error) {
            console.error('Status refresh error:', error);
        }
    }
}, 5000);
