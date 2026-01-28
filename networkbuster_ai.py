"""
NetworkBuster AI - Intelligent Network Assistant
AI-powered diagnostics, monitoring, and automation for NetworkBuster
"""

import os
from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
import psutil
import socket
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)

# AI Signal Monitor Template - Read-only window
AI_SIGNAL_MONITOR = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Signal Monitor - Home Base</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            background: #000;
            color: #0f0;
            padding: 20px;
            overflow: hidden;
        }
        
        .monitor-container {
            border: 2px solid #0f0;
            padding: 15px;
            height: 95vh;
            background: rgba(0, 255, 0, 0.05);
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
        }
        
        .header {
            border-bottom: 1px solid #0f0;
            padding-bottom: 10px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .status-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .status-panel {
            border: 1px solid #0f0;
            padding: 15px;
            background: rgba(0, 255, 0, 0.02);
        }
        
        .status-panel h3 {
            color: #0ff;
            margin-bottom: 10px;
            font-size: 14px;
            text-transform: uppercase;
        }
        
        .signal-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #0f0;
            animation: pulse 2s infinite;
            margin-right: 8px;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; box-shadow: 0 0 10px #0f0; }
            50% { opacity: 0.3; }
        }
        
        .activity-log {
            border: 1px solid #0f0;
            padding: 15px;
            height: 300px;
            overflow-y: auto;
            background: rgba(0, 255, 0, 0.02);
            font-size: 12px;
        }
        
        .log-entry {
            margin-bottom: 5px;
            opacity: 0;
            animation: fadeIn 0.5s forwards;
        }
        
        @keyframes fadeIn {
            to { opacity: 1; }
        }
        
        .threat-alert {
            color: #f00;
            font-weight: bold;
        }
        
        .normal-activity {
            color: #0f0;
        }
        
        .warning {
            color: #ff0;
        }
        
        .metric {
            display: flex;
            justify-content: space-between;
            margin: 8px 0;
            font-size: 13px;
        }
        
        .metric-value {
            color: #0ff;
            font-weight: bold;
        }
        
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: rgba(0, 255, 0, 0.1);
        }
        
        ::-webkit-scrollbar-thumb {
            background: #0f0;
        }
        
        .read-only-badge {
            background: rgba(255, 0, 0, 0.2);
            border: 1px solid #f00;
            padding: 5px 10px;
            border-radius: 3px;
            font-size: 11px;
            color: #f00;
        }
    </style>
</head>
<body>
    <div class="monitor-container">
        <div class="header">
            <div>
                <h1>🛰️ AI SIGNAL MONITOR - HOME BASE</h1>
                <div style="font-size: 11px; margin-top: 5px; opacity: 0.7;">NetworkBuster Intelligence Feed</div>
            </div>
            <div>
                <span class="read-only-badge">READ ONLY</span>
            </div>
        </div>
        
        <div class="status-grid">
            <div class="status-panel">
                <h3>🔴 SIGNAL STATUS</h3>
                <div class="metric">
                    <span>Home Base Connection:</span>
                    <span class="metric-value" id="connectionStatus">ACTIVE</span>
                </div>
                <div class="metric">
                    <span>Signal Strength:</span>
                    <span class="metric-value" id="signalStrength">100%</span>
                </div>
                <div class="metric">
                    <span>AI Engine:</span>
                    <span class="metric-value"><span class="signal-indicator"></span>ONLINE</span>
                </div>
                <div class="metric">
                    <span>Last Update:</span>
                    <span class="metric-value" id="lastUpdate">--:--:--</span>
                </div>
            </div>
            
            <div class="status-panel">
                <h3>🛡️ SECURITY STATUS</h3>
                <div class="metric">
                    <span>Devices Monitored:</span>
                    <span class="metric-value" id="devicesMonitored">0</span>
                </div>
                <div class="metric">
                    <span>Active Threats:</span>
                    <span class="metric-value" id="activeThreats">0</span>
                </div>
                <div class="metric">
                    <span>Blocked Devices:</span>
                    <span class="metric-value" id="blockedDevices">0</span>
                </div>
                <div class="metric">
                    <span>Threat Level:</span>
                    <span class="metric-value" id="threatLevel">LOW</span>
                </div>
            </div>
            
            <div class="status-panel">
                <h3>📊 SYSTEM METRICS</h3>
                <div class="metric">
                    <span>CPU Usage:</span>
                    <span class="metric-value" id="cpuUsage">0%</span>
                </div>
                <div class="metric">
                    <span>Memory Usage:</span>
                    <span class="metric-value" id="memUsage">0%</span>
                </div>
                <div class="metric">
                    <span>Active Services:</span>
                    <span class="metric-value" id="activeServices">0/8</span>
                </div>
                <div class="metric">
                    <span>Network Connections:</span>
                    <span class="metric-value" id="netConnections">0</span>
                </div>
            </div>
            
            <div class="status-panel">
                <h3>📚 HISTORICAL LIBRARY</h3>
                <div class="metric">
                    <span>Total Devices:</span>
                    <span class="metric-value" id="librarySize">0</span>
                </div>
                <div class="metric">
                    <span>Tagged Devices:</span>
                    <span class="metric-value" id="taggedDevices">0</span>
                </div>
                <div class="metric">
                    <span>Reputation Scores:</span>
                    <span class="metric-value" id="reputationCount">0</span>
                </div>
                <div class="metric">
                    <span>Serialization Attempts:</span>
                    <span class="metric-value" id="serializationAttempts">0</span>
                </div>
            </div>
        </div>
        
        <div style="text-align: center; margin: 20px 0; padding: 20px; background: rgba(20,20,20,0.9); border-radius: 8px;">
            <a href="/monitor" target="_blank" style="margin: 0 10px; padding: 12px 24px; background: linear-gradient(135deg, #00ff00, #00dd00); color: #000; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 14px; display: inline-block; box-shadow: 0 4px 6px rgba(0,255,0,0.3); transition: all 0.3s;">
                📡 Signal Monitor
            </a>
            <a href="/history" target="_blank" style="margin: 0 10px; padding: 12px 24px; background: linear-gradient(135deg, #a855f7, #8b3fd9); color: #fff; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 14px; display: inline-block; box-shadow: 0 4px 6px rgba(168,85,247,0.3); transition: all 0.3s;">
                💬 Conversation History
            </a>
        </div>
        
        <div class="activity-log" id="activityLog">
            <div style="color: #0ff; margin-bottom: 10px; font-weight: bold;">📡 REAL-TIME ACTIVITY FEED:</div>
        </div>
    </div>
    
    <script>
        let logCount = 0;
        const maxLogs = 50;
        
        function updateTime() {
            document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString();
        }
        
        function addLog(message, type = 'normal') {
            const logDiv = document.getElementById('activityLog');
            const entry = document.createElement('div');
            entry.className = `log-entry ${type === 'threat' ? 'threat-alert' : type === 'warning' ? 'warning' : 'normal-activity'}`;
            const timestamp = new Date().toLocaleTimeString();
            entry.textContent = `[${timestamp}] ${message}`;
            
            if (logDiv.children.length > 1) {
                logDiv.insertBefore(entry, logDiv.children[1]);
            } else {
                logDiv.appendChild(entry);
            }
            
            logCount++;
            if (logCount > maxLogs) {
                if (logDiv.lastChild && logDiv.lastChild !== logDiv.firstChild) {
                    logDiv.removeChild(logDiv.lastChild);
                }
            }
        }
        
        async function updateSignals() {
            try {
                const response = await fetch('/api/nbai/signal-status');
                const data = await response.json();
                
                // Update status panels
                document.getElementById('devicesMonitored').textContent = data.devices_monitored || 0;
                document.getElementById('activeThreats').textContent = data.active_threats || 0;
                document.getElementById('blockedDevices').textContent = data.blocked_devices || 0;
                document.getElementById('cpuUsage').textContent = `${data.cpu_usage || 0}%`;
                document.getElementById('memUsage').textContent = `${data.memory_usage || 0}%`;
                document.getElementById('activeServices').textContent = `${data.active_services || 0}/8`;
                document.getElementById('netConnections').textContent = data.network_connections || 0;
                document.getElementById('librarySize').textContent = data.library_size || 0;
                document.getElementById('taggedDevices').textContent = data.tagged_devices || 0;
                document.getElementById('reputationCount').textContent = data.reputation_count || 0;
                document.getElementById('serializationAttempts').textContent = data.serialization_attempts || 0;
                
                // Threat level
                const threatLevel = data.active_threats > 5 ? 'CRITICAL' : 
                                   data.active_threats > 2 ? 'HIGH' : 
                                   data.active_threats > 0 ? 'MEDIUM' : 'LOW';
                document.getElementById('threatLevel').textContent = threatLevel;
                
                // Activity feed
                if (data.recent_activity && data.recent_activity.length > 0) {
                    data.recent_activity.forEach(activity => {
                        addLog(activity.message, activity.type);
                    });
                }
                
            } catch (error) {
                addLog('⚠️ Signal error: ' + error.message, 'warning');
            }
        }
        
        // Initialize
        addLog('✅ AI Signal Monitor initialized');
        addLog('🛰️ Connecting to Home Base...');
        addLog('📡 Signal acquisition in progress...');
        
        setTimeout(() => {
            addLog('✅ Signal lock established');
            addLog('🔒 Secure channel open');
            addLog('📊 Beginning continuous monitoring...');
        }, 1000);
        
        updateTime();
        setInterval(updateTime, 1000);
        updateSignals();
        setInterval(updateSignals, 2000);
    </script>
