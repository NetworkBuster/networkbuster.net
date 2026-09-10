// NetworkBuster Lunar Recycling System - Interactive Functionality

// Processing data for different materials
const processingData = {
    plastic: {
        name: 'Mixed Plastics',
        efficiency: 0.875, // 87.5% average
        timePerKg: 100, // minutes
        energyPerKg: 3.0, // kWh
        outputs: ['Pyrolysis oil (65%)', 'Hydrocarbon gases (20%)', 'Carbon black (15%)']
    },
    aluminum: {
        name: 'Aluminum',
        efficiency: 0.965,
        timePerKg: 85,
        energyPerKg: 0.85,
        outputs: ['Aluminum ingots (97%)', 'Dross/waste (3%)']
    },
    steel: {
        name: 'Steel/Iron',
        efficiency: 0.925,
        timePerKg: 45,
        energyPerKg: 0.15,
        outputs: ['Compacted blocks (93%)', 'Iron powder (7%)']
    },
    glass: {
        name: 'Glass',
        efficiency: 0.825,
        timePerKg: 30,
        energyPerKg: 0.075,
        outputs: ['Glass cullet (83%)', 'Fine powder (17%)']
    },
    organic: {
        name: 'Organics',
        efficiency: 0.75,
        timePerKg: 1440, // 1 day average
        energyPerKg: 0.15,
        outputs: ['Compost (45%)', 'Biogas methane (25%)', 'CO₂ (20%)', 'Water (10%)']
    },
    ewaste: {
        name: 'Electronics',
        efficiency: 0.675,
        timePerKg: 200,
        energyPerKg: 2.2,
        outputs: ['Copper (12%)', 'Precious metals (0.5%)', 'Aluminum (8%)', 'Plastics (30%)', 'Other (50%)']
    }
};

// Calculator function
function calculateProcessing() {
    const materialType = document.getElementById('materialType').value;
    const inputMass = parseFloat(document.getElementById('inputMass').value);

    if (!inputMass || inputMass < 500 || inputMass > 50000) {
        alert('Please enter a valid mass between 500g and 50kg');
        return;
    }

    const data = processingData[materialType];
    const inputKg = inputMass / 1000;

    // Calculate results
    const outputMass = (inputKg * data.efficiency * 1000).toFixed(0);
    const processTime = Math.ceil(inputKg * data.timePerKg);
    const energyRequired = (inputKg * data.energyPerKg).toFixed(2);
    const efficiency = (data.efficiency * 100).toFixed(1);

    // Format time
    let timeStr;
    if (processTime < 60) {
        timeStr = `${processTime} minutes`;
    } else if (processTime < 1440) {
        const hours = Math.floor(processTime / 60);
        const mins = processTime % 60;
        timeStr = `${hours}h ${mins}m`;
    } else {
        const days = Math.floor(processTime / 1440);
        const hours = Math.floor((processTime % 1440) / 60);
        timeStr = `${days}d ${hours}h`;
    }

    // Update UI
    document.getElementById('outputMass').textContent = `${outputMass}g`;
    document.getElementById('processTime').textContent = timeStr;
    document.getElementById('energyReq').textContent = `${energyRequired} kWh`;
    document.getElementById('efficiency').textContent = `${efficiency}%`;
    document.getElementById('products').textContent = data.outputs.join(', ');

    // Add animation
    const results = document.querySelectorAll('.result-value');
    results.forEach((el, index) => {
        el.style.animation = 'none';
        setTimeout(() => {
            el.style.animation = `fadeInUp 0.5s ease ${index * 0.1}s backwards`;
        }, 10);
    });
}

