/**
 * Scroll Navigation Component
 * Provides smooth scroll navigation through page sections
 * NetworkBuster.net Staging Build
 */

const SECTIONS = [
    { id: 'hero', label: 'Home', icon: '🏠' },
    { id: 'overview', label: 'Architecture', icon: '🏗️' },
    { id: 'technical', label: 'Specifications', icon: '📊' },
    { id: 'calculator', label: 'Calculator', icon: '🧮' },
    { id: 'data', label: 'Data', icon: '📈' },
    { id: 'operations', label: 'Operations', icon: '⚙️' },
];

class ScrollNavigation {
    constructor() {
        this.activeSection = 'hero';
        this.scrollTimeout = null;
        this.init();
    }
    
    init() {
        this.createNavElement();
        this.createProgressBar();
        this.setupScrollListener();
        this.setupKeyboardNav();
        this.updateActiveSection();
    }
    
    createNavElement() {
        const nav = document.createElement('nav');
        nav.className = 'scroll-nav';
        nav.innerHTML = `
            <div class="scroll-nav-container">
                <div class="scroll-nav-brand">
                    <span class="brand-icon">🌙</span>
                    <span class="brand-text">NetworkBuster<span class="staging-badge">.NET STAGING</span></span>
                </div>
                <div class="scroll-nav-links">
                    ${SECTIONS.map(section => `
                        <a href="#${section.id}" class="scroll-nav-link" data-section="${section.id}">
                            <span class="nav-icon">${section.icon}</span>
                            <span class="nav-label">${section.label}</span>
                        </a>
                    `).join('')}
                </div>
                <div class="scroll-nav-actions">
                    <span class="scroll-indicator">
                        <span class="scroll-percent">0%</span>
                    </span>
                    <button class="scroll-to-top" title="Scroll to top">↑</button>
                </div>
            </div>
        `;
        
        document.body.prepend(nav);
        
        // Add click handlers
        nav.querySelectorAll('.scroll-nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const sectionId = link.dataset.section;
                this.scrollToSection(sectionId);
            });
        });
        
        nav.querySelector('.scroll-to-top').addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
        
        this.navElement = nav;
    }
    
    createProgressBar() {
        const progressBar = document.createElement('div');
        progressBar.className = 'scroll-progress';
        progressBar.innerHTML = '<div class="scroll-progress-fill"></div>';
        document.body.prepend(progressBar);
        this.progressBar = progressBar.querySelector('.scroll-progress-fill');
    }
    
    setupScrollListener() {
        window.addEventListener('scroll', () => {
            this.updateScrollProgress();
            this.updateActiveSection();
            this.toggleNavVisibility();
        }, { passive: true });
    }
    
    setupKeyboardNav() {
        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowDown' && e.altKey) {
                e.preventDefault();
                this.navigateToNextSection();
            } else if (e.key === 'ArrowUp' && e.altKey) {
                e.preventDefault();
                this.navigateToPrevSection();
            }
        });
    }
    
    updateScrollProgress() {
        const scrollTop = window.scrollY;
        const docHeight = document.documentElement.scrollHeight - window.innerHeight;
        const scrollPercent = (scrollTop / docHeight) * 100;
        
        this.progressBar.style.width = `${scrollPercent}%`;
        this.navElement.querySelector('.scroll-percent').textContent = `${Math.round(scrollPercent)}%`;
    }
    
    updateActiveSection() {
        const scrollPos = window.scrollY + 150;
        
        let currentSection = 'hero';
        SECTIONS.forEach(section => {
            const element = document.getElementById(section.id);
            if (element && element.offsetTop <= scrollPos) {
                currentSection = section.id;
            }
        });
        
        if (currentSection !== this.activeSection) {
            this.activeSection = currentSection;
            this.navElement.querySelectorAll('.scroll-nav-link').forEach(link => {
                link.classList.toggle('active', link.dataset.section === currentSection);
            });
        }
    }
    
    toggleNavVisibility() {
        const scrollTop = window.scrollY;
        this.navElement.classList.toggle('scrolled', scrollTop > 100);
        this.navElement.querySelector('.scroll-to-top').classList.toggle('visible', scrollTop > 300);
    }
    
    scrollToSection(sectionId) {
        const element = document.getElementById(sectionId);
        if (element) {
            const offset = sectionId === 'hero' ? 0 : element.offsetTop - 80;
            window.scrollTo({ top: offset, behavior: 'smooth' });
        }
    }
    
    navigateToNextSection() {
        const currentIndex = SECTIONS.findIndex(s => s.id === this.activeSection);
        if (currentIndex < SECTIONS.length - 1) {
            this.scrollToSection(SECTIONS[currentIndex + 1].id);
        }
    }
    
    navigateToPrevSection() {
        const currentIndex = SECTIONS.findIndex(s => s.id === this.activeSection);
        if (currentIndex > 0) {
            this.scrollToSection(SECTIONS[currentIndex - 1].id);
        }
    }
}

// Initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => new ScrollNavigation());
} else {
    new ScrollNavigation();
}

// Export for module usage
window.ScrollNavigation = ScrollNavigation;
