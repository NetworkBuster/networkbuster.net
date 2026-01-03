/**
 * Shared Navigation Component for NetworkBuster Website
 * Auto-injects navigation and footer into all pages
 */

const PAGES = [
    { path: 'index.html', label: 'Home', icon: '🏠' },
    { path: 'about.html', label: 'About', icon: 'ℹ️' },
    { path: 'projects.html', label: 'Projects', icon: '🚀' },
    { path: 'technology.html', label: 'Technology', icon: '⚡' },
    { path: 'documentation.html', label: 'Docs', icon: '📖' },
    { path: 'contact.html', label: 'Contact', icon: '✉️' }
];

const APPS = [
    { path: 'dashboard.html', label: 'Dashboard', icon: '📊' },
    { path: 'control-panel.html', label: 'Control Panel', icon: '🎛️' },
    { path: 'ai-world.html', label: 'AI World', icon: '🤖' },
    { path: 'audio-lab.html', label: 'Audio Lab', icon: '🎵' },
    { path: 'auth.html', label: 'Auth Portal', icon: '🔐' }
];

const TOOLS = [
    { path: 'flash-commands.html', label: 'Flash Commands', icon: '⚡' },
    { path: 'packages.html', label: 'Packages', icon: '📦' },
    { path: 'hud.html', label: 'Function HUD', icon: '🛰️' },
    { path: 'overlay.html', label: 'Overlay', icon: '🌐' },
    { path: 'recycle.html', label: 'Recycle', icon: '♻️' }
];

function getCurrentPage() {
    const path = window.location.pathname;
    const filename = path.split('/').pop() || 'index.html';
    return filename;
}

function generateNavigation() {
    const currentPage = getCurrentPage();
    
    let navHTML = `
    <nav class="site-nav">
        <div class="nav-container">
            <a href="index.html" class="nav-brand">🌙 NetworkBuster</a>
            <div class="nav-links">
                ${PAGES.map(page => `
                    <a href="${page.path}" class="nav-link ${currentPage === page.path ? 'active' : ''}">
                        ${page.icon} ${page.label}
                    </a>
                `).join('')}
                
                <div class="nav-dropdown">
                    <span class="nav-link dropdown-toggle">🎮 Apps ▼</span>
                    <div class="dropdown-menu">
                        ${APPS.map(app => `
                            <a href="${app.path}" class="dropdown-item ${currentPage === app.path ? 'active' : ''}">
                                ${app.icon} ${app.label}
                            </a>
                        `).join('')}
                    </div>
                </div>
                
                <div class="nav-dropdown">
                    <span class="nav-link dropdown-toggle">🛠️ Tools ▼</span>
                    <div class="dropdown-menu">
                        ${TOOLS.map(tool => `
                            <a href="${tool.path}" class="dropdown-item ${currentPage === tool.path ? 'active' : ''}">
                                ${tool.icon} ${tool.label}
                            </a>
                        `).join('')}
                    </div>
                </div>
            </div>
        </div>
    </nav>`;
    
    return navHTML;
}

function generateFooter() {
    return `
    <footer class="site-footer">
        <div class="footer-links">
            ${PAGES.map(page => `<a href="${page.path}" class="footer-link">${page.label}</a>`).join('')}
        </div>
        <p>&copy; ${new Date().getFullYear()} NetworkBuster Research Division. All rights reserved.</p>
    </footer>`;
}

function injectNavigation() {
    // Skip injection if page already has a header (like index.html)
    const existingHeader = document.querySelector('header.header, .main-nav');
    if (existingHeader) {
        // Still inject the app slider
        injectAppSlider();
        return; // Page has its own navigation
    }
    
    // Inject CSS if not already present
    if (!document.querySelector('link[href="nav-shared.css"]')) {
        const cssLink = document.createElement('link');
        cssLink.rel = 'stylesheet';
        cssLink.href = 'nav-shared.css';
        document.head.appendChild(cssLink);
    }
    
    // Inject navigation at the start of body
    const nav = document.createElement('div');
    nav.innerHTML = generateNavigation();
    document.body.insertBefore(nav.firstElementChild, document.body.firstChild);
    
    // Inject footer at the end of body (replace existing footer if present)
    const existingFooter = document.querySelector('footer');
    if (existingFooter) {
        existingFooter.outerHTML = generateFooter();
    } else {
        const footer = document.createElement('div');
        footer.innerHTML = generateFooter();
        document.body.appendChild(footer.firstElementChild);
    }
    
    // Inject app slider
    injectAppSlider();
}

function injectAppSlider() {
    // Skip if already injected
    if (document.querySelector('.app-slider')) return;
    
    // Inject app slider CSS
    if (!document.querySelector('link[href="app-slider.css"]')) {
        const sliderCss = document.createElement('link');
        sliderCss.rel = 'stylesheet';
        sliderCss.href = 'app-slider.css';
        document.head.appendChild(sliderCss);
    }
    
    // Load and inject app slider JS
    if (!document.querySelector('script[src="app-slider.js"]')) {
        const sliderScript = document.createElement('script');
        sliderScript.src = 'app-slider.js';
        document.body.appendChild(sliderScript);
    }
}

// Auto-inject when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', injectNavigation);
} else {
    injectNavigation();
}

// Export for manual use
window.NetworkBusterNav = {
    PAGES,
    APPS,
    TOOLS,
    generateNavigation,
    generateFooter,
    injectNavigation,
    injectAppSlider
};
