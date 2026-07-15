// CSRF Token Helper
const CSRFHelper = {
    token: null,

    async getToken() {
        if (this.token) return this.token;

        try {
            const response = await fetch('/api/csrf-token', {
                credentials: 'include'
            });
            const data = await response.json();
            this.token = data.csrf_token;
            return this.token;
        } catch (error) {
            console.error('Failed to get CSRF token:', error);
            return null;
        }
    },

    getFromCookie() {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; csrf_token=`);
        if (parts.length === 2) {
            return parts.pop().split(';').shift();
        }
        return null;
    },

    async ensureToken() {
        let token = this.getFromCookie();
        if (!token) {
            token = await this.getToken();
        }
        return token;
    },

    async addToRequest(options = {}) {
        const token = await this.ensureToken();
        if (token) {
            options.headers = options.headers || {};
            options.headers['X-CSRFToken'] = token;
            options.credentials = 'include';
        }
        return options;
    }
};

window.CSRFHelper = CSRFHelper;

async function fetchWithCSRF(url, options = {}) {
    options = await CSRFHelper.addToRequest(options);
    return fetch(url, options);
}

window.fetchWithCSRF = fetchWithCSRF;
