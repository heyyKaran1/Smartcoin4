const API_URL = 'http://localhost:5000/api';
let wallets = [];
let refreshInterval;
let blockchainChart = null;
let miningChart = null;

function showNotification(message, type = 'info') {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.className = `notification ${type} show`;

    setTimeout(() => {
        notification.classList.remove('show');
    }, 4000);
}

async function getCsrfToken() {
    const cookie = document.cookie.split('; ').find(row => row.startsWith('csrf_token='));
    if (cookie) {
        return cookie.split('=')[1];
    }
    try {
        const response = await fetch(`${API_URL}/csrf-token`);
        const data = await response.json();
        return data.csrf_token;
    } catch (error) {
        console.error('Failed to get CSRF token:', error);
        return null;
    }
}

async function apiCall(endpoint, method = 'GET', body = null) {
    try {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include'
        };

        if (method === 'POST' || method === 'PUT' || method === 'DELETE') {
            const csrfToken = await getCsrfToken();
            if (csrfToken) {
                options.headers['X-CSRFToken'] = csrfToken;
            }
        }

        if (body) {
            options.body = JSON.stringify(body);
        }

        const response = await fetch(`${API_URL}${endpoint}`, options);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'API request failed');
        }

        return data;
    } catch (error) {
        console.error('API Error:', error);
        showNotification(error.message, 'error');
        throw error;
    }
}

async function loadBlockchainInfo() {
    try {
        const info = await apiCall('/blockchain/info');

        document.getElementById('totalSupply').textContent = `${info.total_supply || 0} coins`;
        document.getElementById('totalBlocks').textContent = info.length || 0;
        document.getElementById('difficulty').textContent = info.difficulty || 0;
        document.getElementById('chainValid').textContent = info.valid ? '✅' : '❌';

        const statsGrid = document.getElementById('blockchainStats');
        statsGrid.innerHTML = `
            <div class="stat-item">
                <strong>Total Supply</strong>
                <span>${info.total_supply || 0} coins</span>
            </div>
            <div class="stat-item">
                <strong>Block Reward</strong>
                <span>${info.block_reward || 0} coins</span>
            </div>
            <div class="stat-item">
                <strong>Mempool Size</strong>
                <span>${info.mempool_size || 0} transactions</span>
            </div>
            <div class="stat-item">
                <strong>UTXO Count</strong>
                <span>${info.utxo_count || 0}</span>
            </div>
            <div class="stat-item">
                <strong>Unique Addresses</strong>
                <span>${info.unique_addresses || 0}</span>
            </div>
            <div class="stat-item">
                <strong>Avg Block Time</strong>
                <span>${(info.average_block_time || 0).toFixed(2)}s</span>
            </div>
        `;

        createBlockchainChart(info);
        createMiningChart(info);
    } catch (error) {
        console.error('Failed to load blockchain info:', error);
    }
}

async function createBlockchainChart(info) {
    const ctx = document.getElementById('blockchainChart');
    if (!ctx) return;
    if (blockchainChart) blockchainChart.destroy();

    try {
        const response = await fetch(`${API_URL}/blockchain/history`);
        const historyData = await response.json();
        const history = historyData.history || [];

        const labels = history.map(b => `Block ${b.index}`);
        const data = history.map(b => b.transaction_count);

        if (labels.length === 0) {
            labels.push('No data');
            data.push(0);
        }

    blockchainChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Transactions',
                data: data,
                backgroundColor: 'rgba(102, 126, 234, 0.8)',
                borderColor: '#667eea',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, grid: { color: 'rgba(0,0,0,0.05)' } },
                x: { grid: { display: false } }
            }
        }
    });
    } catch (error) {
        console.error('Failed to load blockchain history:', error);
    }
}

function createMiningChart(info) {
    const ctx = document.getElementById('miningChart');
    if (!ctx) return;
    if (miningChart) miningChart.destroy();

    const difficulty = info.difficulty || 2;
    const labels = ['Block 1', 'Block 5', 'Block 10', 'Block 15', 'Current'];
    const difficulties = [2, 2, Math.max(2, difficulty - 0.5), Math.max(2, difficulty - 0.2), difficulty];

    miningChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Difficulty',
                data: difficulties,
                borderColor: '#764ba2',
                backgroundColor: 'rgba(118, 75, 162, 0.1)',
                tension: 0.4,
                fill: true,
                pointRadius: 5,
                pointBackgroundColor: '#764ba2'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, grid: { color: 'rgba(0,0,0,0.05)' } },
                x: { grid: { display: false } }
            }
        }
    });
}