// Smooth scrolling for navigation
document.addEventListener('DOMContentLoaded', function () {
    const navLinks = document.querySelectorAll('.nav-link');

    navLinks.forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault();

            // Remove active class from all links
            navLinks.forEach(l => l.classList.remove('active'));

            // Add active class to clicked link
            this.classList.add('active');

            // Scroll to section
            const targetId = this.getAttribute('href');
            const targetSection = document.querySelector(targetId);

            if (targetSection) {
                window.scrollTo({
                    top: targetSection.offsetTop - 80,
                    behavior: 'smooth'
                });
            }
        });
    });

    // Update active nav on scroll
    window.addEventListener('scroll', function () {
        let current = '';
        const sections = document.querySelectorAll('.section');

        sections.forEach(section => {
            const sectionTop = section.offsetTop - 100;
            const sectionHeight = section.clientHeight;

            if (window.pageYOffset >= sectionTop &&
                window.pageYOffset < sectionTop + sectionHeight) {
                current = '#' + section.getAttribute('id');
            }
        });

        navLinks.forEach(link => {
            if (link.getAttribute('href').startsWith('#')) {
                link.classList.remove('active');
                if (link.getAttribute('href') === current) {
                    link.classList.add('active');
                }
            }
        });
    });

    // Highlight active nav link based on current path
    const currentPath = window.location.pathname;
    const allLinks = document.querySelectorAll('.nav-link, .dropdown-item');
    allLinks.forEach(link => {
        const h = link.getAttribute('href');
        if (!h) return;

        // Clean paths for comparison
        const linkPath = h.split('#')[0].split('?')[0];
        const normalizedPath = currentPath === '/' ? '/index.html' : currentPath;
        const normalizedLink = linkPath === '/' ? '/index.html' : linkPath;

        if (normalizedPath === normalizedLink || normalizedPath.endsWith(normalizedLink)) {
            if (!h.startsWith('#')) {
                link.classList.add('active');
                const parentDropdown = link.closest('.nav-dropdown');
                if (parentDropdown) {
                    const toggle = parentDropdown.querySelector('.dropdown-toggle');
                    if (toggle) toggle.classList.add('active');
                }
            }
        }
    });

    // Architecture card interactions
    const archCards = document.querySelectorAll('.arch-card');

    archCards.forEach(card => {
        card.addEventListener('click', function () {
            const module = this.getAttribute('data-module');
            showModuleDetails(module);
        });
    });

    // Initialize charts (simple placeholders)
    initializeCharts();

    // Start Live Pulse Monitoring
    if (document.getElementById('pulse-grid')) {
        updateAllServerStatuses();
        setInterval(updateAllServerStatuses, 30000); // Update every 30 seconds
    }
});

const SERVER_MAP = {
    dashboard: { name: 'Dashboard', port: 3000, path: '/' },
    api: { name: 'API Server', port: 3001, path: '/api/status' }, // Changed to status for better data
    audio: { name: 'Audio Lab', port: 3002, path: '/api/audio/status' },
    auth: { name: 'Auth Portal', port: 3003, path: '/api/auth/health' },
    flash: { name: 'Flash Upgrade', port: 3004, path: '/' },
    bot: { name: 'Chatbot AI', port: 3005, path: '/api/chat/health' },
    security: { name: 'Security Monitor', port: 3006, path: '/api/security/status' },
    timeline: { name: 'Timeline Tracker', port: 3007, path: '/api/timeline/present' }
};

async function checkServerStatus(serverKey) {
    const server = SERVER_MAP[serverKey];
    const url = `http://localhost:${server.port}${server.path}`;

    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 3000);

        const response = await fetch(url, {
            method: 'GET',
            signal: controller.signal,
            mode: 'cors' // Use cors to read response body
        });

        clearTimeout(timeoutId);

        if (response.ok) {
            const data = await response.json().catch(() => ({})); // Attempt to parse JSON, default to empty object on failure
            return { online: true, data };
        }
        return { online: false };
    } catch (e) {
        // Fallback for CORS/no-body issues, try with no-cors to at least detect if server is up
        try {
            const resp = await fetch(url, { mode: 'no-cors' });
            // If no-cors succeeds, it means the server is reachable, even if we can't read its response
            return { online: true, data: {} };
        } catch (err) {
            return { online: false };
        }
    }
}

