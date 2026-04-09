/* ============================================================
   DevCore — Main JavaScript
   Premium Animations, Navigation, Interactions
   ============================================================ */

(function() {
    'use strict';

    /* ── Preloader ─────────────────────────────────────────── */
    window.addEventListener('load', () => {
        const preloader = document.getElementById('preloader');
        if (preloader) {
            setTimeout(() => preloader.classList.add('loaded'), 600);
            setTimeout(() => preloader.remove(), 1200);
        }
        initHeroReveal();
        initScrollAnimations();
        initTextReveal();
        initCounters();
        initMagneticCards();
        initParallaxGlows();
        initCursorGlow();
        initHorizontalScroll();
    });

    /* ── Header Scroll ─────────────────────────────────────── */
    const header = document.getElementById('header');

    function handleScroll() {
        const scrollY = window.scrollY;
        if (header) {
            header.classList.toggle('scrolled', scrollY > 50);
        }
        updateActiveNav(scrollY);
        updateTextReveal();
        updateParallax(scrollY);
        updateHorizontalScroll(scrollY);
    }

    window.addEventListener('scroll', handleScroll, { passive: true });

    /* ── Active Nav Link ───────────────────────────────────── */
    function updateActiveNav(scrollY) {
        const sections = document.querySelectorAll('section[id]');
        const navLinks = document.querySelectorAll('.nav__link');
        const offset = 200;

        sections.forEach(section => {
            const top = section.offsetTop - offset;
            const bottom = top + section.offsetHeight;
            const id = section.getAttribute('id');

            if (scrollY >= top && scrollY < bottom) {
                navLinks.forEach(link => {
                    link.classList.toggle('active', link.getAttribute('href') === '#' + id);
                });
            }
        });
    }

    /* ── Mobile Menu ───────────────────────────────────────── */
    const burger = document.getElementById('navBurger');
    const navMenu = document.getElementById('navMenu');

    if (burger && navMenu) {
        burger.addEventListener('click', () => {
            burger.classList.toggle('active');
            navMenu.classList.toggle('open');
            burger.setAttribute('aria-expanded', navMenu.classList.contains('open'));
            document.body.style.overflow = navMenu.classList.contains('open') ? 'hidden' : '';
        });

        navMenu.querySelectorAll('.nav__link').forEach(link => {
            link.addEventListener('click', () => {
                burger.classList.remove('active');
                navMenu.classList.remove('open');
                burger.setAttribute('aria-expanded', 'false');
                document.body.style.overflow = '';
            });
        });
    }

    /* ── Smooth Scroll ─────────────────────────────────────── */
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            const target = document.querySelector(targetId);
            if (!target) return;
            e.preventDefault();
            const headerHeight = header ? header.offsetHeight : 0;
            const top = target.offsetTop - headerHeight;
            window.scrollTo({ top, behavior: 'smooth' });
        });
    });

    /* ── Hero Word-by-Word Reveal ──────────────────────────── */
    function initHeroReveal() {
        const words = document.querySelectorAll('.hero__title-word');
        const subtitle = document.querySelector('.hero__subtitle');
        const actions = document.querySelector('.hero__actions');
        const stats = document.querySelector('.hero__stats');
        const badge = document.querySelector('.hero__badge');

        // Badge appears first
        if (badge) {
            setTimeout(() => badge.classList.add('visible'), 300);
        }

        words.forEach((word, i) => {
            setTimeout(() => {
                word.classList.add('revealed');
            }, 500 + i * 200);
        });

        // Reveal slash
        const slash = document.querySelector('.hero__slash');
        if (slash) {
            setTimeout(() => slash.classList.add('revealed'), 500 + words.length * 200);
        }

        // Fade in subtitle, actions, stats
        if (subtitle) {
            setTimeout(() => subtitle.classList.add('revealed'), 900 + words.length * 200);
        }
        if (actions) {
            setTimeout(() => actions.classList.add('revealed'), 1100 + words.length * 200);
        }
        if (stats) {
            setTimeout(() => stats.classList.add('revealed'), 1300 + words.length * 200);
        }
    }

    /* ── Scroll Animations (Intersection Observer) ─────────── */
    function initScrollAnimations() {
        const revealEls = document.querySelectorAll('.reveal, .reveal-scale, .reveal-up, .stagger-children');

        if (!('IntersectionObserver' in window)) {
            revealEls.forEach(el => el.classList.add('visible'));
            return;
        }

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.05,
            rootMargin: '50px 0px -20px 0px'
        });

        revealEls.forEach(el => observer.observe(el));

        // Force-check elements already in viewport
        setTimeout(() => {
            revealEls.forEach(el => {
                const rect = el.getBoundingClientRect();
                if (rect.top < window.innerHeight + 100 && rect.bottom > -100) {
                    el.classList.add('visible');
                }
            });
        }, 100);
    }

    /* ── Text Reveal on Scroll (About section) ─────────────── */
    let textRevealWords = [];

    function initTextReveal() {
        const container = document.getElementById('textReveal');
        if (!container) return;
        splitTextReveal(container);
    }

    function splitTextReveal(container) {
        const text = container.textContent.trim();
        if (!text) return;

        container.innerHTML = '';
        const words = text.split(/\s+/);

        words.forEach((word, i) => {
            const span = document.createElement('span');
            span.className = 'text-reveal__word';
            span.textContent = word;
            span.style.transitionDelay = (i * 0.02) + 's';
            container.appendChild(span);

            if (i < words.length - 1) {
                container.appendChild(document.createTextNode(' '));
            }
        });

        textRevealWords = container.querySelectorAll('.text-reveal__word');
        updateTextReveal();
    }

    function updateTextReveal() {
        if (!textRevealWords.length) return;

        const container = document.getElementById('textReveal');
        if (!container) return;

        const rect = container.getBoundingClientRect();
        const windowH = window.innerHeight;
        const progress = Math.min(Math.max((windowH - rect.top) / (windowH * 0.7), 0), 1);

        textRevealWords.forEach((word, i) => {
            const wordProgress = i / textRevealWords.length;
            if (progress > wordProgress) {
                word.classList.add('revealed');
            }
        });
    }

    /* ── Counter Animation ─────────────────────────────────── */
    function initCounters() {
        const counters = document.querySelectorAll('[data-count]');

        if ('IntersectionObserver' in window) {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        animateCounter(entry.target);
                        observer.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.3 });

            counters.forEach(counter => observer.observe(counter));
        } else {
            counters.forEach(counter => {
                const target = parseInt(counter.getAttribute('data-count'));
                const suffix = counter.getAttribute('data-suffix') || '';
                counter.textContent = target + suffix;
            });
        }
    }

    function animateCounter(el) {
        const target = parseInt(el.getAttribute('data-count'));
        const suffix = el.getAttribute('data-suffix') || '';
        const duration = 2000;
        const start = performance.now();

        function step(now) {
            const elapsed = now - start;
            const progress = Math.min(elapsed / duration, 1);
            // Smooth ease-out cubic
            const eased = 1 - Math.pow(1 - progress, 3);
            const current = Math.round(eased * target);
            el.textContent = current + suffix;

            if (progress < 1) {
                requestAnimationFrame(step);
            }
        }

        requestAnimationFrame(step);
    }

    /* ── Magnetic Card Hover Effect ────────────────────────── */
    function initMagneticCards() {
        const cards = document.querySelectorAll('.service-card, .eco-card, .bento__card');

        cards.forEach(card => {
            card.addEventListener('mousemove', (e) => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                const centerX = rect.width / 2;
                const centerY = rect.height / 2;

                const rotateX = (y - centerY) / centerY * -4;
                const rotateY = (x - centerX) / centerX * 4;

                card.style.transform = `perspective(800px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-4px)`;
            });

            card.addEventListener('mouseleave', () => {
                card.style.transform = '';
            });
        });
    }

    /* ── Parallax Glows on Scroll ──────────────────────────── */
    function initParallaxGlows() {
        // Set initial state
        updateParallax(window.scrollY);
    }

    function updateParallax(scrollY) {
        const glows = document.querySelectorAll('.hero__glow');
        glows.forEach((glow, i) => {
            const speed = 0.15 + i * 0.05;
            glow.style.transform = `translateY(${scrollY * speed}px)`;
        });

        // Parallax for CTA bg
        const ctaBg = document.querySelector('.cta__bg');
        if (ctaBg) {
            const rect = ctaBg.getBoundingClientRect();
            if (rect.top < window.innerHeight && rect.bottom > 0) {
                const offset = (window.innerHeight - rect.top) * 0.08;
                ctaBg.style.transform = `translate(-50%, calc(-50% + ${offset}px))`;
            }
        }
    }

    /* ── Cursor Glow Spotlight ──────────────────────────────── */
    function initCursorGlow() {
        const glow = document.getElementById('cursorGlow');
        if (!glow || window.matchMedia('(pointer: coarse)').matches) return;

        let mouseX = 0, mouseY = 0;
        let glowX = 0, glowY = 0;
        let active = false;

        document.addEventListener('mousemove', (e) => {
            mouseX = e.clientX;
            mouseY = e.clientY;
            if (!active) {
                active = true;
                glow.classList.add('active');
                requestAnimationFrame(animateGlow);
            }
        });

        document.addEventListener('mouseleave', () => {
            active = false;
            glow.classList.remove('active');
        });

        function animateGlow() {
            glowX += (mouseX - glowX) * 0.12;
            glowY += (mouseY - glowY) * 0.12;
            glow.style.left = glowX + 'px';
            glow.style.top = glowY + 'px';
            if (active) requestAnimationFrame(animateGlow);
        }
    }

    /* ── Horizontal Scroll (Advantages) ───────────────────── */
    let advSection = null;
    let advTrack = null;

    function initHorizontalScroll() {
        advSection = document.querySelector('.advantages');
        advTrack = document.getElementById('advTrack');
        if (!advSection || !advTrack) return;

        // On mobile, disable scroll-driven and use native horizontal scroll
        if (window.innerWidth <= 768) return;

        updateHorizontalScroll(window.scrollY);
    }

    function updateHorizontalScroll(scrollY) {
        if (!advSection || !advTrack || window.innerWidth <= 768) return;

        const rect = advSection.getBoundingClientRect();
        const sectionTop = advSection.offsetTop;
        const sectionHeight = advSection.offsetHeight;
        const viewportH = window.innerHeight;

        // How far we've scrolled into the section
        const scrollInSection = scrollY - sectionTop;
        const scrollRange = sectionHeight - viewportH;

        if (scrollInSection < 0 || scrollInSection > scrollRange) return;

        const progress = scrollInSection / scrollRange;
        const trackWidth = advTrack.scrollWidth - advTrack.parentElement.offsetWidth + 100;
        const translateX = -progress * trackWidth;

        advTrack.style.transform = `translateX(${translateX}px)`;
    }

    /* ── Contact Form ──────────────────────────────────────── */
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const btn = this.querySelector('button[type="submit"]');
            const originalHTML = btn.innerHTML;

            btn.innerHTML = '<span style="display:inline-flex;align-items:center;gap:8px"><svg width="20" height="20" viewBox="0 0 20 20" fill="none"><path d="M16.7 5L7.5 14.2L3.3 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></span>';
            btn.style.background = '#2ECC71';

            setTimeout(() => {
                btn.innerHTML = originalHTML;
                btn.style.background = '';
                contactForm.reset();
            }, 2500);
        });
    }

    /* ── Glass Modal (Bento Card Details) ────────────────────── */
    function initGlassModal() {
        const modal = document.getElementById('glassModal');
        if (!modal) return;

        const backdrop = modal.querySelector('.glass-modal__backdrop');
        const closeBtn = modal.querySelector('.glass-modal__close');
        const iconEl = document.getElementById('modalIcon');
        const titleEl = document.getElementById('modalTitle');
        const descEl = document.getElementById('modalDesc');
        const detailsEl = document.getElementById('modalDetails');
        const ctaBtn = document.getElementById('modalCta');

        // Card icon color map
        const cardMeta = {
            s1: { iconClass: '', color: 'primary' },
            s2: { iconClass: '', color: 'primary' },
            s3: { iconClass: 'glass-modal__icon--green', color: 'green' },
            s4: { iconClass: 'glass-modal__icon--orange', color: 'orange' },
            s5: { iconClass: 'glass-modal__icon--green', color: 'green' }
        };

        function getLang() {
            return window.devCoreI18n?.currentLang || 'kk';
        }

        function t(key) {
            const lang = getLang();
            return translations?.[lang]?.[key] || key;
        }

        function openModal(cardId) {
            const card = document.querySelector(`[data-bento="${cardId}"]`);
            if (!card) return;

            const meta = cardMeta[cardId] || {};
            const iconSvg = card.querySelector('.bento__icon')?.innerHTML || '';

            // Set icon
            iconEl.className = 'glass-modal__icon';
            if (meta.iconClass) iconEl.classList.add(meta.iconClass);
            iconEl.innerHTML = iconSvg;
            // Make icon SVGs bigger
            const svg = iconEl.querySelector('svg');
            if (svg) { svg.setAttribute('width', '28'); svg.setAttribute('height', '28'); }

            // Set title & description
            titleEl.textContent = t(`solutions.${cardId}_title`);
            descEl.textContent = t(`solutions.${cardId}_full`);

            // Set detail items
            detailsEl.innerHTML = '';
            for (let i = 1; i <= 4; i++) {
                const detailText = t(`solutions.${cardId}_d${i}`);
                if (detailText && !detailText.startsWith('solutions.')) {
                    const item = document.createElement('div');
                    item.className = 'glass-modal__detail-item';
                    if (meta.color === 'green') item.classList.add('glass-modal__detail-item--green');
                    if (meta.color === 'orange') item.classList.add('glass-modal__detail-item--orange');
                    item.innerHTML = `<span class="glass-modal__detail-dot"></span><span>${detailText}</span>`;
                    detailsEl.appendChild(item);
                }
            }

            // Update CTA text
            ctaBtn.textContent = t('nav.cta');

            // Open
            modal.classList.add('open');
            modal.setAttribute('aria-hidden', 'false');
            document.body.style.overflow = 'hidden';
        }

        function closeModal() {
            modal.classList.remove('open');
            modal.setAttribute('aria-hidden', 'true');
            document.body.style.overflow = '';
        }

        // Bind card clicks
        document.querySelectorAll('[data-bento]').forEach(card => {
            card.addEventListener('click', (e) => {
                e.preventDefault();
                openModal(card.getAttribute('data-bento'));
            });
        });

        // Close handlers
        closeBtn.addEventListener('click', closeModal);
        backdrop.addEventListener('click', closeModal);
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && modal.classList.contains('open')) closeModal();
        });

        // Close modal when CTA is clicked (navigates to contact)
        ctaBtn.addEventListener('click', closeModal);
    }

    // Init after DOM ready
    initGlassModal();

    /* ── Copyright Year ────────────────────────────────────── */
    const yearEl = document.getElementById('currentYear');
    if (yearEl) yearEl.textContent = new Date().getFullYear();

    /* ── i18n style transitions ────────────────────────────── */
    const style = document.createElement('style');
    style.textContent = '[data-i18n] { transition: opacity 0.15s ease, transform 0.15s ease; }';
    document.head.appendChild(style);

    /* ── Re-split text reveal on language change ───────────── */
    const originalSetLang = window.devCoreI18n?.setLang?.bind(window.devCoreI18n);
    if (window.devCoreI18n && originalSetLang) {
        window.devCoreI18n.setLang = function(lang, animate) {
            originalSetLang(lang, animate);
            setTimeout(() => {
                const container = document.getElementById('textReveal');
                if (container) {
                    splitTextReveal(container);
                }
            }, 200);
        };
    }

})();
