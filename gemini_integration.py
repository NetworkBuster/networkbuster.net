"""
NetworkBuster - Google Gemini AI Integration
Simple integration with Google Gemini API
"""

import os
from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# Gemini API Configuration
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent'

# HTML Template for Gemini Chat Interface
GEMINI_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NetworkBuster Gemini AI</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            width: 100%;
            max-width: 900px;
            height: 85vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 28px;
            margin-bottom: 5px;
        }
        
        .header p {
            font-size: 14px;
            opacity: 0.9;
        }
        
        .api-status {
            padding: 15px 30px;
            background: #f8f9fa;
            border-bottom: 2px solid #e9ecef;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        
        .status-indicator.connected {
            background: #28a745;
        }
        
        .status-indicator.disconnected {
            background: #dc3545;
            animation: none;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 20px 30px;
            background: #f8f9fa;
        }
        
        .message {
            margin-bottom: 20px;
            animation: slideIn 0.3s ease-out;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .message.user {
            text-align: right;
        }
        
        .message-content {
            display: inline-block;
            max-width: 70%;
            padding: 15px 20px;
            border-radius: 15px;
            word-wrap: break-word;
        }
        
        .message.user .message-content {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-bottom-right-radius: 5px;
        }
        
        .message.assistant .message-content {
            background: white;
            color: #333;
            border: 1px solid #e9ecef;
            border-bottom-left-radius: 5px;
            text-align: left;
        }
        
        .message-label {
            font-size: 12px;
            margin-bottom: 5px;
            opacity: 0.7;
        }
        
        .input-container {
            padding: 20px 30px;
            background: white;
            border-top: 2px solid #e9ecef;
            display: flex;
            gap: 10px;
        }
        
        #messageInput {
            flex: 1;
            padding: 15px;
            border: 2px solid #e9ecef;
            border-radius: 25px;
            font-size: 15px;
            outline: none;
            transition: border-color 0.3s;
        }
        
        #messageInput:focus {
            border-color: #667eea;
        }
        
        #sendButton {
            padding: 15px 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 25px;
            font-size: 15px;
            cursor: pointer;
            transition: transform 0.2s;
        }
        
        #sendButton:hover {
            transform: scale(1.05);
        }
        
        #sendButton:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: scale(1);
        }
        
        .loading {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #667eea;
            animation: bounce 1.4s infinite ease-in-out both;
        }
        
        .loading:nth-child(1) { animation-delay: -0.32s; }
        .loading:nth-child(2) { animation-delay: -0.16s; margin: 0 5px; }
        
        @keyframes bounce {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1); }
        }
        
        .error-message {
            padding: 15px;
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        
        .info-box {
            padding: 15px;
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
            border-radius: 10px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 NetworkBuster Gemini AI</h1>
            <p>Powered by Google Gemini Pro</p>
        </div>
        
        <div class="api-status">
            <div class="status-indicator" id="statusIndicator"></div>
            <span id="statusText">Checking API connection...</span>
        </div>
        
        <div class="chat-container" id="chatContainer">
            <div class="info-box" id="setupInfo">
                <strong>📋 Setup Instructions:</strong><br>
                Set your Gemini API key as an environment variable:<br>
                <code>$env:GEMINI_API_KEY="your-api-key-here"</code><br><br>
                Get your free API key at: <a href="https://makersuite.google.com/app/apikey" target="_blank">Google AI Studio</a>
            </div>
        </div>
        
        <div class="input-container">
            <input type="text" id="messageInput" placeholder="Ask Gemini anything..." />
            <button id="sendButton" onclick="sendMessage()">Send</button>
        </div>
    </div>
    
    <script>
        let apiKeyConfigured = false;
        
        async function checkApiStatus() {
            try {
                const response = await fetch('/api/gemini/status');
                const data = await response.json();
                
                const indicator = document.getElementById('statusIndicator');
                const statusText = document.getElementById('statusText');
                
                if (data.configured) {
                    indicator.className = 'status-indicator connected';
                    statusText.textContent = 'API Connected - Ready to chat';
                    apiKeyConfigured = true;
                    document.getElementById('setupInfo').style.display = 'none';
                } else {
                    indicator.className = 'status-indicator disconnected';
                    statusText.textContent = 'API Key Not Configured';
                    apiKeyConfigured = false;
                }
            } catch (error) {
                console.error('Status check failed:', error);
            }
        }
        
        function addMessage(content, role) {
            const chatContainer = document.getElementById('chatContainer');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${role}`;
            
            const label = role === 'user' ? 'You' : 'Gemini';
            
            messageDiv.innerHTML = `
                <div class="message-label">${label}</div>
                <div class="message-content">${escapeHtml(content)}</div>
            `;
            
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
        
        function addLoadingMessage() {
            const chatContainer = document.getElementById('chatContainer');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message assistant';
            messageDiv.id = 'loadingMessage';
            
            messageDiv.innerHTML = `
                <div class="message-label">Gemini</div>
                <div class="message-content">
                    <span class="loading"></span>
                    <span class="loading"></span>
                    <span class="loading"></span>
                </div>
            `;
            
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
        
        function removeLoadingMessage() {
            const loadingMessage = document.getElementById('loadingMessage');
            if (loadingMessage) {
                loadingMessage.remove();
            }
        }
        
        async function sendMessage() {
            if (!apiKeyConfigured) {
                alert('Please configure your Gemini API key first!');
                return;
            }
            
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            // Add user message
            addMessage(message, 'user');
            input.value = '';
            
            // Disable input while processing
            const sendButton = document.getElementById('sendButton');
            sendButton.disabled = true;
            input.disabled = true;
            
            // Show loading
            addLoadingMessage();
            
            try {
                const response = await fetch('/api/gemini/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: message })
                });
                
                const data = await response.json();
                
                removeLoadingMessage();
                
                if (data.success) {
                    addMessage(data.response, 'assistant');
                } else {
                    addMessage(`Error: ${data.error}`, 'assistant');
                }
            } catch (error) {
                removeLoadingMessage();
                addMessage(`Connection error: ${error.message}`, 'assistant');
            } finally {
                sendButton.disabled = false;
                input.disabled = false;
                input.focus();
            }
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML.replace(/\n/g, '<br>');
        }
        
        // Enter key to send
        document.getElementById('messageInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
        
        // Check API status on load
        checkApiStatus();
        setInterval(checkApiStatus, 30000); // Check every 30 seconds
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Serve the Gemini chat interface"""
    return render_template_string(GEMINI_TEMPLATE)

@app.route('/api/gemini/status')
def api_status():
    """Check if Gemini API is configured"""
    configured = bool(GEMINI_API_KEY)
    return jsonify({
        'configured': configured,
        'model': 'gemini-pro'
    })

@app.route('/api/gemini/chat', methods=['POST'])
def chat():
    """Send message to Gemini and get response"""
    if not GEMINI_API_KEY:
        return jsonify({
            'success': False,
            'error': 'Gemini API key not configured. Set GEMINI_API_KEY environment variable.'
        }), 400
    
    try:
        data = request.json
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({
                'success': False,
                'error': 'No message provided'
            }), 400
        
        # Call Gemini API
        headers = {
            'Content-Type': 'application/json'
        }
        
        payload = {
            'contents': [{
                'parts': [{
                    'text': user_message
                }]
            }]
        }
        
        response = requests.post(
            f'{GEMINI_API_URL}?key={GEMINI_API_KEY}',
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Extract the response text
            if 'candidates' in result and len(result['candidates']) > 0:
                candidate = result['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    parts = candidate['content']['parts']
                    if len(parts) > 0 and 'text' in parts[0]:
                        gemini_response = parts[0]['text']
                        
                        return jsonify({
                            'success': True,
                            'response': gemini_response
                        })
            
            return jsonify({
                'success': False,
                'error': 'Unexpected response format from Gemini API'
            }), 500
        else:
            error_message = response.json().get('error', {}).get('message', 'Unknown error')
            return jsonify({
                'success': False,
                'error': f'Gemini API error: {error_message}'
            }), response.status_code
            
    except requests.exceptions.RequestException as e:
        return jsonify({
            'success': False,
            'error': f'Network error: {str(e)}'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'gemini-integration',
        'api_configured': bool(GEMINI_API_KEY)
    })

if __name__ == '__main__':
    print("""
╔════════════════════════════════════════════════════════════╗
║  NetworkBuster - Google Gemini AI Integration             ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    if GEMINI_API_KEY:
        print("✅ Gemini API Key: Configured")
    else:
        print("⚠️  Gemini API Key: Not configured")
        print("\n📋 To configure, set environment variable:")
        print("   PowerShell: $env:GEMINI_API_KEY=\"your-api-key\"")
        print("   Get your key: https://makersuite.google.com/app/apikey\n")
    
    print("🚀 Starting Gemini Integration Server on http://localhost:4000")
    print("⚡ Features:")
    print("   ✓ Google Gemini Pro chat interface")
    print("   ✓ Real-time AI responses")
    print("   ✓ Clean, modern UI")
    print("   ✓ Health check: /health")
    print("")
    
    app.run(host='0.0.0.0', port=4000, debug=False)