async function loadBlocks() {
    try {
        const blocks = await apiCall('/blocks?limit=10');

        const blocksList = document.getElementById('blocksList');
        if (blocks.length === 0) {
            blocksList.innerHTML = '<p class="empty-state">No blocks yet</p>';
            return;
        }

        blocksList.innerHTML = blocks.reverse().map(block => `
            <div class="block-item">
                <div class="block-header">
                    <span class="block-index">Block #${block.index}</span>
                    <span>${new Date(block.timestamp * 1000).toLocaleTimeString()}</span>
                </div>
                <div class="block-hash">Hash: ${block.hash}</div>
                <div class="block-hash">Previous: ${block.previous_hash}</div>
                <div class="block-hash">Merkle Root: ${block.merkle_root}</div>
                <div class="block-info">
                    <div><strong>Nonce:</strong> ${block.nonce}</div>
                    <div><strong>Transactions:</strong> ${block.transactions.length}</div>
                    <div><strong>Size:</strong> ${JSON.stringify(block).length} bytes</div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Failed to load blocks:', error);
    }
}

async function loadMempool() {
    try {
        const data = await apiCall('/mempool');

        const mempool = document.getElementById('mempool');
        if (data.size === 0) {
            mempool.innerHTML = '<p class="empty-state">No pending transactions</p>';
            return;
        }

        mempool.innerHTML = data.transactions.map(tx => `
            <div class="tx-item">
                <div class="tx-id">TX: ${tx.tx_id}</div>
                <div style="margin-top: 5px;">
                    <strong>Inputs:</strong> ${tx.inputs.length} |
                    <strong>Outputs:</strong> ${tx.outputs.length}
                </div>
                <div style="margin-top: 5px; font-size: 0.85rem; color: #666;">
                    ${new Date(tx.timestamp * 1000).toLocaleString()}
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Failed to load mempool:', error);
    }
}

async function createWallet() {
    try {
        const wallet = await apiCall('/wallet/create', 'POST');
        wallets.push(wallet);

        updateWalletSelects();
        displayWallets();

        showNotification(`Wallet created! Address: ${wallet.address.substring(0, 20)}...`, 'success');
    } catch (error) {
        showNotification('Failed to create wallet', 'error');
    }
}

function displayWallets() {
    const walletList = document.getElementById('walletList');

    if (wallets.length === 0) {
        walletList.innerHTML = '<p class="empty-state">No wallets yet. Create one!</p>';
        return;
    }

    walletList.innerHTML = wallets.map((wallet, index) => `
        <div class="wallet-item">
            <div><strong>Wallet #${wallet.wallet_id}</strong></div>
            <div class="wallet-address">${wallet.address}</div>
            <div class="wallet-balance">${wallet.balance || 0} coins</div>
        </div>
    `).join('');
}

function updateWalletSelects() {
    const fromWallet = document.getElementById('fromWallet');
    const minerWallet = document.getElementById('minerWallet');

    const options = wallets.map(w =>
        `<option value="${w.wallet_id}">${w.address.substring(0, 30)}... (${w.balance || 0} coins)</option>`
    ).join('');

    fromWallet.innerHTML = '<option value="">Select wallet...</option>' + options;
    minerWallet.innerHTML = '<option value="">Select wallet...</option>' + options;
}

async function connectMetaMaskForBalance() {
    if (typeof Web3Manager !== 'undefined') {
        try {
            const account = await Web3Manager.connect();
            document.getElementById('addressInput').value = account;
            showNotification('MetaMask connected! Address filled automatically.', 'success');
            await checkBalance();
        } catch (error) {
            showNotification('Failed to connect MetaMask: ' + error.message, 'error');
        }
    } else {
        showNotification('MetaMask not available. Please install MetaMask extension.', 'error');
    }
}

async function checkBalance() {
    const address = document.getElementById('addressInput').value.trim();

    if (!address) {
        showNotification('Please enter an address', 'error');
        return;
    }

    try {
        let blockchainBalance = 0;
        let metamaskBalance = 0;
        let useMetaMask = false;

        if (typeof Web3Manager !== 'undefined' && Web3Manager.isConnected()) {
            const connectedAccount = Web3Manager.getAccount();
            if (connectedAccount && connectedAccount.toLowerCase() === address.toLowerCase()) {
                useMetaMask = true;
                metamaskBalance = await Web3Manager.getBalance();
            }
        }

        const data = await apiCall(`/balance/${address}`);
        blockchainBalance = data.balance;

        const result = document.getElementById('balanceResult');
        result.className = 'success-message';

        if (useMetaMask) {
            result.innerHTML = `
                <div style="font-size: 1.2rem; margin-bottom: 10px;">
                    <strong>💰 Blockchain Balance: ${blockchainBalance} coins</strong>
                </div>
                <div style="font-size: 1.2rem; margin-bottom: 10px;">
                    <strong>🦊 MetaMask Balance: ${metamaskBalance.toFixed(4)} ETH</strong>
                </div>
                <div style="font-size: 0.9rem; color: #666;">
                    <strong>Address:</strong> ${data.address}<br>
                    <strong>UTXOs:</strong> ${data.utxo_count}
                </div>
            `;
            showNotification(`Blockchain: ${blockchainBalance} coins | MetaMask: ${metamaskBalance.toFixed(4)} ETH`, 'success');
        } else {
            result.innerHTML = `
                <div style="font-size: 1.2rem; margin-bottom: 10px;">
                    <strong>💰 Balance: ${blockchainBalance} coins</strong>
                </div>
                <div style="font-size: 0.9rem; color: #666;">
                    <strong>Address:</strong> ${data.address}<br>
                    <strong>UTXOs:</strong> ${data.utxo_count}
                </div>
            `;
            showNotification(`Balance: ${blockchainBalance} coins`, 'success');
        }
    } catch (error) {
        const result = document.getElementById('balanceResult');
        result.className = 'error-message';
        result.textContent = 'Failed to check balance: ' + error.message;
    }
}

async function sendTransaction(event) {
    event.preventDefault();

    const walletId = parseInt(document.getElementById('fromWallet').value);
    const merchantName = document.getElementById('merchantName').value.trim();
    const merchantId = document.getElementById('merchantId').value.trim();
    const toAddress = document.getElementById('toAddress').value.trim();
    const amount = parseFloat(document.getElementById('amount').value);
    const purpose = document.getElementById('purpose').value.trim();
    const referenceId = document.getElementById('referenceId').value.trim();
    const fee = parseFloat(document.getElementById('fee').value);

    if (!walletId && walletId !== 0) {
        showNotification('Please select a wallet', 'error');
        return;
    }

    const resultDiv = document.getElementById('txResult');
    resultDiv.className = 'info-message';
    resultDiv.innerHTML = `
        <div class="loading"></div>
        <strong>Broadcasting transaction...</strong><br>
        Waiting for network confirmation...
    `;

    try {
        const result = await apiCall('/transaction/create', 'POST', {
            wallet_id: walletId,
            to_address: toAddress,
            amount: amount,
            fee: fee,
            merchant_name: merchantName,
            merchant_id: merchantId,
            purpose: purpose,
            reference_id: referenceId
        });

        resultDiv.className = 'success-message';
        resultDiv.innerHTML = `
            <strong>✅ Payment Confirmed!</strong><br>
            <div style="text-align: left; margin-top: 10px; font-size: 0.9rem;">
                <strong>Merchant:</strong> ${merchantName || 'N/A'}<br>
                <strong>Merchant ID:</strong> ${merchantId || 'N/A'}<br>
                <strong>Amount:</strong> ${amount} CCI<br>
                <strong>Purpose:</strong> ${purpose || 'Payment'}<br>
                <strong>Reference:</strong> ${referenceId || 'N/A'}<br>
                <strong>TX ID:</strong> ${result.tx_id.substring(0, 16)}...<br>
                <strong>Status:</strong> Confirmed in mempool
            </div>
        `;

        document.getElementById('transactionForm').reset();
        showNotification(`Payment to ${merchantName} successful!`, 'success');

        setTimeout(() => {
            loadMempool();
            refreshWallets();
        }, 1000);
    } catch (error) {
        resultDiv.className = 'error-message';
        resultDiv.innerHTML = `
            <strong>❌ Transaction Failed</strong><br>
            ${error.message || 'Failed to send transaction'}
        `;
    }
}

async function mineBlock() {
    const walletId = parseInt(document.getElementById('minerWallet').value);

    if (!walletId && walletId !== 0) {
        showNotification('Please select a miner wallet', 'error');
        return;
    }

    const wallet = wallets.find(w => w.wallet_id === walletId);
    if (!wallet) {
        showNotification('Wallet not found', 'error');
        return;
    }

    const resultDiv = document.getElementById('miningResult');
    resultDiv.className = 'info-message';
    resultDiv.textContent = '⛏️ Mining... Please wait...';

    try {
        const result = await apiCall('/mine', 'POST', {
            miner_address: wallet.address
        });

        resultDiv.className = 'success-message';
        resultDiv.innerHTML = `
            <strong>Block Mined!</strong><br>
            Block #${result.block.index}<br>
            Hash: ${result.block.hash.substring(0, 40)}...<br>
            Transactions: ${result.block.transactions.length}
        `;

        showNotification('Block mined successfully!', 'success');

        setTimeout(() => {
            loadBlockchainInfo();
            loadBlocks();
            loadMempool();
            refreshWallets();
        }, 1000);
    } catch (error) {
        resultDiv.className = 'error-message';
        resultDiv.textContent = error.message || 'Failed to mine block';
    }
}

async function refreshWallets() {
    for (let wallet of wallets) {
        try {
            const updated = await apiCall(`/wallet/${wallet.wallet_id}`);
            wallet.balance = updated.balance;
        } catch (error) {
            console.error(`Failed to update wallet ${wallet.wallet_id}:`, error);
        }
    }
    displayWallets();
    updateWalletSelects();
}

function startAutoRefresh() {
    loadBlockchainInfo();
    loadBlocks();
    loadMempool();

    refreshInterval = setInterval(() => {
        loadBlockchainInfo();
        loadBlocks();
        loadMempool();
        if (wallets.length > 0) {
            refreshWallets();
        }
    }, 2000);
}

function toggleTheme() {
    document.body.classList.toggle('dark-theme');
    const isDark = document.body.classList.contains('dark-theme');
    document.getElementById('themeToggle').checked = isDark;
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
}

window.addEventListener('load', () => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-theme');
        document.getElementById('themeToggle').checked = true;
    }
    startAutoRefresh();
    displayWallets();
    showNotification('Dashboard loaded successfully!', 'success');
});

