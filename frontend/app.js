// Generate a unique client ID
const clientId = 'client_' + Math.random().toString(36).substr(2, 9);

// WebSocket connection
class ChatService {
    constructor() {
        this.connect();
        this.messageQueue = [];
        this.isConnected = false;
    }

    connect() {
        this.ws = new WebSocket(`ws://localhost:8000/ws/chat/${clientId}`);
        
        this.ws.onopen = () => {
            console.log('Connected to chat service');
            this.isConnected = true;
            this.processMessageQueue();
            updateAgentStatus(true);
        };

        this.ws.onclose = () => {
            console.log('Disconnected from chat service');
            this.isConnected = false;
            updateAgentStatus(false);
            // Attempt to reconnect after 3 seconds
            setTimeout(() => this.connect(), 3000);
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            updateAgentStatus(false);
        };

        this.ws.onmessage = (event) => {
            const response = JSON.parse(event.data);
            handleAgentResponse(response);
        };
    }

    sendMessage(message) {
        const messageData = {
            message,
            timestamp: new Date().toISOString(),
            context: {
                category: getCurrentCategory(),
                clientId
            }
        };

        if (this.isConnected && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(messageData));
        } else {
            this.messageQueue.push(messageData);
        }
    }

    processMessageQueue() {
        while (this.messageQueue.length > 0 && this.isConnected) {
            const messageData = this.messageQueue.shift();
            this.ws.send(JSON.stringify(messageData));
        }
    }
}

// UI Elements
const chatMessages = document.getElementById('chat-messages');
const chatInput = document.getElementById('chat-input');
const sendButton = document.getElementById('send-btn');
const messageTemplate = document.getElementById('message-template');
const categoryButtons = document.querySelectorAll('.category-btn');

// Initialize chat service
const chatService = new ChatService();

// Event Listeners
sendButton.addEventListener('click', sendMessage);
chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

categoryButtons.forEach(button => {
    button.addEventListener('click', () => {
        categoryButtons.forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
    });
});

// Message Handling Functions
function sendMessage() {
    const message = chatInput.value.trim();
    if (message) {
        addMessageToChat('user', message);
        chatService.sendMessage(message);
        chatInput.value = '';
    }
}

function handleAgentResponse(response) {
    if (response.type === 'error') {
        addMessageToChat('system', `Error: ${response.message}`, 'error');
        return;
    }

    if (response.type === 'agent_response') {
        addMessageToChat('assistant', formatAgentResponse(response.data));
    }
}

function addMessageToChat(role, content, type = 'normal') {
    const messageNode = messageTemplate.content.cloneNode(true);
    const messageDiv = messageNode.querySelector('.message');
    const messageRole = messageNode.querySelector('.message-role');
    const messageTime = messageNode.querySelector('.message-time');
    const messageContent = messageNode.querySelector('.message-content');

    messageDiv.classList.add(role);
    if (type === 'error') messageDiv.classList.add('error');

    messageRole.textContent = formatRole(role);
    messageTime.textContent = new Date().toLocaleTimeString();
    messageContent.innerHTML = typeof content === 'string' 
        ? content 
        : formatAgentResponse(content);

    chatMessages.appendChild(messageNode);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function formatRole(role) {
    const roles = {
        user: 'You',
        assistant: 'Audit Assistant',
        system: 'System'
    };
    return roles[role] || role;
}

function formatAgentResponse(response) {
    if (typeof response === 'string') return response;

    let formattedResponse = '';

    if (response.type === 'audit_plan') {
        formattedResponse = formatAuditPlan(response);
    } else if (response.type === 'analysis_results') {
        formattedResponse = formatAnalysisResults(response);
    } else if (response.type === 'audit_report') {
        formattedResponse = formatAuditReport(response);
    } else {
        formattedResponse = `<pre>${JSON.stringify(response, null, 2)}</pre>`;
    }

    return formattedResponse;
}

function formatAuditPlan(response) {
    return `
        <div class="audit-plan">
            <h3>Audit Plan - ${response.category}</h3>
            <div class="audit-scope">
                <h4>Scope:</h4>
                <ul>
                    ${response.audit_scope.objectives.map(obj => `<li>${obj}</li>`).join('')}
                </ul>
            </div>
            ${response.next_steps.length ? `
                <div class="next-steps">
                    <h4>Next Steps:</h4>
                    <ul>
                        ${response.next_steps.map(step => `<li>${step}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}
        </div>
    `;
}

function formatAnalysisResults(response) {
    return `
        <div class="analysis-results">
            <h3>Analysis Results - ${response.category}</h3>
            <div class="findings">
                ${Object.entries(response.analysis.findings || {}).map(([key, value]) => `
                    <div class="finding">
                        <h4>${key}:</h4>
                        <p>${value}</p>
                    </div>
                `).join('')}
            </div>
            ${response.recommendations.length ? `
                <div class="recommendations">
                    <h4>Recommendations:</h4>
                    <ul>
                        ${response.recommendations.map(rec => `
                            <li>
                                <strong>${rec.area}:</strong> ${rec.recommendation}
                                <span class="priority">(Priority: ${rec.priority})</span>
                            </li>
                        `).join('')}
                    </ul>
                </div>
            ` : ''}
        </div>
    `;
}

function formatAuditReport(response) {
    const report = response.report;
    return `
        <div class="audit-report">
            <h3>Audit Report - ${response.category}</h3>
            <div class="executive-summary">
                <h4>Executive Summary:</h4>
                <p>${report.executive_summary.overview}</p>
            </div>
            <div class="key-findings">
                <h4>Key Findings:</h4>
                <ul>
                    ${report.executive_summary.key_findings.map(finding => `
                        <li>
                            <strong>${finding.summary}</strong>
                            <span class="risk-level ${finding.risk_level.toLowerCase()}">
                                ${finding.risk_level}
                            </span>
                        </li>
                    `).join('')}
                </ul>
            </div>
            ${report.recommendations.length ? `
                <div class="recommendations">
                    <h4>Recommendations:</h4>
                    <ul>
                        ${report.recommendations.map(rec => `
                            <li class="recommendation ${rec.risk_level.toLowerCase()}">
                                <div class="rec-header">
                                    <strong>${rec.finding_ref}</strong>
                                    <span class="priority">Priority: ${rec.implementation_priority}</span>
                                </div>
                                <p>${rec.recommendation}</p>
                            </li>
                        `).join('')}
                    </ul>
                </div>
            ` : ''}
        </div>
    `;
}

function updateAgentStatus(isConnected) {
    const indicators = document.querySelectorAll('.agent-indicator');
    indicators.forEach(indicator => {
        indicator.style.backgroundColor = isConnected 
            ? 'var(--success-color)' 
            : 'var(--error-color)';
    });
}

function getCurrentCategory() {
    const activeButton = document.querySelector('.category-btn.active');
    return activeButton ? activeButton.dataset.category : null;
}

// Initialize first category as active
categoryButtons[0].classList.add('active');