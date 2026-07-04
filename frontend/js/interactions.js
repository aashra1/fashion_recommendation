// Interaction Tracking

// Intersection Observer for view tracking
class InteractionTracker {
    constructor() {
        this.observers = new Map();
        this.viewTimers = new Map();
        this.setupIntersectionObserver();
    }

    setupIntersectionObserver() {
        this.observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                const productId = entry.target.dataset.productId;
                if (!productId) return;

                if (entry.isIntersecting) {
                    // Product came into view
                    this.viewTimers.set(productId, Date.now());
                    this.observers.set(productId, entry.target);
                } else {
                    // Product left view
                    const startTime = this.viewTimers.get(productId);
                    if (startTime) {
                        const timeSpent = Math.floor((Date.now() - startTime) / 1000);
                        if (timeSpent >= 2) {
                            // Log view if product was visible for at least 2 seconds
                            this.logView(productId, timeSpent);
                        }
                        this.viewTimers.delete(productId);
                    }
                    this.observers.delete(productId);
                }
            });
        }, {
            threshold: 0.5
        });
    }

    trackProduct(productId) {
        const elements = document.querySelectorAll(`[data-product-id="${productId}"]`);
        elements.forEach(el => {
            this.observer.observe(el);
        });
    }

    untrackProduct(productId) {
        const elements = document.querySelectorAll(`[data-product-id="${productId}"]`);
        elements.forEach(el => {
            this.observer.unobserve(el);
        });
        this.viewTimers.delete(productId);
        this.observers.delete(productId);
    }

    async logView(productId, timeSpent = 0) {
        if (!isAuthenticated()) return;

        try {
            await api.post('/interactions/log', {
                product_id: productId,
                interaction_type: 'VIEW',
                time_spent: timeSpent,
                device_type: this.getDeviceType(),
                browser: this.getBrowser(),
                os: this.getOS()
            });
        } catch (error) {
            console.error('Failed to log view:', error);
        }
    }

    async logInteraction(productId, type, ratingValue = null, showSuccessToast = true) {
        if (!isAuthenticated()) return;

        try {
            const data = {
                product_id: productId,
                interaction_type: type,
                device_type: this.getDeviceType(),
                browser: this.getBrowser(),
                os: this.getOS()
            };

            if (ratingValue !== null) {
                data.rating_value = ratingValue;
            }

            await api.post('/interactions/log', data);
            if (showSuccessToast) {
                showToast(`Added to ${type.toLowerCase().replace('_', ' ')}`, 'success');
            }
        } catch (error) {
            console.error('Failed to log interaction:', error);
            showToast('Failed to log action', 'error');
        }
    }

    getDeviceType() {
        const width = window.innerWidth;
        if (width < 768) return 'Mobile';
        if (width < 1024) return 'Tablet';
        return 'Desktop';
    }

    getBrowser() {
        const ua = navigator.userAgent;
        if (ua.includes('Chrome')) return 'Chrome';
        if (ua.includes('Firefox')) return 'Firefox';
        if (ua.includes('Safari')) return 'Safari';
        if (ua.includes('Edge')) return 'Edge';
        return 'Other';
    }

    getOS() {
        const ua = navigator.userAgent;
        if (ua.includes('Windows')) return 'Windows';
        if (ua.includes('Mac')) return 'macOS';
        if (ua.includes('Linux')) return 'Linux';
        if (ua.includes('Android')) return 'Android';
        if (ua.includes('iOS')) return 'iOS';
        return 'Other';
    }
}

// Initialize tracker
const interactionTracker = new InteractionTracker();
