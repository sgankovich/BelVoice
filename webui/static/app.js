/* Dashboard primitives */
(function () {
  const root = document.documentElement;
  const modeToggle = document.getElementById('mode-toggle');
  const styleToggle = document.getElementById('style-toggle');
  const accentSelect = document.getElementById('accent-select');
  const menuBtn = document.getElementById('menu-btn');
  const sidebar = document.getElementById('sidebar');
  const sidebarBackdrop = document.getElementById('sidebar-backdrop');
  const searchTrigger = document.getElementById('search-trigger');
  const cpOverlay = document.getElementById('cp-overlay');
  const cpDialog = document.getElementById('cp-dialog');
  const cpInput = document.getElementById('cp-input');
  const cpList = document.getElementById('cp-list');

  const commands = (typeof window !== 'undefined' && window.UI_COMMANDS) || [
    { name: 'Go to Dashboard', icon: 'layout-dashboard', href: '/', shortcut: 'G D' },
    { name: 'Pipeline — Fetch & Select', icon: 'rss', href: '/step/1', shortcut: 'G 1' },
    { name: 'Pipeline — Generate Digest', icon: 'layers', href: '/step/2', shortcut: 'G 2' },
    { name: 'Pipeline — Script & Edit', icon: 'file-text', href: '/step/3', shortcut: 'G 3' },
    { name: 'Pipeline — Generate Audio', icon: 'headphones', href: '/step/4', shortcut: 'G 4' },
    { name: 'Open Settings', icon: 'settings', href: '/settings', shortcut: 'G S' },
    { name: 'Toggle day/night', icon: 'moon', action: 'mode', shortcut: 'T M' },
    { name: 'Toggle modern/simple', icon: 'layout-dashboard', action: 'style', shortcut: 'T S' }
  ];

  const icons = {
    'layout-dashboard': '<rect x="3" y="3" width="7" height="9" rx="1"/><rect x="14" y="3" width="7" height="5" rx="1"/><rect x="14" y="12" width="7" height="9" rx="1"/><rect x="3" y="16" width="7" height="5" rx="1"/>',
    'rss': '<path d="M4 11a9 9 0 0 1 9 9"/><path d="M4 4a16 16 0 0 1 16 16"/><circle cx="5" cy="19" r="1"/>',
    'file-text': '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><line x1="10" y1="9" x2="8" y2="9"/>',
    'headphones': '<path d="M3 18v-6a9 9 0 0 1 18 0v6"/><path d="M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3zM3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z"/>',
    'settings': '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>',
    'moon': '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>',
    'sun': '<circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>',
    'command': '<path d="M18 3a3 3 0 0 0-3 3v12a3 3 0 0 0 3 3 3 3 0 0 0 3-3 3 3 0 0 0-3-3H6a3 3 0 0 0-3 3 3 3 0 0 0 3 3 3 3 0 0 0 3-3V6a3 3 0 0 0-3-3 3 3 0 0 0-3 3 3 3 0 0 0 3 3h12a3 3 0 0 0 3-3 3 3 0 0 0-3-3z"/>',
    'type': '<polyline points="4 7 4 4 20 4 20 7"/><line x1="9" y1="20" x2="15" y2="20"/><line x1="12" y1="4" x2="12" y2="20"/>',
    'search': '<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>',
    'check': '<polyline points="20 6 9 17 4 12"/>',
    'x': '<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>',
    'mic': '<path d="M12 1a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/>',
    'sparkles': '<path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/><path d="M5 3v4"/><path d="M19 17v4"/><path d="M3 5h4"/><path d="M17 19h4"/>',
    'zap': '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>'
  };

  function iconSvg(name, size) {
    const path = icons[name] || icons['check'];
    return `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${path}</svg>`;
  }

  const MODES = ['dark', 'light'];
  const STYLES = ['modern', 'simple'];
  const ACCENTS = ['lime', 'coral', 'purple', 'blue', 'amber', 'pink', 'teal'];
  const MODE_ICONS = { dark: 'moon', light: 'sun' };
  const STYLE_ICONS = { modern: 'layout-dashboard', simple: 'type' };

  function applyMode(mode) {
    root.setAttribute('data-mode', mode);
    localStorage.setItem('app-mode', mode);
    if (modeToggle) modeToggle.innerHTML = iconSvg(MODE_ICONS[mode] || 'moon', 20);
  }

  function applyStyle(style) {
    root.setAttribute('data-style', style);
    localStorage.setItem('app-style', style);
    if (styleToggle) styleToggle.innerHTML = iconSvg(STYLE_ICONS[style] || 'layout-dashboard', 20);
  }

  function applyAccent(accent) {
    root.setAttribute('data-accent', accent);
    localStorage.setItem('app-accent', accent);
    if (accentSelect) accentSelect.value = accent;
  }

  const savedMode = localStorage.getItem('app-mode') || 'dark';
  const savedStyle = localStorage.getItem('app-style') || 'modern';
  const savedAccent = localStorage.getItem('app-accent') || 'lime';
  applyMode(savedMode);
  applyStyle(savedStyle);
  applyAccent(savedAccent);

  if (modeToggle) {
    modeToggle.addEventListener('click', () => {
      const next = root.getAttribute('data-mode') === 'dark' ? 'light' : 'dark';
      applyMode(next);
    });
  }

  if (styleToggle) {
    styleToggle.addEventListener('click', () => {
      const next = root.getAttribute('data-style') === 'modern' ? 'simple' : 'modern';
      applyStyle(next);
    });
  }

  if (accentSelect) {
    accentSelect.addEventListener('change', (e) => applyAccent(e.target.value));
  }

  function toggleSidebar(show) {
    if (!sidebar) return;
    sidebar.classList.toggle('open', show);
    if (sidebarBackdrop) sidebarBackdrop.classList.toggle('open', show);
  }

  if (menuBtn) menuBtn.addEventListener('click', () => toggleSidebar(true));
  if (sidebarBackdrop) sidebarBackdrop.addEventListener('click', () => toggleSidebar(false));

  function closeCommandPalette() {
    cpOverlay.classList.remove('open');
    cpDialog.classList.remove('open');
    document.body.style.overflow = '';
  }

  function openCommandPalette() {
    cpOverlay.classList.add('open');
    cpDialog.classList.add('open');
    document.body.style.overflow = 'hidden';
    renderCommands();
    cpInput.value = '';
    cpInput.focus();
  }

  function renderCommands(filter) {
    const term = (filter || '').toLowerCase();
    const items = commands.filter(c => c.name.toLowerCase().includes(term) || c.shortcut.toLowerCase().includes(term));
    if (!items.length) {
      const emptyText = (typeof window !== 'undefined' && window.UI_TEXT && window.UI_TEXT.no_matching_commands) || 'No matching commands';
      cpList.innerHTML = '<div class="cp-empty">' + emptyText + '</div>';
      return;
    }
    cpList.innerHTML = items.map((c, i) => `
      <div class="cp-item ${i === 0 ? 'active' : ''}" data-index="${i}" data-href="${c.href || ''}" data-action="${c.action || ''}">
        <span class="cp-item-icon">${iconSvg(c.icon, 18)}</span>
        <span class="cp-item-text">${c.name}</span>
        <span class="cp-shortcut">${c.shortcut}</span>
      </div>
    `).join('');
    activeIndex = 0;
  }

  let activeIndex = 0;

  function setActive(idx) {
    const items = cpList.querySelectorAll('.cp-item');
    items.forEach((el, i) => el.classList.toggle('active', i === idx));
    activeIndex = idx;
    items[idx]?.scrollIntoView({ block: 'nearest' });
  }

  function execute(itemEl) {
    const action = itemEl.dataset.action;
    if (action === 'mode') {
      const next = root.getAttribute('data-mode') === 'dark' ? 'light' : 'dark';
      applyMode(next);
      closeCommandPalette();
      return;
    }
    if (action === 'style') {
      const next = root.getAttribute('data-style') === 'modern' ? 'simple' : 'modern';
      applyStyle(next);
      closeCommandPalette();
      return;
    }
    const href = itemEl.dataset.href;
    if (href) {
      window.location.href = href;
      return;
    }
    if (action) {
      document.dispatchEvent(new CustomEvent('belvoice:command', { detail: action }));
      closeCommandPalette();
    }
  }

  if (cpList) {
    cpList.addEventListener('click', (e) => {
      const item = e.target.closest('.cp-item');
      if (item) execute(item);
    });
  }

  if (cpInput) {
    cpInput.addEventListener('input', (e) => renderCommands(e.target.value));
    cpInput.addEventListener('keydown', (e) => {
      const items = cpList.querySelectorAll('.cp-item');
      if (e.key === 'ArrowDown') { e.preventDefault(); setActive((activeIndex + 1) % items.length); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); setActive((activeIndex - 1 + items.length) % items.length); }
      else if (e.key === 'Enter') { e.preventDefault(); items[activeIndex] && execute(items[activeIndex]); }
      else if (e.key === 'Escape') { e.preventDefault(); closeCommandPalette(); }
    });
  }

  if (cpOverlay) cpOverlay.addEventListener('click', closeCommandPalette);

  document.addEventListener('keydown', (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
      e.preventDefault();
      openCommandPalette();
    }
    if (e.key === 'Escape') {
      if (cpDialog.classList.contains('open')) closeCommandPalette();
      if (sidebar && sidebar.classList.contains('open')) toggleSidebar(false);
    }
  });

  if (searchTrigger) {
    searchTrigger.addEventListener('click', openCommandPalette);
    searchTrigger.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); openCommandPalette(); } });
  }

  document.addEventListener('click', (e) => {
    if (e.target.closest('.sidebar') || e.target.closest('.menu-btn')) return;
    if (window.innerWidth < 1024 && sidebar && sidebar.classList.contains('open')) {
      toggleSidebar(false);
    }
  });

  // Live progress panel via Server-Sent Events
  const progressCard = document.getElementById('progress-card');
  if (progressCard) {
    const jobId = progressCard.dataset.jobId;
    const nextStep = progressCard.dataset.nextStep;
    const currentPath = progressCard.dataset.currentPath;
    const progressBar = document.getElementById('progress-bar');
    const progressLogs = document.getElementById('progress-logs');
    const progressTitle = document.getElementById('progress-title');
    const progressSub = document.getElementById('progress-sub');
    const progressSpinner = document.getElementById('progress-spinner');
    const progressActions = document.getElementById('progress-actions');
    const continueBtn = document.getElementById('progress-continue');
    const retryBtn = document.getElementById('progress-retry');

    function addLog(text, isError) {
      const time = new Date().toLocaleTimeString();
      const row = document.createElement('div');
      row.className = 'progress-log' + (isError ? ' error' : '');
      row.innerHTML = '<span class="timestamp">' + time + '</span><span class="text">' + text + '</span>';
      progressLogs.appendChild(row);
      progressLogs.scrollTop = progressLogs.scrollHeight;
    }

    addLog(window.UI_TEXT && window.UI_TEXT.please_wait ? window.UI_TEXT.please_wait : 'Starting...', false);

    const source = new EventSource('/events/' + encodeURIComponent(jobId));
    source.onmessage = function (e) {
      try {
        const data = JSON.parse(e.data);
        if (data.percent !== undefined && progressBar) {
          progressBar.style.width = Math.max(0, Math.min(100, data.percent)) + '%';
        }
        if (data.message) {
          addLog(data.message, data.error);
          if (progressSub) progressSub.textContent = data.message;
        }
        if (data.done) {
          source.close();
          if (progressSpinner) progressSpinner.style.display = 'none';
          if (progressActions) progressActions.style.display = 'flex';
          if (data.error) {
            if (progressTitle) progressTitle.textContent = window.UI_TEXT && window.UI_TEXT.error || 'Error';
            if (continueBtn) continueBtn.style.display = 'none';
            if (retryBtn) {
              retryBtn.style.display = 'inline-flex';
              retryBtn.href = currentPath || window.location.pathname;
            }
          } else {
            if (progressTitle) progressTitle.textContent = window.UI_TEXT && window.UI_TEXT.done || 'Done';
            if (continueBtn) {
              continueBtn.style.display = 'inline-flex';
              const step = data.next_step || nextStep;
              continueBtn.href = step ? '/step/' + encodeURIComponent(step) : '/';
              setTimeout(function () { window.location.href = continueBtn.href; }, 250);
            }
            if (retryBtn) retryBtn.style.display = 'none';
          }
        }
      } catch (err) {
        console.error('Progress event parse error', err);
      }
    };
    source.onerror = function () {
      addLog('Connection error. Please refresh the page.', true);
      if (progressSpinner) progressSpinner.style.display = 'none';
    };
  }

  // Digest preview: copy and toggle rendered / Markdown source
  const copyDigestBtn = document.getElementById('copy-digest');
  const toggleDigestBtn = document.getElementById('toggle-digest-view');
  const renderedView = document.getElementById('digest-rendered');
  const sourceView = document.getElementById('digest-source');

  if (copyDigestBtn && sourceView) {
    copyDigestBtn.addEventListener('click', function () {
      const text = sourceView.textContent;
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).catch(function () {});
      } else {
        const ta = document.createElement('textarea');
        ta.value = text;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
      }
    });
  }

  if (toggleDigestBtn && renderedView && sourceView) {
    toggleDigestBtn.addEventListener('click', function () {
      const showingSource = toggleDigestBtn.classList.toggle('show-source');
      renderedView.style.display = showingSource ? 'none' : 'block';
      sourceView.style.display = showingSource ? 'block' : 'none';
    });
  }

  // Script editor copy button
  const copyScriptBtn = document.getElementById('copy-script');
  const scriptTextarea = document.getElementById('script');
  if (copyScriptBtn && scriptTextarea) {
    copyScriptBtn.addEventListener('click', function () {
      const text = scriptTextarea.value;
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).catch(function () {});
      } else {
        const ta = document.createElement('textarea');
        ta.value = text;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
      }
    });
  }
})();