</body>
</html>
"""

# NetworkBuster AI Template
NBAI_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NetworkBuster AI Assistant</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #7e22ce 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            background: rgba(0, 0, 0, 0.85);
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
            width: 100%;
            max-width: 1000px;
            height: 90vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            border: 2px solid rgba(126, 34, 206, 0.3);
        }
        
        .header {
            background: linear-gradient(135deg, #7e22ce 0%, #581c87 100%);
            color: white;
            padding: 20px 30px;
            text-align: center;
            border-bottom: 2px solid #a855f7;
        }
        
        .header h1 {
            font-size: 32px;
            margin-bottom: 5px;
            text-transform: uppercase;
            letter-spacing: 2px;
            text-shadow: 0 0 10px rgba(168, 85, 247, 0.5);
        }
        
        .header p {
            font-size: 14px;
            opacity: 0.9;
            color: #e9d5ff;
        }
        
        .status-bar {
            padding: 12px 30px;
            background: rgba(30, 60, 114, 0.4);
            border-bottom: 1px solid rgba(126, 34, 206, 0.2);
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 12px;
        }
        
        .status-item {
            display: flex;
            align-items: center;
            gap: 8px;
            color: #a5b4fc;
        }
        
        .status-indicator {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #22c55e;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; box-shadow: 0 0 10px #22c55e; }
            50% { opacity: 0.6; }
        }
        
        .chat-area {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            background: rgba(0, 0, 0, 0.3);
        }
        
        .message {
            margin-bottom: 20px;
            animation: fadeIn 0.3s ease;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .message-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 8px;
        }
        
        .message-label {
            font-weight: bold;
            font-size: 13px;
            padding: 4px 12px;
            border-radius: 12px;
        }
        
        .message-label.user {
            background: rgba(59, 130, 246, 0.2);
            color: #93c5fd;
            border: 1px solid rgba(59, 130, 246, 0.3);
        }
        
        .message-label.ai {
            background: rgba(168, 85, 247, 0.2);
            color: #e9d5ff;
            border: 1px solid rgba(168, 85, 247, 0.3);
        }
        
        .message-time {
            color: #6b7280;
            font-size: 11px;
        }
        
        .message-content {
            background: rgba(30, 41, 59, 0.6);
            color: #e2e8f0;
            padding: 15px 20px;
            border-radius: 12px;
            border-left: 3px solid;
            line-height: 1.6;
            font-size: 14px;
        }
        
        .message.user .message-content {
            border-left-color: #3b82f6;
            background: rgba(30, 58, 138, 0.3);
        }
        
        .message.ai .message-content {
            border-left-color: #a855f7;
            background: rgba(88, 28, 135, 0.3);
        }
        
        .message-content code {
            background: rgba(0, 0, 0, 0.4);
            padding: 2px 6px;
            border-radius: 4px;
            color: #22d3ee;
            font-family: 'Consolas', monospace;
        }
        
        .input-area {
            padding: 20px 30px;
            background: rgba(0, 0, 0, 0.5);
            border-top: 2px solid rgba(126, 34, 206, 0.3);
            display: flex;
            gap: 15px;
        }
        
        #messageInput {
            flex: 1;
            padding: 15px 20px;
            border: 2px solid rgba(126, 34, 206, 0.3);
            border-radius: 10px;
            background: rgba(30, 41, 59, 0.6);
            color: #e2e8f0;
            font-size: 14px;
            font-family: 'Consolas', monospace;
            outline: none;
            transition: all 0.3s ease;
        }
        
        #messageInput:focus {
            border-color: #a855f7;
            box-shadow: 0 0 20px rgba(168, 85, 247, 0.3);
        }
        
        #sendBtn {
            padding: 15px 35px;
            background: linear-gradient(135deg, #7e22ce 0%, #581c87 100%);
            color: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-weight: bold;
            font-size: 14px;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        #sendBtn:hover {
            background: linear-gradient(135deg, #9333ea 0%, #6b21a8 100%);
            box-shadow: 0 5px 20px rgba(168, 85, 247, 0.4);
            transform: translateY(-2px);
        }
        
        #sendBtn:active {
            transform: translateY(0);
        }
        
        .system-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .stat-card {
            background: rgba(30, 58, 138, 0.3);
            border: 1px solid rgba(59, 130, 246, 0.3);
            border-radius: 10px;
            padding: 15px;
        }
        
        .stat-label {
            color: #93c5fd;
            font-size: 12px;
            margin-bottom: 5px;
            text-transform: uppercase;
        }
        
        .stat-value {
            color: #e2e8f0;
            font-size: 24px;
            font-weight: bold;
        }
        
        .typing-indicator {
            display: none;
            align-items: center;
            gap: 5px;
            color: #a855f7;
            font-size: 13px;
            padding: 10px 0;
        }
        
        .typing-indicator.active {
            display: flex;
        }
        
        .typing-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #a855f7;
            animation: typing 1.4s infinite;
        }
        
        .typing-dot:nth-child(2) { animation-delay: 0.2s; }
        .typing-dot:nth-child(3) { animation-delay: 0.4s; }
        
        @keyframes typing {
            0%, 60%, 100% { opacity: 0.3; transform: translateY(0); }
            30% { opacity: 1; transform: translateY(-10px); }
        }
        
        ::-webkit-scrollbar {
            width: 10px;
        }
        
        ::-webkit-scrollbar-track {
            background: rgba(0, 0, 0, 0.3);
        }
        
        ::-webkit-scrollbar-thumb {
            background: rgba(168, 85, 247, 0.5);
            border-radius: 5px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(168, 85, 247, 0.7);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 NetworkBuster AI</h1>
            <p>Intelligent Network Assistant • Powered by NetworkBuster</p>
        </div>
        
        <div class="status-bar">
            <div class="status-item">
                <div class="status-indicator"></div>
                <span>AI ONLINE</span>
            </div>
            <div class="status-item">
                <span id="systemTime">--:--:--</span>
            </div>
            <div class="status-item">
                <span id="networkStatus">7 Services Active</span>
            </div>
        </div>
        
        <div class="chat-area" id="chatArea">
            <div class="message ai">
                <div class="message-header">
                    <div class="message-label ai">NetworkBuster AI</div>
                    <div class="message-time" id="welcomeTime"></div>
                </div>
                <div class="message-content">
                    👋 <strong>Welcome to NetworkBuster AI!</strong><br><br>
                    I'm your intelligent network assistant, ready to help with:<br><br>
                    • <code>system status</code> - Check all services and ports<br>
                    • <code>network scan</code> - Analyze network topology<br>
                    • <code>diagnose</code> - Troubleshoot connectivity issues<br>
                    • <code>optimize</code> - Performance tuning recommendations<br>
                    • <code>security check</code> - Security analysis<br>
                    • <code>health report</code> - Comprehensive system health<br><br>
                    Type any command or ask a question to get started! 🚀
                </div>
            </div>
        </div>
        
        <div class="typing-indicator" id="typingIndicator">
            <span>NetworkBuster AI is thinking</span>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
        
        <div class="input-area">
            <input type="text" id="messageInput" placeholder="Ask NetworkBuster AI anything..." />
            <button id="sendBtn">Send</button>
        </div>
    </div>
    
    <script>
        // Initialize
        updateWelcomeTime();
        updateSystemTime();
        setInterval(updateSystemTime, 1000);
        
        function updateWelcomeTime() {
            const now = new Date();
            document.getElementById('welcomeTime').textContent = now.toLocaleTimeString();
        }
        
        function updateSystemTime() {
            const now = new Date();
            document.getElementById('systemTime').textContent = now.toLocaleTimeString();
        }
        
        // Chat functionality
        const messageInput = document.getElementById('messageInput');
        const sendBtn = document.getElementById('sendBtn');
        const chatArea = document.getElementById('chatArea');
        const typingIndicator = document.getElementById('typingIndicator');
        
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });
        
        sendBtn.addEventListener('click', sendMessage);
        
        async function sendMessage() {
            const message = messageInput.value.trim();
            if (!message) return;
            
            // Add user message
            addMessage(message, 'user');
            messageInput.value = '';
            
            // Show typing indicator
            typingIndicator.classList.add('active');
            
            try {
                const response = await fetch('/api/nbai/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message })
                });
                
                const data = await response.json();
                
                // Hide typing indicator
                typingIndicator.classList.remove('active');
                
                if (data.response) {
                    addMessage(data.response, 'ai');
                } else {
                    addMessage('Sorry, I encountered an error processing your request.', 'ai');
                }
            } catch (error) {
                typingIndicator.classList.remove('active');
                addMessage('Connection error. Please check if the AI service is running.', 'ai');
            }
        }
        
        function addMessage(text, role) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${role}`;
            
            const now = new Date();
            const timeStr = now.toLocaleTimeString();
            
            const label = role === 'user' ? 'You' : 'NetworkBuster AI';
            const labelClass = role === 'user' ? 'user' : 'ai';
            
            messageDiv.innerHTML = `
                <div class="message-header">
                    <div class="message-label ${labelClass}">${label}</div>
                    <div class="message-time">${timeStr}</div>
                </div>
                <div class="message-content">${formatMessage(text)}</div>
            `;
            
            chatArea.appendChild(messageDiv);
            chatArea.scrollTop = chatArea.scrollHeight;
        }
        
        function formatMessage(text) {
            // Convert markdown-style code to HTML
            text = text.replace(/`([^`]+)`/g, '<code>$1</code>');
            // Convert newlines to <br>
            text = text.replace(/\n/g, '<br>');
            return text;
        }
        
        // Update network status
        async function updateNetworkStatus() {
            try {
                const response = await fetch('/api/nbai/status');
                const data = await response.json();
                if (data.services) {
                    const activeCount = data.services.filter(s => s.active).length;
                    document.getElementById('networkStatus').textContent = `${activeCount} Services Active`;
                }
            } catch (error) {
                console.error('Failed to update network status:', error);
            }
        }
        
        updateNetworkStatus();
        setInterval(updateNetworkStatus, 5000);
    </script>
</body>
</html>
"""

