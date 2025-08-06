// WynnBuilder Web Interface JavaScript

class WynnBuilder {
    constructor() {
        this.isGenerating = false;
        this.isChatting = false;
        this.currentBuilds = [];
        
        this.init();
    }

    init() {
        // Bind event listeners
        this.bindEvents();
        
        // Initialize tooltips
        this.initTooltips();
        
        console.log('WynnBuilder initialized');
    }

    bindEvents() {
        // Build form submission
        document.getElementById('buildForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.generateBuilds();
        });

        // Chat form submission
        document.getElementById('chatForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.sendChatMessage();
        });

        // Example question buttons
        document.querySelectorAll('.example-question').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const question = e.target.dataset.question;
                document.getElementById('chatInput').value = question;
                this.sendChatMessage();
            });
        });

        // Smooth scrolling for navigation
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    initTooltips() {
        // Initialize Bootstrap tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    async generateBuilds() {
        if (this.isGenerating) return;

        this.isGenerating = true;
        this.showLoading('generateBtn', 'Generating...');

        try {
            // Collect form data
            const formData = this.getFormData();
            
            // Show loading modal
            const loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
            loadingModal.show();

            // Make API request
            const response = await fetch('/api/generate_builds', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();
            loadingModal.hide();

            if (data.success) {
                this.currentBuilds = data.builds;
                this.displayBuilds(data.builds, data.total_found);
            } else {
                this.showError('Failed to generate builds: ' + (data.error || 'Unknown error'));
            }

        } catch (error) {
            console.error('Error generating builds:', error);
            this.showError('Network error. Please try again.');
        } finally {
            this.isGenerating = false;
            this.hideLoading('generateBtn', 'Generate Builds');
        }
    }

    getFormData() {
        const elements = document.getElementById('elementsInput').value
            .split(',')
            .map(e => e.trim())
            .filter(e => e.length > 0);

        return {
            class: document.getElementById('classSelect').value,
            playstyle: document.getElementById('playstyleSelect').value,
            elements: elements,
            no_mythics: document.getElementById('noMythics').checked,
            min_dps: parseInt(document.getElementById('minDps').value) || 0,
            min_mana: parseFloat(document.getElementById('minMana').value) || 0,
            max_cost: parseInt(document.getElementById('maxCost').value) || 0
        };
    }

    displayBuilds(builds, totalFound) {
        const resultsContainer = document.getElementById('buildResults');
        const resultsCount = document.getElementById('resultsCount');

        // Update count
        resultsCount.textContent = `${builds.length} of ${totalFound} builds`;

        if (builds.length === 0) {
            resultsContainer.innerHTML = `
                <div class="text-center text-muted py-5">
                    <i class="fas fa-search fa-3x mb-3"></i>
                    <h5>No builds found</h5>
                    <p>Try adjusting your filters or requirements</p>
                </div>
            `;
            return;
        }

        // Generate build cards
        const buildsHtml = builds.map((build, index) => this.createBuildCard(build, index)).join('');
        resultsContainer.innerHTML = buildsHtml;

        // Add event listeners for export buttons
        builds.forEach((build, index) => {
            document.getElementById(`export-wynnbuilder-${index}`).addEventListener('click', () => {
                this.exportBuild(build, 'wynnbuilder');
            });
            document.getElementById(`export-text-${index}`).addEventListener('click', () => {
                this.exportBuild(build, 'text');
            });
        });

        // Scroll to results
        document.getElementById('buildResults').scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
        });
    }

    createBuildCard(build, index) {
        const tierClass = this.getTierClass(build.items.weapon?.tier || 'Normal');
        
        return `
            <div class="build-card card mb-3 fade-in">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h6 class="mb-0">
                        <i class="fas fa-trophy text-warning me-2"></i>
                        Build #${build.id} - ${build.class.charAt(0).toUpperCase() + build.class.slice(1)}
                    </h6>
                    <span class="badge bg-primary">${Math.round(build.stats.dps)} DPS</span>
                </div>
                <div class="card-body">
                    <div class="row">
                        <!-- Items -->
                        <div class="col-md-7">
                            <h6 class="text-muted mb-2">
                                <i class="fas fa-sword me-1"></i>Equipment
                            </h6>
                            <div class="item-grid">
                                ${this.createItemSlots(build.items)}
                            </div>
                        </div>
                        
                        <!-- Stats -->
                        <div class="col-md-5">
                            <h6 class="text-muted mb-2">
                                <i class="fas fa-chart-bar me-1"></i>Statistics
                            </h6>
                            <div class="build-stats">
                                <div class="stat-item">
                                    <span><i class="fas fa-skull text-danger me-1"></i>DPS</span>
                                    <span class="stat-value">${Math.round(build.stats.dps)}</span>
                                </div>
                                <div class="stat-item">
                                    <span><i class="fas fa-tint text-primary me-1"></i>Mana/s</span>
                                    <span class="stat-value">${build.stats.mana.toFixed(1)}</span>
                                </div>
                                <div class="stat-item">
                                    <span><i class="fas fa-heart text-success me-1"></i>EHP</span>
                                    <span class="stat-value">${Math.round(build.stats.ehp).toLocaleString()}</span>
                                </div>
                                <div class="stat-item">
                                    <span><i class="fas fa-coins text-warning me-1"></i>Cost</span>
                                    <span class="stat-value">${Math.round(build.stats.cost)} EB</span>
                                </div>
                            </div>
                            
                            <!-- Skill Points -->
                            <h6 class="text-muted mb-2 mt-3">
                                <i class="fas fa-star me-1"></i>Skill Points
                            </h6>
                            <div class="skill-points">
                                <div class="skill-point str">
                                    <div>STR</div>
                                    <div>${build.skill_points.str}</div>
                                </div>
                                <div class="skill-point dex">
                                    <div>DEX</div>
                                    <div>${build.skill_points.dex}</div>
                                </div>
                                <div class="skill-point int">
                                    <div>INT</div>
                                    <div>${build.skill_points.int}</div>
                                </div>
                                <div class="skill-point def">
                                    <div>DEF</div>
                                    <div>${build.skill_points.def}</div>
                                </div>
                                <div class="skill-point agi">
                                    <div>AGI</div>
                                    <div>${build.skill_points.agi}</div>
                                </div>
                            </div>
                            <div class="text-center mt-2">
                                <small class="text-muted">
                                    Total: ${Object.values(build.skill_points).reduce((a, b) => a + b, 0)}/120
                                </small>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Export Buttons -->
                    <div class="export-buttons mt-3">
                        <button class="btn btn-outline-primary export-btn" id="export-wynnbuilder-${index}">
                            <i class="fas fa-external-link-alt me-1"></i>Export to Wynnbuilder
                        </button>
                        <button class="btn btn-outline-secondary export-btn" id="export-text-${index}">
                            <i class="fas fa-file-text me-1"></i>Export as Text
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    createItemSlots(items) {
        const slots = [
            { key: 'weapon', name: 'Weapon', icon: 'fas fa-sword' },
            { key: 'helmet', name: 'Helmet', icon: 'fas fa-hard-hat' },
            { key: 'chestplate', name: 'Chestplate', icon: 'fas fa-tshirt' },
            { key: 'leggings', name: 'Leggings', icon: 'fas fa-socks' },
            { key: 'boots', name: 'Boots', icon: 'fas fa-shoe-prints' },
            { key: 'ring1', name: 'Ring 1', icon: 'fas fa-ring' },
            { key: 'ring2', name: 'Ring 2', icon: 'fas fa-ring' },
            { key: 'bracelet', name: 'Bracelet', icon: 'fas fa-circle' },
            { key: 'necklace', name: 'Necklace', icon: 'fas fa-gem' }
        ];

        return slots.map(slot => {
            const item = items[slot.key];
            if (item) {
                const tierClass = this.getTierClass(item.tier);
                return `
                    <div class="item-slot">
                        <div class="item-name ${tierClass}">${item.name}</div>
                        <div class="item-type">${slot.name}</div>
                    </div>
                `;
            } else {
                return `
                    <div class="item-slot">
                        <div class="item-name text-muted">Empty</div>
                        <div class="item-type">${slot.name}</div>
                    </div>
                `;
            }
        }).join('');
    }

    getTierClass(tier) {
        const tierMap = {
            'Normal': 'text-tier-normal',
            'Unique': 'text-tier-unique',
            'Rare': 'text-tier-rare',
            'Legendary': 'text-tier-legendary',
            'Mythic': 'text-tier-mythic',
            'Fabled': 'text-tier-fabled'
        };
        return tierMap[tier] || 'text-tier-normal';
    }

    async exportBuild(build, format) {
        try {
            const response = await fetch('/api/export_build', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    build: build,
                    format: format
                })
            });

            const data = await response.json();

            if (data.success) {
                if (format === 'wynnbuilder') {
                    this.copyToClipboard(data.export_string, 'Wynnbuilder string copied to clipboard!');
                } else if (format === 'text') {
                    this.downloadTextFile(data.export_text, `build_${build.id}.txt`);
                }
            } else {
                this.showError('Export failed: ' + (data.error || 'Unknown error'));
            }

        } catch (error) {
            console.error('Error exporting build:', error);
            this.showError('Network error during export. Please try again.');
        }
    }

    async sendChatMessage() {
        if (this.isChatting) return;

        const input = document.getElementById('chatInput');
        const message = input.value.trim();

        if (!message) return;

        this.isChatting = true;
        this.showLoading('chatSendBtn', '');

        // Add user message to chat
        this.addChatMessage(message, 'user');
        input.value = '';

        try {
            const response = await fetch('/api/ai_query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: message })
            });

            const data = await response.json();

            if (data.success) {
                this.addChatMessage(data.response, 'ai');
            } else {
                this.addChatMessage('Sorry, I encountered an error processing your request.', 'ai');
            }

        } catch (error) {
            console.error('Error sending chat message:', error);
            this.addChatMessage('Sorry, I\'m having trouble connecting right now. Please try again.', 'ai');
        } finally {
            this.isChatting = false;
            this.hideLoading('chatSendBtn', '<i class="fas fa-paper-plane"></i>');
        }
    }

    addChatMessage(message, sender) {
        const chatContainer = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `${sender}-message`;

        const content = document.createElement('div');
        content.className = 'message-content';
        
        if (sender === 'user') {
            content.innerHTML = `<strong>You:</strong> ${this.escapeHtml(message)}`;
        } else {
            content.innerHTML = `<strong>AI Assistant:</strong> ${this.formatAIResponse(message)}`;
        }

        messageDiv.appendChild(content);
        chatContainer.appendChild(messageDiv);

        // Scroll to bottom
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    formatAIResponse(message) {
        // Convert markdown-style formatting to HTML
        return this.escapeHtml(message)
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/•/g, '&bull;')
            .replace(/\n/g, '<br>');
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    copyToClipboard(text, successMessage) {
        navigator.clipboard.writeText(text).then(() => {
            this.showSuccess(successMessage);
        }).catch(() => {
            // Fallback for older browsers
            const textarea = document.createElement('textarea');
            textarea.value = text;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
            this.showSuccess(successMessage);
        });
    }

    downloadTextFile(content, filename) {
        const blob = new Blob([content], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        this.showSuccess('Build exported as ' + filename);
    }

    showLoading(elementId, text) {
        const element = document.getElementById(elementId);
        element.disabled = true;
        element.innerHTML = `
            <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
            ${text}
        `;
    }

    hideLoading(elementId, originalText) {
        const element = document.getElementById(elementId);
        element.disabled = false;
        element.innerHTML = originalText;
    }

    showError(message) {
        this.showToast(message, 'danger');
    }

    showSuccess(message) {
        this.showToast(message, 'success');
    }

    showToast(message, type) {
        // Create toast element
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${this.escapeHtml(message)}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;

        // Add to container
        let toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            document.body.appendChild(toastContainer);
        }

        toastContainer.appendChild(toast);

        // Show toast
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();

        // Remove from DOM after hiding
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new WynnBuilder();
});
