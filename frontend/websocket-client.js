class WebSocketClient {
    constructor(url) {
        this.url = url || `ws://${window.location.hostname}:5000/ws`;
        this.ws = null;
        this.reconnectInterval = 5000;
        this.listeners = {};
        this.connect();
    }

    connect() {
        try {
            this.ws = new WebSocket(this.url);

            this.ws.onopen = () => {
                console.log('WebSocket connected');
                this.emit('connected');
            };

            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleMessage(data);
                } catch (error) {
                    console.error('Failed to parse WebSocket message:', error);
                }
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.emit('error', error);
            };

            this.ws.onclose = () => {
                console.log('WebSocket disconnected. Reconnecting...');
                this.emit('disconnected');
                setTimeout(() => this.connect(), this.reconnectInterval);
            };
        } catch (error) {
            console.error('WebSocket connection failed:', error);
            setTimeout(() => this.connect(), this.reconnectInterval);
        }
    }

    handleMessage(data) {
        const { type, payload } = data;

        if (type === 'payment_received') {
            this.emit('payment', payload);
        } else if (type === 'block_mined') {
            this.emit('block', payload);
        } else if (type === 'transaction_confirmed') {
            this.emit('transaction', payload);
        } else if (type === 'balance_updated') {
            this.emit('balance', payload);
        }

        this.emit(type, payload);
    }

    on(event, callback) {
        if (!this.listeners[event]) {
            this.listeners[event] = [];
        }
        this.listeners[event].push(callback);
    }

    emit(event, data) {
        if (this.listeners[event]) {
            this.listeners[event].forEach(callback => callback(data));
        }
    }

    send(type, payload) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({ type, payload }));
        } else {
            console.warn('WebSocket is not connected');
        }
    }

    subscribe(channel, address) {
        this.send('subscribe', { channel, address });
    }

    unsubscribe(channel, address) {
        this.send('unsubscribe', { channel, address });
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
        }
    }
}

window.WebSocketClient = WebSocketClient;
