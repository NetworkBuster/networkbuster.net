/**
 * App Slider Navigation - NetworkBuster.net
 * Provides quick access to all applications via a slide-out navigation panel
 */

(function() {
  'use strict';

  const apps = [
    {
      id: 'home',
      icon: '🏠',
      label: 'Home',
      title: 'Home',
      desc: 'Main landing page',
      url: 'index.html'
    },
    {
      id: 'dashboard',
      icon: '📊',
      label: 'Dash',
      title: 'Dashboard',
      desc: 'System monitoring & metrics',
      url: 'dashboard.html'
    },
    {
      id: 'control',
      icon: '🎛️',
      label: 'Control',
      title: 'Control Panel',
      desc: 'Server management & controls',
      url: 'control-panel.html'
    },
    { divider: true },
    {
      id: 'ai-world',
      icon: '🤖',
      label: 'AI',
      title: 'AI World',
      desc: 'AI models & neural networks',
      url: 'ai-world.html'
    },
    {
      id: 'audio-lab',
      icon: '🎵',
      label: 'Audio',
      title: 'Audio Lab',
      desc: 'Audio processing & streaming',
      url: 'audio-lab.html'
    },
    {
      id: 'overlay',
      icon: '🛰️',
      label: 'Overlay',
      title: 'Real-Time Overlay',
      desc: '3D visualization & maps',
      url: 'http://localhost:5173/overlay/',
      external: true
    },
    { divider: true },
    {
      id: 'projects',
      icon: '🚀',
      label: 'Projects',
      title: 'Projects',
      desc: 'Portfolio & showcases',
      url: 'projects.html'
    },
    {
      id: 'packages',
      icon: '📦',
      label: 'Packages',
      title: 'Packages',
      desc: 'NPM & software packages',
      url: 'packages.html'
    },
    {
      id: 'hud',
      icon: '🎯',
      label: 'HUD',
      title: 'HUD Display',
      desc: 'Heads-up display interface',
      url: 'hud.html'
    },
    { divider: true },
    {
      id: 'docs',
      icon: '📚',
      label: 'Docs',
      title: 'Documentation',
      desc: 'Guides & API reference',
      url: 'documentation.html'
    },
    {
      id: 'flash',
      icon: '⚡',
      label: 'Flash',
      title: 'Flash Commands',
      desc: 'Quick command reference',
      url: 'flash-commands.html'
    },
    {
      id: 'tech',
      icon: '💻',
      label: 'Tech',
      title: 'Technology',
      desc: 'Tech stack & tools',
      url: 'technology.html'
    },
    { divider: true },
    {
      id: 'auth',
      icon: '🔐',
      label: 'Auth',
      title: 'Auth Portal',
      desc: 'Login & registration',
      url: 'auth.html'
    },
    {
      id: 'about',
      icon: 'ℹ️',
      label: 'About',
      title: 'About Us',
      desc: 'Company information',
      url: 'about.html'
    },
    {
      id: 'contact',
      icon: '✉️',
      label: 'Contact',
      title: 'Contact',
      desc: 'Get in touch',
      url: 'contact.html'
    }
  ];

  function getCurrentPage() {
    const path = window.location.pathname;
    const page = path.split('/').pop() || 'index.html';
    return page;
  }

  function createSlider() {
    const currentPage = getCurrentPage();
    
    const slider = document.createElement('nav');
    slider.className = 'app-slider';
    slider.setAttribute('aria-label', 'Application Navigation');

    // Toggle button
    const toggle = document.createElement('button');
    toggle.className = 'app-slider-toggle';
    toggle.setAttribute('aria-label', 'Toggle navigation slider');
    toggle.innerHTML = `
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="15 18 9 12 15 6"></polyline>
      </svg>
    `;
    toggle.onclick = () => slider.classList.toggle('collapsed');

    // Content container
    const content = document.createElement('div');
    content.className = 'app-slider-content';

    // Title
    const title = document.createElement('div');
    title.className = 'app-slider-title';
    title.textContent = 'Apps';
    content.appendChild(title);

    // App items
    apps.forEach(app => {
      if (app.divider) {
        const divider = document.createElement('div');
        divider.className = 'app-slider-divider';
        content.appendChild(divider);
        return;
      }

      const item = document.createElement('a');
      item.className = 'app-slider-item';
      item.setAttribute('data-app', app.id);
      item.href = app.url;
      
      if (app.external) {
        item.target = '_blank';
        item.rel = 'noopener noreferrer';
      }

      // Check if current page
      if (currentPage === app.url || (currentPage === '' && app.url === 'index.html')) {
        item.classList.add('active');
      }

      item.innerHTML = `
        <span class="app-slider-icon">${app.icon}</span>
        <span class="app-slider-label">${app.label}</span>
        <div class="app-slider-tooltip">
          <div class="app-slider-tooltip-title">${app.title}</div>
          <div class="app-slider-tooltip-desc">${app.desc}</div>
        </div>
      `;

      content.appendChild(item);
    });

    slider.appendChild(toggle);
    slider.appendChild(content);

    return slider;
  }

  function injectStyles() {
    if (document.querySelector('link[href*="app-slider.css"]')) return;
    
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = 'app-slider.css';
    document.head.appendChild(link);
  }

  function init() {
    // Don't inject if already exists
    if (document.querySelector('.app-slider')) return;

    injectStyles();
    
    // Wait for styles to load
    setTimeout(() => {
      const slider = createSlider();
      document.body.appendChild(slider);
      
      // Keyboard navigation
      document.addEventListener('keydown', (e) => {
        // Alt + S to toggle slider
        if (e.altKey && e.key.toLowerCase() === 's') {
          e.preventDefault();
          slider.classList.toggle('collapsed');
        }
      });

      // Save collapsed state
      const savedState = localStorage.getItem('appSliderCollapsed');
      if (savedState === 'true') {
        slider.classList.add('collapsed');
      }

      slider.querySelector('.app-slider-toggle').addEventListener('click', () => {
        localStorage.setItem('appSliderCollapsed', slider.classList.contains('collapsed'));
      });

    }, 100);
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Export for manual control
  window.AppSlider = {
    show: () => document.querySelector('.app-slider')?.classList.remove('collapsed'),
    hide: () => document.querySelector('.app-slider')?.classList.add('collapsed'),
    toggle: () => document.querySelector('.app-slider')?.classList.toggle('collapsed')
  };

})();
