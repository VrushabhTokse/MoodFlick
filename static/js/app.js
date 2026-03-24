/**
 * app.js
 * Global UI behaviour:
 *  - Sticky navbar shadow
 *  - Hamburger mobile menu
 *  - Flash message auto-dismiss
 *  - Scroll-reveal (fade-up class)
 *  - Toast notification system
 *  - Movie card search/filter (recommend page)
 */

// ────────────────────────────────────────────────────────────────────────────
// Custom Cursor Follower Logic
// ────────────────────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
    const cursor = document.getElementById('cursor-follower');
    if (!cursor) return;

    let mouseX = 0;
    let mouseY = 0;
    let cursorX = 0;
    let cursorY = 0;

    // Track mouse position
    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
        
        // Show cursor on first move
        if (cursor.style.display !== 'block') {
            cursor.style.display = 'block';
        }
    });

    // Smooth follow loop
    const tick = () => {
        // Linear interpolation for smooth movement
        cursorX += (mouseX - cursorX) * 0.15;
        cursorY += (mouseY - cursorY) * 0.15;

        cursor.style.left = `${cursorX}px`;
        cursor.style.top = `${cursorY}px`;

        requestAnimationFrame(tick);
    };
    tick();

    // Hover effects for interactive elements
    const interactiveElements = document.querySelectorAll('a, button, .movie-card, .emotion-pill, .close-btn, .clear-btn');
    
    interactiveElements.forEach(el => {
        el.addEventListener('mouseenter', () => {
            cursor.classList.add('cursor-hover');
        });
        el.addEventListener('mouseleave', () => {
            cursor.classList.remove('cursor-hover');
        });
    });
});

// ────────────────────────────────────────────────────────────────────────────
// Original App Logic
// ────────────────────────────────────────────────────────────────────────────
/* ─── Navbar ──────────────────────────────────────────────────────────── */
(function initNavbar() {
  const navbar = document.getElementById('navbar');
  const hamburger = document.getElementById('hamburger');
  const navLinks = document.querySelector('.nav-links');
  if (!navbar) return;

  // Add shadow on scroll
  window.addEventListener('scroll', () => {
    navbar.style.boxShadow = window.scrollY > 20
      ? '0 4px 24px rgba(0,0,0,0.4)'
      : 'none';
  }, { passive: true });

  // Hamburger toggle
  if (hamburger && navLinks) {
    hamburger.addEventListener('click', () => {
      navLinks.classList.toggle('open');
      hamburger.classList.toggle('open');
    });
    // Close on outside click
    document.addEventListener('click', (e) => {
      if (!navbar.contains(e.target)) {
        navLinks.classList.remove('open');
        hamburger.classList.remove('open');
      }
    });
  }
})();

/* ─── Flash messages – auto dismiss after 5 s ────────────────────────── */
(function autoFlash() {
  const container = document.getElementById('flash-container');
  if (!container) return;
  setTimeout(() => {
    container.querySelectorAll('.flash').forEach((el, i) => {
      setTimeout(() => {
        el.style.opacity = '0';
        el.style.transform = 'translateX(30px)';
        el.style.transition = 'all 0.4s ease';
        setTimeout(() => el.remove(), 400);
      }, i * 150);
    });
  }, 5000);
})();

