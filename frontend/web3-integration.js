const Web3Manager = {
    web3: null,
    account: null,

    async init() {
        if (typeof window.ethereum !== 'undefined') {
            this.web3 = window.ethereum;

            window.ethereum.on('accountsChanged', (accounts) => {
                if (accounts.length > 0) {
                    this.account = accounts[0];
                    localStorage.setItem('metamask_connected_account', this.account);
                    this.onAccountChanged(this.account);
                } else {
                    localStorage.removeItem('metamask_connected_account');
                    this.account = null;
                    this.onDisconnect();
                }
            });

            window.ethereum.on('chainChanged', () => {
                window.location.reload();
            });

            const savedAccount = localStorage.getItem('metamask_connected_account');
            if (savedAccount) {
                await this.connect();
            }
        }
    },

    async connect() {
        try {
            const accounts = await window.ethereum.request({
                method: 'eth_requestAccounts'
            });
            this.account = accounts[0];
            localStorage.setItem('metamask_connected_account', this.account);
            return this.account;
        } catch (error) {
            console.error('MetaMask connection failed:', error);
            throw error;
        }
    },

    async signTransaction(tx) {
        if (!this.account) {
            throw new Error('Please connect MetaMask first');
        }

        try {
            const transactionParameters = {
                to: tx.to,
                from: this.account,
                value: this.toWei(tx.amount),
                data: tx.data || '0x',
                gas: '0x5208',
            };

            const txHash = await window.ethereum.request({
                method: 'eth_sendTransaction',
                params: [transactionParameters],
            });

            return txHash;
        } catch (error) {
            console.error('Transaction signing failed:', error);
            throw error;
        }
    },

    async signMessage(message) {
        if (!this.account) {
            throw new Error('Please connect MetaMask first');
        }

        try {
            const signature = await window.ethereum.request({
                method: 'personal_sign',
                params: [message, this.account],
            });
            return signature;
        } catch (error) {
            console.error('Message signing failed:', error);
            throw error;
        }
    },

    toWei(amount) {
        const wei = Math.floor(amount * 1e18);
        return '0x' + wei.toString(16);
    },

    fromWei(wei) {
        return parseInt(wei, 16) / 1e18;
    },

    isConnected() {
        return this.account !== null;
    },

    getAccount() {
        return this.account;
    },

    async getBalance() {
        if (!this.account) return 0;

        try {
            const balance = await window.ethereum.request({
                method: 'eth_getBalance',
                params: [this.account, 'latest']
            });
            return this.fromWei(balance);
        } catch (error) {
            console.error('Failed to get balance:', error);
            return 0;
        }
    },

    async getNetwork() {
        try {
            const chainId = await window.ethereum.request({
                method: 'eth_chainId'
            });
            return parseInt(chainId, 16);
        } catch (error) {
            console.error('Failed to get network:', error);
            return null;
        }
    },

    async switchNetwork(chainId) {
        try {
            await window.ethereum.request({
                method: 'wallet_switchEthereumChain',
                params: [{ chainId: '0x' + chainId.toString(16) }],
            });
        } catch (error) {
            console.error('Failed to switch network:', error);
            throw error;
        }
    },

    onAccountChanged(account) {
        if (typeof window.onMetaMaskAccountChanged === 'function') {
            window.onMetaMaskAccountChanged(account);
        }
    },

    onDisconnect() {
        if (typeof window.onMetaMaskDisconnect === 'function') {
            window.onMetaMaskDisconnect();
        }
    }
};

window.Web3Manager = Web3Manager;
Web3Manager.init();
