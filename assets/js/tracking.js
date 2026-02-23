/**
 * Iowa Gutter Guards - Analytics & Event Tracking
 * Version: 1.0
 * 
 * This file handles:
 * - Google Analytics 4 (GA4) tracking
 * - Form submission tracking
 * - Phone click tracking
 * - CTA button click tracking
 * - Scroll depth tracking
 */

(function() {
  'use strict';

  // ========================================
  // Configuration
  // ========================================
  const config = {
    // Replace with your actual GA4 Measurement ID
    GA4_MEASUREMENT_ID: 'G-XXXXXXXXXX',
    
    // Scroll depth thresholds to track
    scrollDepthThresholds: [25, 50, 75, 90, 100],
    
    // Debug mode (set to false in production)
    debug: false
  };

  // Track which scroll depths have been reached
  const scrollDepthReached = {};

  // ========================================
  // Utility Functions
  // ========================================
  function log(message, data) {
    if (config.debug) {
      console.log('[IGG Tracking]', message, data || '');
    }
  }

  function trackEvent(eventName, eventParams = {}) {
    log('Event:', { eventName, eventParams });
    
    // Send to GA4
    if (typeof gtag === 'function') {
      gtag('event', eventName, eventParams);
    }
  }

  // ========================================
  // Phone Click Tracking
  // ========================================
  function initPhoneTracking() {
    document.querySelectorAll('a[href^="tel:"]').forEach(function(link) {
      link.addEventListener('click', function(e) {
        const phoneNumber = this.href.replace('tel:', '');
        trackEvent('phone_click', {
          event_category: 'contact',
          event_label: phoneNumber,
          phone_number: phoneNumber,
          page_location: window.location.pathname
        });
      });
    });
    log('Phone tracking initialized');
  }

  // ========================================
  // CTA Button Tracking
  // ========================================
  function initCTATracking() {
    // Track primary CTA buttons
    document.querySelectorAll('.btn-primary').forEach(function(button, index) {
      button.addEventListener('click', function(e) {
        const buttonText = this.textContent.trim();
        const buttonId = this.id || 'cta_' + index;
        
        trackEvent('cta_click', {
          event_category: 'engagement',
          event_label: buttonText,
          button_text: buttonText,
          button_id: buttonId,
          page_location: window.location.pathname
        });
      });
    });

    // Track quote form CTA specifically
    document.querySelectorAll('a[href="#quote-form"], a[href*="quote"]').forEach(function(link) {
      link.addEventListener('click', function(e) {
        trackEvent('quote_cta_click', {
          event_category: 'conversion',
          event_label: this.textContent.trim(),
          page_location: window.location.pathname
        });
      });
    });

    log('CTA tracking initialized');
  }

  // ========================================
  // Form Submission Tracking
  // ========================================
  function initFormTracking() {
    document.querySelectorAll('form').forEach(function(form, index) {
      form.addEventListener('submit', function(e) {
        const formId = this.id || 'form_' + index;
        const formAction = this.action || '';
        
        // Get form data for tracking (excluding sensitive info)
        const formData = new FormData(this);
        const hasEmail = formData.get('email') || formData.get('Email');
        const hasPhone = formData.get('phone') || formData.get('Phone');
        const city = formData.get('city') || formData.get('City') || '';
        
        trackEvent('form_submit', {
          event_category: 'conversion',
          event_label: formId,
          form_id: formId,
          form_destination: formAction,
          has_email: !!hasEmail,
          has_phone: !!hasPhone,
          city: city,
          page_location: window.location.pathname
        });

        // Track as conversion
        trackEvent('generate_lead', {
          event_category: 'conversion',
          currency: 'USD',
          value: 50 // Estimated lead value
        });
      });
    });

    // Track form field interactions
    document.querySelectorAll('form input, form select, form textarea').forEach(function(field) {
      field.addEventListener('focus', function(e) {
        if (!this.dataset.tracked) {
          this.dataset.tracked = 'true';
          trackEvent('form_start', {
            event_category: 'engagement',
            field_name: this.name || this.id,
            page_location: window.location.pathname
          });
        }
      });
    });

    log('Form tracking initialized');
  }

  // ========================================
  // Scroll Depth Tracking
  // ========================================
  function initScrollTracking() {
    let ticking = false;
    
    function calculateScrollDepth() {
      const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
      const documentHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
      
      if (documentHeight <= 0) return 0;
      
      return Math.round((scrollTop / documentHeight) * 100);
    }

    function checkScrollDepth() {
      const currentDepth = calculateScrollDepth();
      
      config.scrollDepthThresholds.forEach(function(threshold) {
        if (currentDepth >= threshold && !scrollDepthReached[threshold]) {
          scrollDepthReached[threshold] = true;
          
          trackEvent('scroll_depth', {
            event_category: 'engagement',
            event_label: threshold + '%',
            percent_scrolled: threshold,
            page_location: window.location.pathname
          });
        }
      });
    }

    window.addEventListener('scroll', function() {
      if (!ticking) {
        window.requestAnimationFrame(function() {
          checkScrollDepth();
          ticking = false;
        });
        ticking = true;
      }
    }, { passive: true });

    log('Scroll tracking initialized');
  }

  // ========================================
  // Page View Tracking Enhancement
  // ========================================
  function trackEnhancedPageView() {
    // Get page metadata
    const pageTitle = document.title;
    const pagePath = window.location.pathname;
    const referrer = document.referrer;
    
    // Determine page type
    let pageType = 'other';
    if (pagePath === '/' || pagePath === '/index.html') {
      pageType = 'homepage';
    } else if (pagePath.includes('/service-areas/')) {
      pageType = 'city_landing';
    } else if (pagePath.includes('/thank-you')) {
      pageType = 'conversion';
    } else if (pagePath.includes('/warranty') || pagePath.includes('/faq') || pagePath.includes('/reviews')) {
      pageType = 'info';
    }

    // Extract city from path if it's a city page
    let cityName = '';
    const cityMatch = pagePath.match(/\/service-areas\/([^/]+)/);
    if (cityMatch) {
      cityName = cityMatch[1].replace(/-ia$/, '').replace(/-/g, ' ');
    }

    trackEvent('page_view_enhanced', {
      page_title: pageTitle,
      page_path: pagePath,
      page_type: pageType,
      city_name: cityName,
      referrer: referrer
    });

    // Track thank you page as conversion
    if (pageType === 'conversion') {
      trackEvent('conversion', {
        event_category: 'conversion',
        conversion_type: 'form_submission',
        page_location: pagePath
      });
    }
  }

  // ========================================
  // External Link Tracking
  // ========================================
  function initExternalLinkTracking() {
    document.querySelectorAll('a[href^="http"]').forEach(function(link) {
      if (!link.href.includes(window.location.hostname)) {
        link.addEventListener('click', function(e) {
          trackEvent('outbound_link', {
            event_category: 'engagement',
            event_label: this.href,
            link_url: this.href,
            link_text: this.textContent.trim()
          });
        });
      }
    });
    log('External link tracking initialized');
  }

  // ========================================
  // Time on Page Tracking
  // ========================================
  function initTimeOnPageTracking() {
    const startTime = Date.now();
    const timeThresholds = [30, 60, 120, 300]; // seconds
    const timeTracked = {};

    setInterval(function() {
      const elapsedSeconds = Math.floor((Date.now() - startTime) / 1000);
      
      timeThresholds.forEach(function(threshold) {
        if (elapsedSeconds >= threshold && !timeTracked[threshold]) {
          timeTracked[threshold] = true;
          trackEvent('time_on_page', {
            event_category: 'engagement',
            event_label: threshold + 's',
            time_seconds: threshold,
            page_location: window.location.pathname
          });
        }
      });
    }, 5000); // Check every 5 seconds

    log('Time on page tracking initialized');
  }

  // ========================================
  // Initialize All Tracking
  // ========================================
  function init() {
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', initTracking);
    } else {
      initTracking();
    }
  }

  function initTracking() {
    log('Initializing tracking...');
    
    trackEnhancedPageView();
    initPhoneTracking();
    initCTATracking();
    initFormTracking();
    initScrollTracking();
    initExternalLinkTracking();
    initTimeOnPageTracking();
    
    log('All tracking initialized');
  }

  // Start initialization
  init();

})();