window.addEventListener('beforeunload', () => {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
});

async function payWithMetaMask(event) {
    event.preventDefault();

    const toAddress = document.getElementById('recipientWallet').value;
    const amount = parseFloat(document.getElementById('amount').value);
    const merchantName = document.getElementById('merchantName').value;
    const merchantId = document.getElementById('merchantId').value;
    const purpose = document.getElementById('purpose').value;
    const referenceId = document.getElementById('referenceId').value;

    if (!toAddress || !amount) {
        showNotification('Please fill in recipient and amount', 'error');
        return;
    }

    if (typeof Web3Manager === 'undefined') {
        showNotification('Web3 not loaded. Please refresh the page.', 'error');
        return;
    }

    try {
        if (!Web3Manager.isConnected()) {
            showNotification('Connecting to MetaMask...', 'info');
            await Web3Manager.connect();
        }

        showNotification('Please confirm transaction in MetaMask...', 'info');

        const txHash = await Web3Manager.signTransaction({
            to: toAddress,
            amount: amount,
            data: JSON.stringify({
                merchant_name: merchantName,
                merchant_id: merchantId,
                purpose: purpose,
                reference_id: referenceId,
                payment_method: 'MetaMask',
                timestamp: Date.now()
            })
        });

        showNotification(`✅ Payment successful! TX: ${txHash.substring(0, 16)}...`, 'success');

        document.getElementById('merchantPaymentForm').reset();

        setTimeout(() => {
            loadBlockchainInfo();
            loadRecentBlocks();
        }, 2000);

    } catch (error) {
        if (error.code === 4001) {
            showNotification('Transaction rejected by user', 'error');
        } else {
            showNotification('MetaMask payment failed: ' + error.message, 'error');
        }
    }
}
