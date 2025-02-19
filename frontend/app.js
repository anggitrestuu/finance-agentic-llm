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
        clientId,
      },
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
const loadingTemplate = document.getElementById('loading-template');
const categoryButtons = document.querySelectorAll('.category-btn');

// Initialize chat service
const chatService = new ChatService();

// Event Listeners
const resetButton = document.getElementById('reset-btn');
resetButton.addEventListener('click', () => window.location.reload());

sendButton.addEventListener('click', sendMessage);
chatInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

categoryButtons.forEach((button) => {
  button.addEventListener('click', () => {
    categoryButtons.forEach((btn) => btn.classList.remove('active'));
    button.classList.add('active');
  });
});

// Message Handling Functions
function sendMessage() {
  const message = chatInput.value.trim();
  if (message) {
    addMessageToChat('user', message);
    
    // Show loading indicator
    const loadingNode = loadingTemplate.content.cloneNode(true);
    const loadingTime = loadingNode.querySelector('.message-time');
    loadingTime.textContent = new Date().toLocaleTimeString();
    chatMessages.appendChild(loadingNode);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    chatService.sendMessage(message);
    chatInput.value = '';
  }
}

function handleAgentResponse(response) {
  // Remove any existing loading indicators
  const loadingIndicators = chatMessages.querySelectorAll('.message.loading');
  loadingIndicators.forEach(indicator => indicator.remove());

  if (response.type === 'error') {
    addMessageToChat('system', `Error: ${response.message}`, 'error');
    return;
  }

  if (response.type === 'agent_response') {
    addMessageToChat('assistant', formatAgentResponse(response.data));
    
    // Add logs to the logs panel if they exist
    if (response.logs) {
      updateLogs(response.logs);
    }
  }
}

// Logs Panel Functions
const logsPanel = document.getElementById('logs-panel');
const toggleLogsBtn = document.getElementById('toggle-logs');
const logsContent = document.getElementById('logs-content');

// Close logs button
const closeLogsBtn = document.getElementById('close-logs-btn');

// Toggle and close logs functionality
function toggleLogs(show) {
  logsPanel.classList.toggle('show', show);
  toggleLogsBtn.textContent = show ? 'Hide Logs' : 'Show Logs';
}

toggleLogsBtn.addEventListener('click', () => {
  toggleLogs(!logsPanel.classList.contains('show'));
});

closeLogsBtn.addEventListener('click', () => {
  toggleLogs(false);
});

function updateLogs(logs) {
  // Clear previous logs
  logsContent.innerHTML = '';
  
  // Create a pre element for formatted logs
  const preElement = document.createElement('pre');
  preElement.classList.add('logs-pre');
  
  // Format logs as JSON with indentation
  let formattedLogs = typeof logs === 'string'
    ? logs
    : JSON.stringify(logs, null, 2);
  
  // Normalize text by removing specific patterns
  formattedLogs = formattedLogs
    // Remove ANSI formatting characters
    .replace(/\[\d+m\[\d+m|\[\d+m/g, '')
    // Remove extra text after "Task:"
    .replace(/## Task:\s*[^#\n]+/g, '## Task')
    // Clean up any double newlines that might result
    .replace(/\n\s*\n/g, '\n');
    
  preElement.textContent = formattedLogs;
  
  // Add to logs panel
  logsContent.appendChild(preElement);
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

  // Parse content based on its type and role
  if (typeof content === 'string') {
    // Use marked for markdown parsing for assistant and user messages
    if (role === 'assistant' || role === 'user') {
      messageContent.innerHTML = marked.parse(content);
    } else {
      messageContent.textContent = content;
    }
  } else {
    // For structured responses (like audit plans, reports etc)
    messageContent.innerHTML = formatAgentResponse(content);
  }

  chatMessages.appendChild(messageNode);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function formatRole(role) {
  const roles = {
    user: 'You',
    assistant: 'Audit Assistant',
    system: 'System',
  };
  return roles[role] || role;
}

function formatAgentResponse(response) {
  if (typeof response === 'string') {
    return marked.parse(response);
  }

  return marked.parse(JSON.stringify(response, null, 2));
}

function updateAgentStatus(isConnected) {
  const indicators = document.querySelectorAll('.agent-indicator');
  indicators.forEach((indicator) => {
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
