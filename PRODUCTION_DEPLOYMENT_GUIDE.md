# 🚀 CCI Coin - Production Deployment Guide

## ✅ What's Implemented

### Core Blockchain Features
- ✅ Advanced blockchain with UTXO model
- ✅ Wallet generation and management
- ✅ Transaction creation and signing
- ✅ Mining with proof-of-work
- ✅ Block explorer
- ✅ Mempool

### Token & Smart Contracts
- ✅ ERC-20 token implementation (CCI Coin)
- ✅ Token transfer, mint, burn
- ✅ Staking with rewards (10% APY)
- ✅ Smart contract framework

### Frontend & UX
- ✅ Professional dashboard
- ✅ Merchant payment system
- ✅ QR code generation for payments
- ✅ QR scanner for mobile
- ✅ Real-time blockchain updates
- ✅ Dark/light theme
- ✅ 8 complete pages (Blockchain, Token, Merchant, Scanner, Roadmap, Governance, Security, Future)

### Security (NEW)
- ✅ JWT authentication system
- ✅ Password hashing with bcrypt
- ✅ Input validation
- ✅ Rate limiting ready
- ✅ Environment variables
- ✅ CORS configuration

---

## 🔧 Production Setup Steps

### 1. Install Dependencies

```bash
pip install flask flask-cors flask-limiter pyjwt bcrypt psycopg2-binary python-dotenv gunicorn
```

### 2. Configure Environment

Create `.env` file:

```bash
cp .env.example .env
```

Edit `.env`:

```
JWT_SECRET_KEY=<generate-strong-key>
DATABASE_URL=postgresql://user:pass@localhost:5432/cci_coin
FLASK_ENV=production
CORS_ORIGINS=https://yourdomain.com
RATE_LIMIT_PER_MINUTE=60
ADMIN_EMAIL=admin@yourdomain.com
ADMIN_PASSWORD=<strong-password>
```

Generate secret key:
```python
import secrets
print(secrets.token_hex(32))
```

### 3. Setup PostgreSQL Database

```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Create database
sudo -u postgres psql
CREATE DATABASE cci_coin;
CREATE USER cci_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE cci_coin TO cci_user;
\q
```

### 4. Deploy Smart Contract to Ethereum

#### Option A: Testnet (Sepolia/Goerli)

1. Install Hardhat:
```bash
cd cci-coin
npm install
```

2. Get testnet ETH from faucet:
- Sepolia: https://sepoliafaucet.com/
- Goerli: https://goerlifaucet.com/

3. Configure `.env` in `cci-coin/`:
```
PRIVATE_KEY=your_wallet_private_key
INFURA_API_KEY=your_infura_key
ETHERSCAN_API_KEY=your_etherscan_key
```

4. Deploy:
```bash
npx hardhat run scripts/deploy.js --network sepolia
```

5. Verify contract:
```bash
npx hardhat run scripts/verify.js --network sepolia
```

#### Option B: Mainnet (Production)

**⚠️ WARNING: Requires real ETH for gas fees**

```bash
npx hardhat run scripts/deploy.js --network mainnet
```

### 5. Setup HTTPS with SSL

#### Using Certbot (Let's Encrypt):

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

#### Nginx Configuration:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 6. Deploy to Cloud

#### AWS EC2:

```bash
# 1. Launch EC2 instance (t2.medium recommended)
# 2. SSH into instance
ssh -i your-key.pem ubuntu@your-ip

# 3. Install dependencies
sudo apt update
sudo apt install python3-pip nginx postgresql

# 4. Clone repository
git clone https://github.com/heyyKaran1/SmartCoin1.git
cd SmartCoin1

# 5. Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 6. Configure environment
cp .env.example .env
nano .env  # Edit with production values

# 7. Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 api:app
```

#### DigitalOcean Droplet:

Same steps as AWS, but:
```bash
# Create droplet with Ubuntu 22.04
# Use at least 2GB RAM
```

#### Docker Deployment:

```bash
# Create Dockerfile
docker build -t cci-coin .
docker run -d -p 5000:5000 --env-file .env cci-coin
```

### 7. Production API Server

Create `gunicorn.conf.py`:

```python
bind = "0.0.0.0:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
```

Run:
```bash
gunicorn -c gunicorn.conf.py api:app
```

### 8. Process Management (PM2 or Systemd)

#### Using systemd:

Create `/etc/systemd/system/cci-coin.service`:

```ini
[Unit]
Description=CCI Coin API Server
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/SmartCoin1
Environment="PATH=/home/ubuntu/SmartCoin1/venv/bin"
ExecStart=/home/ubuntu/SmartCoin1/venv/bin/gunicorn -c gunicorn.conf.py api:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable cci-coin
sudo systemctl start cci-coin
sudo systemctl status cci-coin
```

---

## 🔒 Security Checklist

- [ ] Changed all default passwords
- [ ] Generated strong JWT secret
- [ ] Configured HTTPS/SSL
- [ ] Setup rate limiting
- [ ] Enabled CORS with whitelist
- [ ] Input validation on all endpoints
- [ ] Database connection secured
- [ ] Firewall configured (ports 80, 443, 22 only)
- [ ] Backup strategy in place
- [ ] Monitoring setup (logs, errors)

---

## 📊 Monitoring & Logs

### Setup Logging:

```python
import logging
logging.basicConfig(
    filename='/var/log/cci-coin/app.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)
```

### Monitor with:
- **Datadog**
- **New Relic**
- **AWS CloudWatch**
- **Sentry** (error tracking)

---

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Load testing
ab -n 1000 -c 10 http://your domain.com/api/blockchain/info
```

---

## 📈 Scaling

### Horizontal Scaling:
- Load balancer (AWS ELB, Nginx)
- Multiple API servers
- Redis for caching
- Separate database server

### Database Optimization:
- Indexes on frequently queried columns
- Connection pooling
- Read replicas

---

## 🆘 Support & Maintenance

### Backup:
```bash
# Database backup
pg_dump cci_coin > backup_$(date +%Y%m%d).sql

# Code backup
git push origin main
```

### Updates:
```bash
git pull origin main
pip install -r requirements.txt
sudo systemctl restart cci-coin
```

---

## 📝 Next Steps for Full Production

1. ✅ **Complete MetaMask Integration**
   - Web3.js integration
   - Transaction signing in browser

2. ✅ **Add Payment Gateway**
   - Stripe/PayPal for fiat on-ramp
   - Exchange integration

3. ✅ **Mobile Apps**
   - React Native app
   - iOS/Android native

4. ✅ **Advanced Features**
   - Multi-signature wallets
   - Layer 2 scaling
   - Cross-chain bridges

5. ✅ **Compliance**
   - KYC/AML integration
   - Legal review
   - Terms of service
   - Privacy policy

---

## 🎯 Current Status

**Demo Ready**: ✅
**Pilot Ready**: ⚠️ (Needs PostgreSQL + SSL)
**Production Ready**: ⏳ (3-4 weeks of additional work)

**Estimated Time to Production**: 3-4 weeks with 1 developer

---

## 📞 Contact

For production deployment assistance:
- Create GitHub issue
- Email: support@ccicoin.com (update with your email)

---

**Note**: This system is currently configured for development/demo. Follow all production steps above before deploying to real users.