async function updateServerUI(serverKey, result) {
    const card = document.querySelector(`.pulse-card[data-server="${serverKey}"]`);
    if (!card) return;

    const isOnline = result.online;
    card.classList.remove('loading', 'online', 'offline');
    card.classList.add(isOnline ? 'online' : 'offline');

    const statusEl = card.querySelector('.pulse-status');
    const portEl = card.querySelector('.pulse-port');

    if (isOnline) {
        statusEl.textContent = 'ONLINE';

        // Add live data if available
        let extraInfo = '';
        if (serverKey === 'api' && result.data.systemInfo) {
            const mem = (result.data.systemInfo.memoryUsage.heapUsed / (1024 * 1024)).toFixed(1); // Convert bytes to MB
            extraInfo = `<div style="font-size:0.75rem; color:var(--text-dim); margin-top:5px;">RAM: ${mem}MB</div>`;
        } else if (serverKey === 'timeline' && result.data.snapshot) {
            const branch = result.data.snapshot.git.branch || 'N/A';
            extraInfo = `<div style="font-size:0.75rem; color:var(--text-dim); margin-top:5px;">Branch: ${branch}</div>`;
        } else if (serverKey === 'bot' && result.data.status) {
            extraInfo = `<div style="font-size:0.75rem; color:var(--text-dim); margin-top:5px;">State: ${result.data.status}</div>`;
        }

        // Clear old info and add new
        const oldExtra = card.querySelector('.pulse-extra');
        if (oldExtra) oldExtra.remove();

        if (extraInfo) {
            const infoDiv = document.createElement('div');
            infoDiv.className = 'pulse-extra';
            infoDiv.innerHTML = extraInfo;
            card.appendChild(infoDiv);
        }
    } else {
        statusEl.textContent = 'OFFLINE';
        const oldExtra = card.querySelector('.pulse-extra');
        if (oldExtra) oldExtra.remove();
    }
}

async function updateAllServerStatuses() {
    console.log('Refreshing system pulse with live data...');
    const keys = Object.keys(SERVER_MAP);

    // Process sequentially to update UI as results come in
    for (const key of keys) {
        const result = await checkServerStatus(key);
        updateServerUI(key, result);
    }
}

// Module details modal (simplified version)
function showModuleDetails(module) {
    const moduleInfo = {
        ipm: 'Input Processing Module: Handles material intake with spectroscopic analysis and AI-powered classification.',
        msu: 'Material Separation Unit: Uses optical, magnetic, and density-based sorting for >95% accuracy.',
        thermal: 'Thermal Processing Chamber: Pyrolysis system for plastics operating at 150-400°C in vacuum.',
        mechanical: 'Mechanical Processing Chamber: Grinding, milling, and compaction for metals and glass.',
        biological: 'Biological Processing Chamber: Composting and anaerobic digestion for organic waste.',
        output: 'Output Management System: Automated packaging with RFID tracking and inventory management.'
    };

    alert(moduleInfo[module] || 'Module information not available.');
}

// Chart initialization (placeholder - would use Chart.js or similar in production)
function initializeCharts() {
    const charts = document.querySelectorAll('.chart-container canvas');

    charts.forEach(canvas => {
        const ctx = canvas.getContext('2d');
        const chartType = canvas.id;

        // Clear the canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Set canvas size
        canvas.width = canvas.parentElement.clientWidth - 32;
        canvas.height = 250;

        // Draw placeholder
        ctx.fillStyle = '#94a3b8';
        ctx.font = '14px Inter';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(
            `${chartType.replace('Chart', '').toUpperCase()} DATA VISUALIZATION`,
            canvas.width / 2,
            canvas.height / 2 - 10
        );
        ctx.font = '12px Inter';
        ctx.fillStyle = '#64748b';
        ctx.fillText(
            'Interactive charts available in full deployment',
            canvas.width / 2,
            canvas.height / 2 + 15
        );

        // Draw simple visualization based on chart type
        drawSimpleChart(ctx, chartType, canvas.width, canvas.height);
    });
}