/* ─── Toast Notification System ──────────────────────────────────────── */
(function initToast() {
  // Create toast container
  let tc = document.getElementById('toast-container');
  if (!tc) {
    tc = document.createElement('div');
    tc.id = 'toast-container';
    Object.assign(tc.style, {
      position: 'fixed', bottom: '24px', right: '24px',
      zIndex: '9999', display: 'flex', flexDirection: 'column', gap: '10px',
      maxWidth: '340px', pointerEvents: 'none',
    });
    document.body.appendChild(tc);
  }

  window.appShowToast = function(message, type = 'info', duration = 3500) {
    const COLORS = { success:'#27AE60', error:'#FF4136', warning:'#F39C12', info:'#4A9EFF' };
    const ICONS  = { success:'✅', error:'❌', warning:'⚠️', info:'ℹ️' };

    const toast = document.createElement('div');
    Object.assign(toast.style, {
      display: 'flex', alignItems: 'center', gap: '10px',
      padding: '12px 18px',
      background: 'rgba(18,18,40,0.92)',
      backdropFilter: 'blur(16px)',
      border: `1px solid ${COLORS[type]}55`,
      borderRadius: '12px',
      boxShadow: `0 6px 24px rgba(0,0,0,0.5), 0 0 0 1px ${COLORS[type]}22`,
      color: '#f0f0ff', fontSize: '0.88rem', lineHeight: '1.4',
      pointerEvents: 'auto',
      opacity: '0', transform: 'translateX(30px)',
      transition: 'all 0.35s cubic-bezier(0.4,0,0.2,1)',
    });
    toast.innerHTML = `<span style="font-size:1.1rem;flex-shrink:0">${ICONS[type]}</span><span>${message}</span>`;
    tc.appendChild(toast);

    // Animate in
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        toast.style.opacity = '1';
        toast.style.transform = 'translateX(0)';
      });
    });

    // Auto remove
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(30px)';
      setTimeout(() => toast.remove(), 350);
    }, duration);
  };
})();

/* ─── Scroll-Reveal: .fade-up elements ───────────────────────────────── */
(function initScrollReveal() {
  const items = document.querySelectorAll('.fade-up');
  if (!items.length) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (e.isIntersecting) {
        e.target.classList.add('visible');
        observer.unobserve(e.target);
      }
    });
  }, { threshold: 0.12 });

  items.forEach((el) => observer.observe(el));
})();

/* ─── Movie card search/filter (recommend page) ──────────────────────── */
(function initMovieFilter() {
  const grid = document.getElementById('movies-grid');
  if (!grid) return;

  // Inject a search box above the grid
  const searchWrap = document.createElement('div');
  searchWrap.style.cssText = `
    display:flex; justify-content:center; margin-bottom:24px;
  `;
  const input = document.createElement('input');
  input.type = 'text';
  input.placeholder = '🔍  Search movies…';
  input.id = 'movie-search';
  input.style.cssText = `
    width:100%; max-width:380px; padding:11px 18px;
    background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.12);
    border-radius:999px; color:#f0f0ff; font-size:0.94rem; font-family:inherit;
    outline:none; transition:border-color 0.3s, box-shadow 0.3s;
  `;
  input.addEventListener('focus', () => {
    input.style.borderColor = '#7c6aff';
    input.style.boxShadow   = '0 0 0 3px rgba(124,106,255,0.25)';
  });
  input.addEventListener('blur', () => {
    input.style.borderColor = 'rgba(255,255,255,0.12)';
    input.style.boxShadow   = 'none';
  });
  searchWrap.appendChild(input);
  grid.parentElement.insertBefore(searchWrap, grid);

  input.addEventListener('input', () => {
    const q = input.value.toLowerCase();
    grid.querySelectorAll('.movie-card').forEach((card) => {
      const title = (card.dataset.title || '').toLowerCase();
      const visible = !q || title.includes(q);
      card.style.display = visible ? '' : 'none';
    });
  });
})();

/* ─── Add fade-up class to key sections after load ───────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.step-card, .mood-card, .movie-card, .timeline-card, .stat-item')
    .forEach((el, i) => {
      el.classList.add('fade-up');
      el.style.transitionDelay = `${i * 50}ms`;
    });

  // Trigger IntersectionObserver refresh for newly classed elements
  const newItems = document.querySelectorAll('.fade-up');
  if (newItems.length) {
    const obs = new IntersectionObserver((entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) {
          e.target.classList.add('visible');
          obs.unobserve(e.target);
        }
      });
    }, { threshold: 0.1 });
    newItems.forEach((el) => obs.observe(el));
  }
});
