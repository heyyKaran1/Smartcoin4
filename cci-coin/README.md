# CCI Coin - ERC-20 Smart Contract

Professional-grade ERC-20 token smart contract for CCI Coin Enterprise Platform.

## 🎯 Token Specifications

- **Name:** CCI Coin
- **Symbol:** CCI
- **Decimals:** 18 (standard ERC-20)
- **Total Supply:** 1,000,000,000 (1 billion) CCI
- **Standard:** ERC-20 (OpenZeppelin audited implementation)
- **Network:** Ethereum/Polygon/BNB Smart Chain

## 📋 Features

- ✅ Fixed supply (no additional minting)
- ✅ Standard ERC-20 functions (transfer, approve, transferFrom)
- ✅ Ownable (contract owner management)
- ✅ Fully tested with Hardhat
- ✅ Audited OpenZeppelin base contracts
- ✅ Gas-optimized with Solidity 0.8.20

## 🛠️ Tech Stack

- **Solidity:** ^0.8.20
- **Hardhat:** Development framework
- **OpenZeppelin Contracts:** Audited ERC-20 implementation
- **Ethers.js:** Blockchain interaction
- **Mocha/Chai:** Testing framework

## 📦 Installation

```bash
npm install
```

## ⚙️ Configuration

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Configure your `.env` file:
```env
PRIVATE_KEY=your_private_key_without_0x_prefix
SEPOLIA_RPC_URL=https://eth-sepolia.g.alchemy.com/v2/YOUR_KEY
BSC_RPC_URL=https://bsc-dataseed1.binance.org
POLYGON_RPC_URL=https://polygon-rpc.com
ETHERSCAN_API_KEY=your_etherscan_api_key
BSCSCAN_API_KEY=your_bscscan_api_key
POLYGONSCAN_API_KEY=your_polygonscan_api_key
```

⚠️ **Security:** Never commit your `.env` file! It contains private keys.

## 🔨 Compilation

Compile the smart contracts:
```bash
npx hardhat compile
```

## 🧪 Testing

Run the comprehensive test suite:
```bash
npx hardhat test
```

All 15 tests must pass before deployment.

## 🚀 Deployment

### 1. Local Hardhat Network (Development)
```bash
npx hardhat run scripts/deploy.js
```

### 2. Sepolia Testnet (Testing)
```bash
npx hardhat run scripts/deploy.js --network sepolia
```

### 3. Production Networks

**BNB Smart Chain:**
```bash
npx hardhat run scripts/deploy.js --network bsc
```

**Polygon Mainnet:**
```bash
npx hardhat run scripts/deploy.js --network polygon
```

## ✅ Contract Verification

After deployment, verify the contract on block explorers:

```bash
npx hardhat verify --network <network-name> <CONTRACT_ADDRESS> "<OWNER_ADDRESS>"
```

Example for Sepolia:
```bash
npx hardhat verify --network sepolia 0x123... "0xYourOwnerAddress..."
```

## 📄 Frontend Integration

After deployment, you need three pieces of information for the frontend:

### 1. Contract Address
Displayed in the deployment output. Example:
```
📍 Contract Address: 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb
```

### 2. Contract ABI
Located at:
```
artifacts/contracts/CCICoin.sol/CCICoin.json
```

### 3. Network Configuration
Ensure your frontend connects to the same network:
- **Sepolia:** Chain ID `11155111`
- **BNB Chain:** Chain ID `56`
- **Polygon:** Chain ID `137`

### MetaMask Configuration

Update the frontend's API configuration:
```javascript
const CCI_CONTRACT_ADDRESS = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb";
const CCI_ABI = require("./artifacts/contracts/CCICoin.sol/CCICoin.json").abi;
const NETWORK_ID = 137; // Polygon
```

## 🔒 Security

- ✅ Uses OpenZeppelin's audited ERC-20 implementation
- ✅ No custom transfer/balance logic
- ✅ Private keys managed via `.env` (never committed)
- ✅ Comprehensive test coverage
- ✅ Owner cannot arbitrarily change user balances
- ✅ Fixed supply prevents inflation

### Pre-Deployment Checklist

Before mainnet deployment:

- [ ] All tests passing (`npx hardhat test`)
- [ ] Contract compiled without warnings
- [ ] Deployed and tested on Sepolia testnet
- [ ] Contract verified on block explorer
- [ ] Private keys secured and backed up
- [ ] .env file never committed to git
- [ ] Owner address is a secure hardware wallet

## 📊 Test Coverage

```
CCICoin
  Deployment
    ✓ Should set the correct name and symbol
    ✓ Should have 18 decimals
    ✓ Should mint total supply to deployer
    ✓ Should have correct total supply
    ✓ Should set the correct owner
  Transactions
    ✓ Should transfer tokens between accounts
    ✓ Should fail if sender doesn't have enough tokens
    ✓ Should update balances after transfers
  Allowances
    ✓ Should approve tokens for delegated transfer
    ✓ Should allow delegated transfers with transferFrom
    ✓ Should fail transferFrom without sufficient allowance
    ✓ Should fail transferFrom exceeding allowance
  Ownership
    ✓ Should allow owner to transfer ownership
    ✓ Should prevent non-owners from transferring ownership
    ✓ Should allow owner to renounce ownership

15 passing (1s)
```

## 📜 License

MIT License - See LICENSE file for details

## 🔗 Links

- **Documentation:** [CCI Coin Enterprise Platform Docs](../README.md)
- **Frontend:** [Frontend Dashboard](../frontend/)
- **OpenZeppelin:** [https://openzeppelin.com/contracts](https://openzeppelin.com/contracts)
- **Hardhat:** [https://hardhat.org](https://hardhat.org)

## 🤝 Contributing

This is a production-ready smart contract. Any changes should:
1. Pass all existing tests
2. Add new tests for new functionality
3. Follow OpenZeppelin security patterns
4. Be reviewed by security experts

## ⚠️ Disclaimer

This smart contract has been tested but has not undergone a professional security audit. Deploy at your own risk. Always test thoroughly on testnets before mainnet deployment.

---

**Built with ❤️ by CCI Digital Ventures**