// Simple chart drawing function
function drawSimpleChart(ctx, chartType, width, height) {
    ctx.strokeStyle = '#6366f1';
    ctx.lineWidth = 2;
    ctx.beginPath();

    const padding = 40;
    const chartWidth = width - 2 * padding;
    const chartHeight = height - 2 * padding - 60;

    if (chartType === 'tempChart') {
        // Temperature sine wave
        for (let x = 0; x <= chartWidth; x++) {
            const progress = x / chartWidth;
            const temp = Math.sin(progress * Math.PI * 2) * 0.4 + 0.5;
            const y = padding + chartHeight - (temp * chartHeight);

            if (x === 0) {
                ctx.moveTo(padding + x, y);
            } else {
                ctx.lineTo(padding + x, y);
            }
        }
    } else if (chartType === 'powerChart') {
        // Power generation curve
        for (let x = 0; x <= chartWidth; x++) {
            const progress = x / chartWidth;
            let power;
            if (progress < 0.45) {
                power = Math.max(0, Math.sin(progress * Math.PI * 2.2) * 0.5 + 0.5);
            } else {
                power = 0;
            }
            const y = padding + chartHeight - (power * chartHeight);

            if (x === 0) {
                ctx.moveTo(padding + x, y);
            } else {
                ctx.lineTo(padding + x, y);
            }
        }
    } else if (chartType === 'throughputChart') {
        // Bar chart simulation
        const materials = 6;
        const barWidth = chartWidth / (materials * 2);
        const values = [0.7, 0.5, 0.4, 0.3, 0.8, 0.2];

        ctx.fillStyle = '#6366f1';
        values.forEach((value, i) => {
            const x = padding + (i * 2 + 0.5) * barWidth;
            const barHeight = value * chartHeight;
            const y = padding + chartHeight - barHeight;
            ctx.fillRect(x, y, barWidth * 0.8, barHeight);
        });
        return; // Skip stroke for bar chart
    } else if (chartType === 'efficiencyChart') {
        // Efficiency bars
        const materials = 6;
        const barWidth = chartWidth / (materials * 2);
        const values = [0.88, 0.97, 0.93, 0.83, 0.75, 0.68];

        ctx.fillStyle = '#10b981';
        values.forEach((value, i) => {
            const x = padding + (i * 2 + 0.5) * barWidth;
            const barHeight = value * chartHeight;
            const y = padding + chartHeight - barHeight;
            ctx.fillRect(x, y, barWidth * 0.8, barHeight);
        });
        return;
    }

    ctx.stroke();
}

// Keyboard shortcuts
document.addEventListener('keydown', function (e) {
    // Ctrl/Cmd + K to focus search (if implemented)
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        // Focus search input if exists
    }

    // Escape to close modals (if implemented)
    if (e.key === 'Escape') {
        // Close any open modals
    }
});

// Add intersection observer for scroll animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.animation = 'fadeInUp 0.8s ease forwards';
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

// Observe all cards and important elements
document.addEventListener('DOMContentLoaded', () => {
    const elements = document.querySelectorAll(
        '.arch-card, .env-card, .data-card, .timeline-item'
    );

    elements.forEach(el => {
        el.style.opacity = '0';
        observer.observe(el);
    });
});

// Console easter egg
console.log('%c🌙 NetworkBuster Lunar Recycling System',
    'font-size: 20px; font-weight: bold; color: #6366f1;');
console.log('%cVersion 1.0.0 | Payload: 500g+ | Recovery: 95%%',
    'font-size: 12px; color: #94a3b8;');
console.log('%cFor more information, visit the documentation.',
    'font-size: 12px; color: #94a3b8;');

// Export functions for external use
window.NLRS = {
    calculateProcessing,
    processingData,
    initializeCharts
};