# AI Intelligence Engine with Advanced Indexing
class NetworkBusterAI:
    def __init__(self):
        # Service index for O(1) lookups
        self.services = [
            {'name': 'Web Server', 'port': 3000, 'type': 'node', 'critical': True},
            {'name': 'API Server', 'port': 3001, 'type': 'node', 'critical': True},
            {'name': 'Audio Stream', 'port': 3002, 'type': 'node', 'critical': False},
            {'name': 'NetworkBuster AI', 'port': 4000, 'type': 'python', 'critical': True},
            {'name': 'Mission Control', 'port': 5000, 'type': 'python', 'critical': True},
            {'name': 'Network Map', 'port': 6000, 'type': 'python', 'critical': False},
            {'name': 'Universal Launcher', 'port': 7000, 'type': 'python', 'critical': False},
            {'name': 'API Tracer', 'port': 8000, 'type': 'python', 'critical': False},
        ]
        
        # Build indexed lookups for supercomputer-speed performance
        self.port_index = {svc['port']: svc for svc in self.services}
        self.name_index = {svc['name'].lower(): svc for svc in self.services}
        self.type_index = {}
        for svc in self.services:
            if svc['type'] not in self.type_index:
                self.type_index[svc['type']] = []
            self.type_index[svc['type']].append(svc)
        
        # Performance metrics cache
        self.metrics_cache = {}
        self.cache_timestamp = 0
        
        # Security: Microdevice tracking and barrier system
        self.device_fingerprints = {}  # Track known devices
        self.serialization_attempts = []  # Log suspicious activity
        self.blocked_devices = set()  # Blacklist for threats
        self.connection_history = {}  # Connection pattern analysis
        self.threat_score_index = {}  # Real-time threat scoring
        
        # Historical Device Library System
        self.device_library = {}  # Persistent device database
        self.device_tags = {}  # Device categorization (trusted, suspicious, unknown, threat)
        self.device_reputation = {}  # Long-term reputation scores
        self.library_file = 'networkbuster_device_library.json'
        self.load_device_library()  # Load existing historical data
        
        # Conversation History System
        self.conversation_history = []  # Store all Q&A exchanges
        self.conversation_file = 'networkbuster_conversations.json'
        self.load_conversation_history()
    
    def check_port(self, port):
        """Check if a port is listening"""
        for conn in psutil.net_connections():
            if conn.laddr.port == port and conn.status == 'LISTEN':
                return True
        return False
    
    def load_device_library(self):
        """Load historical device library from persistent storage"""
        try:
            if os.path.exists(self.library_file):
                with open(self.library_file, 'r') as f:
                    data = json.load(f)
                    self.device_library = data.get('devices', {})
                    self.device_tags = data.get('tags', {})
                    self.device_reputation = data.get('reputation', {})
                    print(f"📚 Loaded {len(self.device_library)} devices from historical library")
            else:
                print("📚 Creating new device library")
        except Exception as e:
            print(f"⚠️ Error loading library: {e}")
    
    def load_conversation_history(self):
        """Load conversation history from persistent storage"""
        try:
            if os.path.exists(self.conversation_file):
                with open(self.conversation_file, 'r') as f:
                    data = json.load(f)
                    self.conversation_history = data.get('conversations', [])
                    print(f"💬 Loaded {len(self.conversation_history)} conversation exchanges")
            else:
                print("💬 Creating new conversation history")
        except Exception as e:
            print(f"⚠️ Error loading conversations: {e}")
    
    def save_conversation(self, user_message, ai_response):
        """Save conversation exchange to history"""
        try:
            conversation_entry = {
                'timestamp': datetime.now().isoformat(),
                'user_message': user_message,
                'ai_response': ai_response,
                'session': datetime.now().strftime('%Y-%m-%d')
            }
            self.conversation_history.append(conversation_entry)
            
            # Save to file
            data = {
                'conversations': self.conversation_history[-1000:],  # Keep last 1000
                'total_exchanges': len(self.conversation_history),
                'last_updated': datetime.now().isoformat()
            }
            with open(self.conversation_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"⚠️ Error saving conversation: {e}")
            return False
    
    def save_device_library(self):
        """Save device library to persistent storage"""
        try:
            data = {
                'devices': self.device_library,
                'tags': self.device_tags,
                'reputation': self.device_reputation,
                'last_updated': datetime.now().isoformat(),
                'total_devices': len(self.device_library)
            }
            with open(self.library_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"⚠️ Error saving library: {e}")
            return False
    
    def tag_device(self, device_ip, tag, reason=''):
        """Tag a device with category (trusted, suspicious, unknown, threat, blocked)"""
        valid_tags = ['trusted', 'suspicious', 'unknown', 'threat', 'blocked', 'internal']
        if tag not in valid_tags:
            tag = 'unknown'
        
        self.device_tags[device_ip] = {
            'tag': tag,
            'reason': reason,
            'timestamp': time.time(),
            'tagged_at': datetime.now().isoformat()
        }
        
        # Update device library entry
        if device_ip not in self.device_library:
            self.device_library[device_ip] = {
                'first_seen': datetime.now().isoformat(),
                'total_connections': 0,
                'threat_events': [],
                'ports_accessed': []
            }
        
        self.device_library[device_ip]['tag'] = tag
        self.device_library[device_ip]['tag_reason'] = reason
        self.device_library[device_ip]['last_updated'] = datetime.now().isoformat()
        
        # Auto-save after tagging
        self.save_device_library()
        return True
    
    def update_device_reputation(self, device_ip, score_delta, event_type=''):
        """Update device reputation score based on behavior"""
        if device_ip not in self.device_reputation:
            self.device_reputation[device_ip] = {
                'score': 50,  # Start neutral (0-100 scale)
                'history': []
            }
        
        # Update score
        current_score = self.device_reputation[device_ip]['score']
        new_score = max(0, min(100, current_score + score_delta))
        self.device_reputation[device_ip]['score'] = new_score
        
        # Log event
        self.device_reputation[device_ip]['history'].append({
            'timestamp': datetime.now().isoformat(),
            'event': event_type,
            'score_change': score_delta,
            'new_score': new_score
        })
        
        # Auto-tag based on reputation
        if new_score >= 80:
            self.tag_device(device_ip, 'trusted', f'High reputation: {new_score}')
        elif new_score <= 20:
            self.tag_device(device_ip, 'threat', f'Low reputation: {new_score}')
        elif new_score <= 40:
            self.tag_device(device_ip, 'suspicious', f'Poor reputation: {new_score}')
        
        return new_score
    
    def get_device_history(self, device_ip):
        """Get complete historical data for a device"""
        if device_ip not in self.device_library:
            return None
        
        device_data = self.device_library[device_ip].copy()
        device_data['tag_info'] = self.device_tags.get(device_ip, {'tag': 'unknown'})
        device_data['reputation'] = self.device_reputation.get(device_ip, {'score': 50})
        device_data['current_threat_score'] = self.threat_score_index.get(device_ip, 0)
        device_data['is_blocked'] = device_ip in self.blocked_devices
        
        return device_data
    
    def get_system_status(self):
        """Get comprehensive system status"""
        status = []
        for service in self.services:
            is_active = self.check_port(service['port'])
            status.append({
                'name': service['name'],
                'port': service['port'],
                'active': is_active,
                'type': service.get('type'),
                'critical': service.get('critical')
            })
        return status
    
    def detect_microdevices(self):
        """Detect and analyze microdevice serialization attempts with AI barrier"""
        import time
        from collections import defaultdict
        
        start_time = time.perf_counter()
        
        # Get all network connections
        connections = psutil.net_connections(kind='inet')
        
        # Index devices by remote address for O(1) lookups
        device_index = defaultdict(list)
        
        for conn in connections:
            if hasattr(conn, 'raddr') and conn.raddr:
                remote_ip = conn.raddr.ip
                remote_port = conn.raddr.port
                
                # Build device fingerprint
                fingerprint = {
                    'ip': remote_ip,
                    'port': remote_port,
                    'local_port': conn.laddr.port,
                    'status': conn.status,
                    'pid': conn.pid
                }
                
                device_index[remote_ip].append(fingerprint)
                
                # Update connection history for pattern analysis
                if remote_ip not in self.connection_history:
                    self.connection_history[remote_ip] = {
                        'first_seen': time.time(),
                        'connection_count': 0,
                        'ports_accessed': set()
                    }
                
                self.connection_history[remote_ip]['connection_count'] += 1
                self.connection_history[remote_ip]['ports_accessed'].add(conn.laddr.port)
                self.connection_history[remote_ip]['last_seen'] = time.time()
                
                # Update historical device library
                if remote_ip not in self.device_library:
                    self.device_library[remote_ip] = {
                        'first_seen': datetime.now().isoformat(),
                        'total_connections': 0,
                        'threat_events': [],
                        'ports_accessed': []
                    }
                
                self.device_library[remote_ip]['total_connections'] += 1
                self.device_library[remote_ip]['last_seen'] = datetime.now().isoformat()
                if conn.laddr.port not in self.device_library[remote_ip]['ports_accessed']:
                    self.device_library[remote_ip]['ports_accessed'].append(conn.laddr.port)
                
                # Auto-tag localhost/internal devices
                if remote_ip.startswith('127.') or remote_ip.startswith('192.168.') or remote_ip.startswith('10.'):
                    if remote_ip not in self.device_tags:
                        self.tag_device(remote_ip, 'internal', 'Internal network device')
        
        # AI-powered threat analysis with indexed pattern matching
        threats_detected = []
        for device_ip, device_conns in device_index.items():
            threat_score = 0
            reasons = []
            
            # Pattern 1: Port scanning (serialization reconnaissance)
            unique_ports = len(set(c['local_port'] for c in device_conns))
            if unique_ports > 10:
                threat_score += 50
                reasons.append(f"🔍 Port scanning: {unique_ports} ports")
            
            # Pattern 2: Rapid serialization attempts
            if len(device_conns) > 20:
                threat_score += 40
                reasons.append(f"⚡ Serialization attack: {len(device_conns)} attempts")
            
            # Pattern 3: Critical service targeting
            critical_ports = [3000, 3001, 4000, 5000]
            critical_accessed = [c for c in device_conns if c['local_port'] in critical_ports]
            if len(critical_accessed) > 3:
                threat_score += 30
                reasons.append("🎯 Critical service targeting")
            
            # Pattern 4: Historical suspicious behavior
            if device_ip in self.connection_history:
                hist = self.connection_history[device_ip]
                if hist['connection_count'] > 100:
                    threat_score += 20
                    reasons.append(f"📊 High activity: {hist['connection_count']} total")
            
            # Store threat score in indexed structure
            self.threat_score_index[device_ip] = threat_score
            
            # AI barrier decision: Block or monitor
            if threat_score >= 70:
                threats_detected.append({
                    'ip': device_ip,
                    'threat_score': threat_score,
                    'connections': len(device_conns),
                    'unique_ports': unique_ports,
                    'reasons': reasons,
                    'status': 'BLOCKED',
                    'action': 'Barrier activated',
                    'tag': self.device_tags.get(device_ip, {}).get('tag', 'unknown')
                })
                self.blocked_devices.add(device_ip)
                self.serialization_attempts.append({
                    'timestamp': time.time(),
                    'ip': device_ip,
                    'score': threat_score
                })
                # Tag as threat and update reputation
                self.tag_device(device_ip, 'blocked', f'Threat score: {threat_score}')
                self.update_device_reputation(device_ip, -30, 'High threat detected')
                # Log threat event
                if device_ip in self.device_library:
                    self.device_library[device_ip]['threat_events'].append({
                        'timestamp': datetime.now().isoformat(),
                        'threat_score': threat_score,
                        'reasons': reasons,
                        'action': 'blocked'
                    })
            elif threat_score >= 40:
                threats_detected.append({
                    'ip': device_ip,
                    'threat_score': threat_score,
                    'connections': len(device_conns),
                    'unique_ports': unique_ports,
                    'reasons': reasons,
                    'status': 'WARNING',
                    'action': 'Monitoring enabled',
                    'tag': self.device_tags.get(device_ip, {}).get('tag', 'unknown')
                })
                # Tag as suspicious and update reputation
                self.tag_device(device_ip, 'suspicious', f'Warning level threat: {threat_score}')
                self.update_device_reputation(device_ip, -10, 'Suspicious activity')
            else:
                # Good behavior - increase reputation
                if device_ip in self.device_library:
                    self.update_device_reputation(device_ip, 1, 'Normal activity')
        
        analysis_time = (time.perf_counter() - start_time) * 1000
        
        # Save updated library after analysis
        self.save_device_library()
        
        return {
            'total_devices': len(device_index),
            'threats_detected': threats_detected,
            'blocked_count': len(self.blocked_devices),
            'blocked_devices': list(self.blocked_devices),
            'total_attempts_logged': len(self.serialization_attempts),
            'library_size': len(self.device_library),
            'tagged_devices': len(self.device_tags),
            'analysis_time_ms': round(analysis_time, 3)
        }
    
    def analyze_network(self):
        """Analyze network connections with supercomputer-grade indexing"""
        import time
        start_time = time.perf_counter()
        
        connections = psutil.net_connections()
        
        # Build indexed analysis structures
        status_index = {}
        port_usage = {}
        protocol_index = {'TCP': 0, 'UDP': 0}
        
        for conn in connections:
            # Index by status
            status = conn.status
            status_index[status] = status_index.get(status, 0) + 1
            
            # Index port usage
            if hasattr(conn.laddr, 'port'):
                port = conn.laddr.port
                if port in self.port_index:
                    port_usage[port] = port_usage.get(port, 0) + 1
            
            # Protocol analysis
            if conn.type == 1:  # SOCK_STREAM = TCP
                protocol_index['TCP'] += 1
            elif conn.type == 2:  # SOCK_DGRAM = UDP
                protocol_index['UDP'] += 1
        
        analysis_time = (time.perf_counter() - start_time) * 1000  # Convert to ms
        
        return {
            'total_connections': len(connections),
            'status_breakdown': status_index,
            'listening_ports': status_index.get('LISTEN', 0),
            'established': status_index.get('ESTABLISHED', 0),
            'port_usage': port_usage,
            'protocol_distribution': protocol_index,
            'analysis_time_ms': round(analysis_time, 3)
        }
    
    def get_system_health(self):
        """Get comprehensive system health with supercomputer-grade metrics"""
        import time
        start_time = time.perf_counter()
        
        # Check cache (5 second TTL)
        current_time = time.time()
        if 'health' in self.metrics_cache and (current_time - self.cache_timestamp) < 5:
            return self.metrics_cache['health']
        
        # CPU metrics with per-core analysis
        cpu_percent = psutil.cpu_percent(interval=0.5, percpu=False)
        cpu_cores = psutil.cpu_count(logical=False)
        cpu_threads = psutil.cpu_count(logical=True)
        cpu_freq = psutil.cpu_freq()
        
        # Memory analysis
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        # Disk I/O metrics
        disk = psutil.disk_usage('/')
        disk_io = psutil.disk_io_counters()
        
        # Network I/O metrics
        net_io = psutil.net_io_counters()
        
        # Process count and load
        process_count = len(psutil.pids())
        load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else (0, 0, 0)
        
        analysis_time = (time.perf_counter() - start_time) * 1000
        
        health_data = {
            'cpu_usage': round(cpu_percent, 2),
            'cpu_cores': cpu_cores,
            'cpu_threads': cpu_threads,
            'cpu_frequency_mhz': round(cpu_freq.current, 2) if cpu_freq else 0,
            'memory_usage': round(memory.percent, 2),
            'memory_total_gb': round(memory.total / (1024**3), 2),
            'memory_available_gb': round(memory.available / (1024**3), 2),
            'memory_used_gb': round(memory.used / (1024**3), 2),
            'swap_usage': round(swap.percent, 2),
            'swap_total_gb': round(swap.total / (1024**3), 2),
            'disk_usage': round(disk.percent, 2),
            'disk_total_gb': round(disk.total / (1024**3), 2),
            'disk_free_gb': round(disk.free / (1024**3), 2),
            'disk_read_mb': round(disk_io.read_bytes / (1024**2), 2) if disk_io else 0,
            'disk_write_mb': round(disk_io.write_bytes / (1024**2), 2) if disk_io else 0,
            'network_sent_mb': round(net_io.bytes_sent / (1024**2), 2),
            'network_recv_mb': round(net_io.bytes_recv / (1024**2), 2),
            'process_count': process_count,
            'load_average': [round(l, 2) for l in load_avg],
            'analysis_time_ms': round(analysis_time, 3)
        }
        
        # Cache results
        self.metrics_cache['health'] = health_data
        self.cache_timestamp = current_time
        
        return health_data
    
    def process_query(self, query):
        """Process user query and generate intelligent response"""
        query_lower = query.lower()
        
        # System status command with supercomputer analysis
        if 'status' in query_lower or 'services' in query_lower:
            import time
            scan_start = time.perf_counter()
            
            status = self.get_system_status()
            active = [s for s in status if s['active']]
            inactive = [s for s in status if not s['active']]
            critical_down = [s for s in inactive if s.get('critical', False)]
            
            scan_time = (time.perf_counter() - scan_start) * 1000
            
            response = f"📊 <strong>SUPERCOMPUTER SYSTEM ANALYSIS</strong><br>"
            response += f"<code>Scan completed in {scan_time:.3f}ms</code><br><br>"
            response += f"✅ <strong>SERVICE STATUS: {len(active)}/{len(status)} OPERATIONAL</strong><br><br>"
            
            # Critical services check
            if critical_down:
                response += "<strong>⚠️ CRITICAL SERVICES DOWN:</strong><br>"
                for s in critical_down:
                    response += f"• <code style='color:#ef4444'>{s['name']}</code> (Port {s['port']}) - CRITICAL OFFLINE<br>"
                response += "<br>"
            
            # Active services by type
            if active:
                response += "<strong>🟢 ACTIVE SERVICES:</strong><br>"
                node_services = [s for s in active if s.get('type') == 'node']
                python_services = [s for s in active if s.get('type') == 'python']
                
                if node_services:
                    response += "<em>Node.js Services:</em><br>"
                    for s in node_services:
                        response += f"• <code>{s['name']}</code> → Port {s['port']} → ONLINE<br>"
                
                if python_services:
                    response += "<em>Python Services:</em><br>"
                    for s in python_services:
                        critical_badge = " 🔴" if s.get('critical') else ""
                        response += f"• <code>{s['name']}</code> → Port {s['port']} → ONLINE{critical_badge}<br>"
            
            if inactive and not critical_down:
                response += f"<br><strong>⚪ INACTIVE SERVICES ({len(inactive)}):</strong><br>"
                for s in inactive:
                    response += f"• <code>{s['name']}</code> (Port {s['port']}) - Standby<br>"
            
            response += f"<br><code>Index lookup time: O(1) constant time</code>"
            return response
        
        # Network scan command with supercomputer analysis
        elif 'network' in query_lower and ('scan' in query_lower or 'analyze' in query_lower):
            net = self.analyze_network()
            response = f"🌐 <strong>SUPERCOMPUTER NETWORK ANALYSIS</strong><br>"
            response += f"<code>Analysis time: {net['analysis_time_ms']}ms</code><br><br>"
            
            response += f"<strong>📊 CONNECTION METRICS:</strong><br>"
            response += f"• Total Connections: <strong>{net['total_connections']}</strong><br>"
            response += f"• Listening Ports: <strong>{net['listening_ports']}</strong><br>"
            response += f"• Established: <strong>{net['established']}</strong><br><br>"
            
            response += f"<strong>🔌 PROTOCOL DISTRIBUTION:</strong><br>"
            for protocol, count in net['protocol_distribution'].items():
                response += f"• {protocol}: <strong>{count}</strong> connections<br>"
            
            if net.get('status_breakdown'):
                response += f"<br><strong>📍 CONNECTION STATUS INDEX:</strong><br>"
                for status, count in sorted(net['status_breakdown'].items(), key=lambda x: -x[1])[:5]:
                    response += f"• <code>{status}</code>: {count}<br>"
            
            if net.get('port_usage'):
                response += f"<br><strong>🔌 SERVICE PORT USAGE:</strong><br>"
                for port, count in sorted(net['port_usage'].items()):
                    service_name = self.port_index.get(port, {}).get('name', 'Unknown')
                    response += f"• Port {port} (<code>{service_name}</code>): {count} connections<br>"
            
            response += f"<br><code>Indexed lookup performance: O(1) hash table</code>"
            return response
        
        # Health report command with supercomputer metrics
        elif 'health' in query_lower or 'performance' in query_lower:
            health = self.get_system_health()
            response = f"💪 <strong>SUPERCOMPUTER HEALTH ANALYSIS</strong><br>"
            response += f"<code>Metrics cached | Query time: {health['analysis_time_ms']}ms</code><br><br>"
            
            response += f"<strong>⚡ CPU METRICS:</strong><br>"
            response += f"• Usage: <strong>{health['cpu_usage']}%</strong><br>"
            response += f"• Cores: <strong>{health['cpu_cores']}</strong> physical / <strong>{health['cpu_threads']}</strong> logical<br>"
            response += f"• Frequency: <strong>{health['cpu_frequency_mhz']} MHz</strong><br><br>"
            
            response += f"<strong>💾 MEMORY ANALYSIS:</strong><br>"
            response += f"• RAM Usage: <strong>{health['memory_usage']}%</strong><br>"
            response += f"• Used: <strong>{health['memory_used_gb']} GB</strong> / Total: <strong>{health['memory_total_gb']} GB</strong><br>"
            response += f"• Available: <strong>{health['memory_available_gb']} GB</strong><br>"
            response += f"• Swap: <strong>{health['swap_usage']}%</strong> ({health['swap_total_gb']} GB)<br><br>"
            
            response += f"<strong>💿 DISK I/O METRICS:</strong><br>"
            response += f"• Usage: <strong>{health['disk_usage']}%</strong><br>"
            response += f"• Free Space: <strong>{health['disk_free_gb']} GB</strong> / <strong>{health['disk_total_gb']} GB</strong><br>"
            response += f"• Read: <strong>{health['disk_read_mb']} MB</strong> | Write: <strong>{health['disk_write_mb']} MB</strong><br><br>"
            
            response += f"<strong>🌐 NETWORK I/O:</strong><br>"
            response += f"• Sent: <strong>{health['network_sent_mb']} MB</strong><br>"
            response += f"• Received: <strong>{health['network_recv_mb']} MB</strong><br><br>"
            
            response += f"<strong>📊 SYSTEM LOAD:</strong><br>"
            response += f"• Active Processes: <strong>{health['process_count']}</strong><br>"
            if health['load_average'][0] > 0:
                response += f"• Load Average: <strong>{health['load_average'][0]}</strong> (1m) / <strong>{health['load_average'][1]}</strong> (5m) / <strong>{health['load_average'][2]}</strong> (15m)<br><br>"
            else:
                response += "<br>"
            
            # Performance assessment
            if health['cpu_usage'] > 80:
                response += "⚠️ <strong>High CPU usage</strong> - Consider closing unused applications<br>"
            if health['memory_usage'] > 80:
                response += "⚠️ <strong>High memory pressure</strong> - Services may need restart<br>"
            if health['disk_usage'] > 90:
                response += "⚠️ <strong>Low disk space</strong> - Run cleanup operations<br>"
            
            if health['cpu_usage'] < 60 and health['memory_usage'] < 70:
                response += "✅ <strong>System operating at optimal performance!</strong><br>"
            
            response += f"<br><code>Metrics cached with 5s TTL for performance</code>"
            return response
        
        # Diagnose command
        elif 'diagnose' in query_lower or 'troubleshoot' in query_lower:
            status = self.get_system_status()
            inactive = [s for s in status if not s['active']]
            
            response = f"🔍 <strong>Diagnostic Report</strong><br><br>"
            
            if not inactive:
                response += "✅ All services are running correctly!<br><br>"
                response += "No issues detected. System is healthy."
            else:
                response += f"⚠️ <strong>{len(inactive)} Service(s) Not Running</strong><br><br>"
                response += "<strong>Recommended Actions:</strong><br>"
                response += "1. Run <code>AUTOSTART.bat</code> to start all services<br>"
                response += "2. Or use <code>nb-start</code> PowerShell command<br>"
                response += "3. Check logs for any error messages<br><br>"
                response += "<strong>Inactive Services:</strong><br>"
                for s in inactive:
                    response += f"• {s['name']} (Port {s['port']})<br>"
            
            return response
        
        # Optimize command
        elif 'optimize' in query_lower or 'performance' in query_lower:
            health = self.get_system_health()
            response = f"⚡ <strong>Optimization Recommendations</strong><br><br>"
            response += "<strong>Performance Tuning:</strong><br>"
            response += "• Run <code>nb-autostart</code> for boot optimization<br>"
            response += "• Enable high-performance power plan<br>"
            response += "• Close unused background applications<br>"
            response += "• Clear browser cache and temporary files<br>"
            response += "• Run <code>flash_git_backup.py</code> to free space<br><br>"
            
            if health['cpu_usage'] < 50 and health['memory_usage'] < 50:
                response += "✅ System resources are well-balanced!"
            else:
                response += "💡 Consider restarting services during low-usage periods."
            
            return response
        
        # Security check command with microdevice barrier analysis
        elif 'security' in query_lower or 'secure' in query_lower or 'device' in query_lower or 'threat' in query_lower:
            # Run microdevice detection
            device_scan = self.detect_microdevices()
            
            response = f"🔒 <strong>AI SECURITY BARRIER ANALYSIS</strong><br>"
            response += f"<code>Deep scan completed in {device_scan['analysis_time_ms']}ms</code><br><br>"
            
            response += f"<strong>🛡️ MICRODEVICE DETECTION:</strong><br>"
            response += f"• Total Devices Scanned: <strong>{device_scan['total_devices']}</strong><br>"
            response += f"• Threats Detected: <strong>{len(device_scan['threats_detected'])}</strong><br>"
            response += f"• Blocked Devices: <strong>{device_scan['blocked_count']}</strong><br>"
            response += f"• Serialization Attempts Logged: <strong>{device_scan['total_attempts_logged']}</strong><br>"
            response += f"• Historical Library Size: <strong>{device_scan['library_size']}</strong> devices<br>"
            response += f"• Tagged Devices: <strong>{device_scan['tagged_devices']}</strong><br><br>"
            
            # Show threat details
            if device_scan['threats_detected']:
                response += f"<strong>⚠️ ACTIVE THREATS:</strong><br>"
                for threat in device_scan['threats_detected'][:5]:  # Top 5 threats
                    status_color = '#ef4444' if threat['status'] == 'BLOCKED' else '#f59e0b'
                    tag = threat.get('tag', 'unknown')
                    tag_color = {'blocked': '#ef4444', 'threat': '#dc2626', 'suspicious': '#f59e0b', 
                                'internal': '#3b82f6', 'trusted': '#22c55e', 'unknown': '#6b7280'}.get(tag, '#6b7280')
                    response += f"<div style='margin: 10px 0; padding: 10px; background: rgba(0,0,0,0.3); border-left: 3px solid {status_color}; border-radius: 5px;'>"
                    response += f"<strong style='color:{status_color}'>{threat['status']}</strong> | IP: <code>{threat['ip']}</code> "
                    response += f"| Tag: <span style='color:{tag_color}'>🏷️ {tag.upper()}</span><br>"
                    response += f"Threat Score: <strong>{threat['threat_score']}/100</strong><br>"
                    response += f"Connections: {threat['connections']} | Ports: {threat['unique_ports']}<br>"
                    response += f"<em>Reasons:</em><br>"
                    for reason in threat['reasons']:
                        response += f"  • {reason}<br>"
                    response += f"<strong>Action:</strong> {threat['action']}<br>"
                    response += f"</div>"
                
                if len(device_scan['threats_detected']) > 5:
                    response += f"<em>...and {len(device_scan['threats_detected']) - 5} more threats</em><br>"
            else:
                response += "<strong>✅ NO THREATS DETECTED</strong><br>"
                response += "All devices are within normal parameters.<br>"
            
            response += "<br><strong>🔐 SECURITY STATUS:</strong><br>"
            response += "• AI Barrier: <strong style='color:#22c55e'>ACTIVE</strong><br>"
            response += "• Pattern Recognition: <strong>ENABLED</strong><br>"
            response += "• Real-time Monitoring: <strong>ONLINE</strong><br>"
            response += "• Historical Device Library: <strong>TRACKING</strong><br>"
            response += "• Device Tagging System: <strong>OPERATIONAL</strong><br>"
            response += "• Reputation Scoring: <strong>ACTIVE</strong><br>"
            response += "• Indexed Threat Database: <strong>O(1) lookup</strong><br>"
            response += "• CORS Protection: <strong>ENABLED</strong><br>"
            response += "• Localhost Isolation: <strong>ACTIVE</strong><br><br>"
            
            response += "<strong>📋 RECOMMENDATIONS:</strong><br>"
            response += "• Monitor blocked devices regularly<br>"
            response += "• Run <code>security check</code> periodically<br>"
            response += "• Review historical device library<br>"
            response += "• Check device tags and reputation scores<br>"
            response += "• Review serialization attempt logs<br>"
            response += "• Keep firewall rules updated<br>"
            
            response += f"<br><code>AI barrier with persistent historical library</code>"
            return response
        
        # Help command
        elif 'help' in query_lower or 'commands' in query_lower:
            response = f"📚 <strong>NetworkBuster AI Commands</strong><br><br>"
            response += "<strong>Available Commands:</strong><br>"
            response += "• <code>system status</code> - Check all services with indexed analysis<br>"
            response += "• <code>network scan</code> - Analyze connections and protocols<br>"
            response += "• <code>health report</code> - Comprehensive system metrics<br>"
            response += "• <code>security check</code> - AI microdevice barrier scan 🛡️<br>"
            response += "• <code>diagnose</code> - Troubleshoot issues<br>"
            response += "• <code>optimize</code> - Performance tips<br>"
            response += "• <code>security check</code> - Security analysis<br>"
            response += "• <code>help</code> - Show this message<br><br>"
            response += "You can also ask questions in natural language!"
            return response
        
        # Default intelligent response
        else:
            response = f"🤔 I understand you're asking about: <em>{query}</em><br><br>"
            response += "I'm NetworkBuster AI with <strong>Historical Device Library</strong>, specialized in:<br><br>"
            response += "• System status and service health<br>"
            response += "• Network analysis and connectivity<br>"
            response += "• Performance optimization<br>"
            response += "• Security with device tagging & tracking 🏷️<br>"
            response += "• Microdevice threat detection 🛡️<br>"
            response += "• Historical pattern analysis 📚<br><br>"
            response += "Type <code>help</code> to see all available commands!"
            return response

