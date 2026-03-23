(function() {
    'use strict';

    /* ── Intersection Observer for fade-in ── */
    var observerOptions = {
        threshold: 0.15,
        rootMargin: '0px 0px -50px 0px'
    };

    var observer = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                if (entry.target.classList.contains('viz-container')) {
                    animateBarCharts(entry.target);
                }
            }
        });
    }, observerOptions);

    document.querySelectorAll('.fade-in').forEach(function(el) {
        observer.observe(el);
    });

    /* ── Bar chart animation ── */
    function animateBarCharts(container) {
        var barFills = container.querySelectorAll('.bar-fill');
        barFills.forEach(function(bar) {
            var target = parseFloat(bar.getAttribute('data-target'));
            animateValue(bar, 0, target, 1200);
        });
    }

    function animateValue(element, start, end, duration) {
        var startTimestamp = null;
        function step(timestamp) {
            if (!startTimestamp) startTimestamp = timestamp;
            var progress = Math.min((timestamp - startTimestamp) / duration, 1);
            var value = Math.floor(progress * (end - start) + start);
            element.style.width = value + '%';
            if (progress < 1) {
                requestAnimationFrame(step);
            }
        }
        requestAnimationFrame(step);
    }

    /* ── Subscribe form handler ── */
    document.querySelectorAll('.subscribe-form').forEach(function(form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            var btn = this.querySelector('button');
            var msgEl = this.parentElement.querySelector('.form-message');
            var emailInput = this.querySelector('input[name="email"]');
            var email = emailInput.value;
            if (!email) return;

            btn.disabled = true;
            var originalText = btn.textContent;
            btn.textContent = 'Subscribing...';
            if (msgEl) { msgEl.textContent = ''; }

            // Hidden iframe POST to sibforms.com
            var iframeName = 'brevo_iframe_' + Date.now();
            var iframe = document.createElement('iframe');
            iframe.name = iframeName;
            iframe.style.display = 'none';
            document.body.appendChild(iframe);

            var hiddenForm = document.createElement('form');
            hiddenForm.method = 'POST';
            hiddenForm.action = 'https://134fd1fd.sibforms.com/serve/MUIFAN5qAJLG0g2AEBbIvYpGBB_HzgQ0cQGX_S1gbTFopqWWH25xu27PtcyJDv025hP1RpQsU9PnUqAz9-iXgxUgC5vl4lxcSdoqYYwl2W5JxZ1xIMZIwPv4-hiIWYUWPTgigG1b89O0-a1SZomRSRN1uBPS9MFW14JkSu6omaNbCbSaPVKmWV01qolKwvYDtZc-6JZIdUkWfHVfMQ==';
            hiddenForm.target = iframeName;
            hiddenForm.style.display = 'none';

            var emailField = document.createElement('input');
            emailField.type = 'hidden';
            emailField.name = 'EMAIL';
            emailField.value = email;
            hiddenForm.appendChild(emailField);

            document.body.appendChild(hiddenForm);
            hiddenForm.submit();

            var done = false;
            function showSuccess() {
                if (done) return;
                done = true;
                if (msgEl) {
                    msgEl.textContent = "You're in! We'll be in touch.";
                    msgEl.className = 'form-message success';
                }
                emailInput.value = '';
                btn.disabled = false;
                btn.textContent = originalText;
                if (window.fathom) fathom.trackEvent('email_signup');
                setTimeout(function() {
                    if (iframe.parentNode) iframe.parentNode.removeChild(iframe);
                    if (hiddenForm.parentNode) hiddenForm.parentNode.removeChild(hiddenForm);
                }, 2000);
            }
            iframe.addEventListener('load', showSuccess);
            setTimeout(showSuccess, 3000);
        });
    });

    /* ── Sticky CTA ── */
    var stickyCta = document.querySelector('.sticky-cta');
    if (stickyCta) {
        var showThreshold = 600;

        window.addEventListener('scroll', function() {
            var currentScroll = window.scrollY;
            if (currentScroll > showThreshold) {
                stickyCta.classList.add('visible');
            } else {
                stickyCta.classList.remove('visible');
            }
        }, { passive: true });
    }

    /* ── Mobile nav toggle ── */
    var navToggle = document.querySelector('.nav-toggle');
    var navLinks = document.querySelector('.nav-links');
    if (navToggle && navLinks) {
        navToggle.addEventListener('click', function() {
            navLinks.classList.toggle('active');
        });
    }

    /* ── Scroll hint ── */
    var scrollHint = document.querySelector('.scroll-hint');
    if (scrollHint) {
        scrollHint.addEventListener('click', function() {
            var sections = document.querySelectorAll('section');
            if (sections.length > 0) {
                sections[0].scrollIntoView({ behavior: 'smooth' });
            }
        });
    }

})();