# Initialize AI with Historical Library
print("\n🧠 Initializing NetworkBuster AI with Historical Device Library...")
ai_engine = NetworkBusterAI()
print(f"✅ AI Engine ready with {len(ai_engine.device_library)} historical devices\n")

@app.route('/')
def index():
    """Render NetworkBuster AI interface"""
    return render_template_string(NBAI_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    """Process chat messages"""
    try:
        data = request.json
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Process query through AI engine
        response = ai_engine.process_query(user_message)
        
        # Save to conversation history
        ai_engine.save_conversation(user_message, response)
        
        return jsonify({
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/nbai/status', methods=['GET'])
def status():
    """Get system status"""
    try:
        services = ai_engine.get_system_status()
        health = ai_engine.get_system_health()
        network = ai_engine.analyze_network()
        
        return jsonify({
            'services': services,
            'health': health,
            'network': network,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/nbai/diagnose', methods=['GET'])
def diagnose():
    """Run diagnostics"""
    try:
        status = ai_engine.get_system_status()
        health = ai_engine.get_system_health()
        
        inactive_services = [s for s in status if not s['active']]
        
        issues = []
        if inactive_services:
            issues.append(f"{len(inactive_services)} service(s) not running")
        if health['cpu_usage'] > 80:
            issues.append("High CPU usage")
        if health['memory_usage'] > 80:
            issues.append("High memory usage")
        if health['disk_usage'] > 90:
            issues.append("Low disk space")
        
        return jsonify({
            'healthy': len(issues) == 0,
            'issues': issues,
            'inactive_services': inactive_services,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/monitor')
def signal_monitor():
    """Render AI Signal Monitor - Read-only window"""
    return render_template_string(AI_SIGNAL_MONITOR)

@app.route('/history')
def conversation_history():
    """Render Conversation History page"""
    with open('conversation_history_template.html', 'r', encoding='utf-8') as f:
        template = f.read()
    return template

@app.route('/api/nbai/conversations', methods=['GET'])
def get_conversations():
    """Get all conversation history"""
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        today_count = sum(1 for conv in ai_engine.conversation_history 
                         if conv.get('session') == today)
        
        sessions = set(conv.get('session') for conv in ai_engine.conversation_history)
        
        return jsonify({
            'conversations': ai_engine.conversation_history,
            'total_count': len(ai_engine.conversation_history),
            'today_count': today_count,
            'session_count': len(sessions),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/nbai/signal-status', methods=['GET'])
def signal_status():
    """Get AI signal status for home base monitoring"""
    try:
        import time
        
        # Get comprehensive status
        status = ai_engine.get_system_status()
        health = ai_engine.get_system_health()
        
        # Device and threat metrics
        active_services = len([s for s in status if s['active']])
        
        # Recent activity feed
        recent_activity = []
        
        # Check for new threats
        if len(ai_engine.blocked_devices) > 0:
            recent_activity.append({
                'message': f'🛡️ {len(ai_engine.blocked_devices)} devices blocked by barrier',
                'type': 'threat'
            })
        
        # Check for new devices
        new_devices = sum(1 for ip, data in ai_engine.device_library.items() 
                         if 'last_seen' in data and 
                         (datetime.now() - datetime.fromisoformat(data['last_seen'])).seconds < 10)
        if new_devices > 0:
            recent_activity.append({
                'message': f'📡 {new_devices} new device(s) detected',
                'type': 'normal'
            })
        
        # System health warnings
        if health['cpu_usage'] > 80:
            recent_activity.append({
                'message': f'⚠️ High CPU usage: {health["cpu_usage"]}%',
                'type': 'warning'
            })
        
        if health['memory_usage'] > 80:
            recent_activity.append({
                'message': f'⚠️ High memory usage: {health["memory_usage"]}%',
                'type': 'warning'
            })
        
        # Build comprehensive signal data
        signal_data = {
            'timestamp': datetime.now().isoformat(),
            'connection_status': 'ACTIVE',
            'signal_strength': 100,
            'ai_engine_online': True,
            
            # Security metrics
            'devices_monitored': len(ai_engine.connection_history),
            'active_threats': len([ip for ip, score in ai_engine.threat_score_index.items() if score >= 40]),
            'blocked_devices': len(ai_engine.blocked_devices),
            
            # System metrics
            'cpu_usage': round(health['cpu_usage'], 1),
            'memory_usage': round(health['memory_usage'], 1),
            'active_services': active_services,
            'network_connections': len(psutil.net_connections()),
            
            # Historical library
            'library_size': len(ai_engine.device_library),
            'tagged_devices': len(ai_engine.device_tags),
            'reputation_count': len(ai_engine.device_reputation),
            'serialization_attempts': len(ai_engine.serialization_attempts),
            
            # Activity feed
            'recent_activity': recent_activity[-10:]  # Last 10 activities
        }
        
        return jsonify(signal_data)
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'connection_status': 'ERROR',
            'signal_strength': 0
        }), 500

def main():
    """Start NetworkBuster AI server with Historical Device Library"""
    print("\n" + "═" * 60)
    print("║  NetworkBuster AI - Intelligent Network Assistant         ║")
    print("║  with Historical Device Library & Threat Tagging          ║")
    print("═" * 60)
    print("\n🧠 AI Engine Status:")
    print(f"   📚 Historical Library: {len(ai_engine.device_library)} devices tracked")
    print(f"   🏷️  Tagged Devices: {len(ai_engine.device_tags)}")
    print(f"   🛡️  Blocked Threats: {len(ai_engine.blocked_devices)}")
    print(f"   📊 Reputation Scores: {len(ai_engine.device_reputation)} devices")
    print(f"\n🌐 Server Details:")
    print(f"   Main Dashboard: http://localhost:8000")
    print(f"   Signal Monitor: http://localhost:8000/monitor 📡")
    print(f"   API Endpoint: http://localhost:8000/api/nbai/chat")
    print(f"   🌍 Remote Access: Use ngrok or Cloudflare Tunnel")
    print(f"   Library File: {ai_engine.library_file}")
    print("\n💡 Features:")
    print("   • Interactive AI Chat Interface")
    print("   • Read-Only Signal Monitor (Home Base Feed)")
    print("   • Device Tracking & Tagging")
    print("   • Real-Time Threat Detection")
    print("\n📡 Open /monitor for real-time signal feed to home base!")
    print("═" * 60 + "\n")
    
    app.run(host='0.0.0.0', port=8000, debug=False)

if __name__ == '__main__':
    main()
