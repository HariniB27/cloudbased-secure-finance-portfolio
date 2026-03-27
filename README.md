# Secure Cloud-Based Hybrid AI Multi-Asset Portfolio Manager

A production-grade fintech web application for managing multi-asset portfolios with AI-powered insights, specifically designed for Indian markets.

## 🎯 Features

- **Multi-Asset Support**: Equity (NSE/BSE), Debt, Mutual Funds, Gold (24K/22K/18K/14K), Silver, Cash
- **Real-Time Pricing**: Live updates from yfinance, mfapi.in, and commodity APIs
- **Hybrid AI System**:
  - RandomForest ML classifier for risk prediction (LOW/MODERATE/HIGH)
  - LLM advisor (AWS Bedrock Claude / Mock mode) for actionable insights
- **Security-First**: JWT authentication, bcrypt password hashing, protected APIs
- **PDF Export**: Professional portfolio reports with charts and AI recommendations
- **INR-Native**: All calculations and displays in Indian Rupees (₹)
- **Cloud-Ready**: Designed for AWS (EB/EC2 + RDS + S3 + Bedrock)

## 📁 Project Structure

```
secure-portfolio-app/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── routes/            # API endpoints
│   │   ├── services/          # Business logic
│   │   ├── providers/         # Data providers (equity, gold, MF)
│   │   ├── ml/                # ML feature extraction + model
│   │   └── middleware/        # Auth middleware
│   ├── scripts/               # Training & DB init scripts
│   └── requirements.txt
├── frontend/                   # Next.js frontend
│   ├── src/
│   │   ├── app/               # Pages (register, login, dashboard)
│   │   ├── components/        # React components
│   │   ├── lib/               # API client, auth, utils
│   │   └── types/             # TypeScript types
│   └── package.json
├── docker-compose.yml          # PostgreSQL container
└── README.md
```

## 🚀 Quick Start (macOS)

### Prerequisites

- Python 3.10+
- Node.js 18+
- Docker Desktop
- PostgreSQL (via Docker)

### 1. Clone and Setup

```bash
cd secure-portfolio-app
```

### 2. Start PostgreSQL Database

```bash
# Start Docker Desktop first, then:
docker-compose up -d

# Verify database is running
docker ps
```

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# IMPORTANT: Edit .env and set a secure JWT_SECRET_KEY
# Generate one with: python -c "import secrets; print(secrets.token_urlsafe(32))"
nano .env  # or use your preferred editor

# Initialize database
python scripts/init_db.py

# Train ML risk model
python scripts/train_model.py

# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: `http://localhost:8000`
API docs at: `http://localhost:8000/docs`

### 4. Frontend Setup (New Terminal)

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local file
cp .env.local.example .env.local

# Start development server
npm run dev
```

Frontend will be available at: `http://localhost:3000`

## 📝 Testing the Application

### 1. Register a New User

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "SecurePass123!"
  }'
```

### 2. Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "SecurePass123!"
  }'
```

Save the `access_token` from the response.

### 3. Add an Asset

```bash
# Replace YOUR_TOKEN with the token from login
curl -X POST http://localhost:8000/assets \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "asset_type": "equity",
    "name": "Reliance Industries",
    "symbol": "RELIANCE",
    "exchange": "NSE",
    "invested_amount": 100000,
    "quantity": 35
  }'
```

### 4. Add Gold Asset

```bash
curl -X POST http://localhost:8000/assets \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "asset_type": "gold",
    "name": "Gold 24K",
    "karat": "24K",
    "invested_amount": 50000,
    "quantity": 10
  }'
```

### 5. Refresh Prices

```bash
curl -X POST http://localhost:8000/portfolio/refresh \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 6. Get Portfolio Summary

```bash
curl -X GET http://localhost:8000/portfolio/summary \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 7. Get Risk Prediction

```bash
curl -X POST http://localhost:8000/risk/predict \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 8. Get AI Advice

```bash
curl -X POST http://localhost:8000/advisor \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 9. Export PDF

```bash
curl -X GET http://localhost:8000/export/pdf \
  -H "Authorization: Bearer YOUR_TOKEN" \
  --output portfolio_report.pdf
```

## 🎨 Using the Web Interface

1. Navigate to `http://localhost:3000`
2. Click "Register" and create an account
3. Login with your credentials
4. You'll be redirected to the dashboard
5. Click "Add Asset" to add holdings:
   - **Equity**: Enter symbol (e.g., TCS, INFY), exchange (NSE/BSE), quantity
   - **Gold**: Select karat (24K/22K/18K/14K), enter grams
   - **Mutual Fund**: Enter scheme code from mfapi.in, units
   - **Cash**: Enter amount, optional interest rate
6. Click "Refresh Prices" to update current values
7. View allocation chart, P&L, and risk assessment
8. Read AI advisor recommendations
9. Click "Export PDF" to download report

## 🏗️ Architecture

### Backend (FastAPI)

- **Auth**: JWT tokens, bcrypt password hashing
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Pricing Providers**:
  - Equity: yfinance with .NS/.BO suffixes
  - Gold/Silver: Fallback rates with karat calculations
  - Mutual Funds: mfapi.in NAV data
- **ML**: RandomForest classifier trained on synthetic data
- **LLM**: AWS Bedrock Claude (optional) or deterministic mock
- **PDF**: ReportLab for professional reports

### Frontend (Next.js 14)

- **App Router**: React Server Components
- **Styling**: TailwindCSS + shadcn/ui components
- **Charts**: Recharts for allocation donut
- **State**: React hooks, no global state needed
- **TypeScript**: Full type safety

## 🔧 Configuration

### Backend Environment Variables (.env)

```env
# Database
DATABASE_URL=postgresql://portfolio_user:portfolio_pass@localhost:5432/portfolio_db

# JWT (CHANGE THIS!)
JWT_SECRET_KEY=your-secret-key-min-32-chars
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
FRONTEND_URL=http://localhost:3000

# AWS Bedrock (optional)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0

# App
USE_MOCK_LLM=true  # Set to false to use real Bedrock
ENVIRONMENT=development
```

### Frontend Environment Variables (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📊 ML Risk Model

The risk classifier uses 10 deterministic features:

1. **total_return**: (current - invested) / invested
2. **volatility_proxy**: Weighted by asset type risk
3. **momentum_proxy**: Rolling price change (0 if no history)
4. **drawdown_proxy**: Concentration × volatility
5. **risk_score**: return / (volatility + ε)
6. **equity_allocation**: % in equity
7. **debt_allocation**: % in debt + MF
8. **commodity_allocation**: % in gold + silver
9. **cash_allocation**: % in cash
10. **concentration_hhi**: Herfindahl-Hirschman Index

### Training Data Rules

- **LOW**: risk_score > 1.0, volatility < 0.10
- **MODERATE**: risk_score 0.3-1.0, volatility 0.10-0.20
- **HIGH**: risk_score < 0.3 or volatility > 0.20

Model saved at: `backend/app/ml/risk_model.pkl`

## 🔐 Security Features

- **Password Hashing**: bcrypt with salt
- **JWT Tokens**: Short expiry (30 min default)
- **Protected Routes**: All asset/portfolio endpoints require auth
- **Input Validation**: Pydantic schemas
- **CORS**: Configured for localhost only
- **SQL Injection**: Protected via SQLAlchemy ORM
- **Rate Limiting**: Placeholder in code for production

## 🚢 Production Deployment (AWS)

### Future Cloud Architecture

```
┌─────────────────┐
│   CloudFront    │  (Frontend CDN)
└────────┬────────┘
         │
┌────────▼────────┐
│   S3 Bucket     │  (Static Next.js)
└─────────────────┘

┌─────────────────┐
│  Elastic Beanst │  (FastAPI backend)
│  or EC2 + ALB   │
└────────┬────────┘
         │
┌────────▼────────┐
│   RDS Postgres  │  (Database)
└─────────────────┘

┌─────────────────┐
│  AWS Bedrock    │  (LLM Advisor)
└─────────────────┘

┌─────────────────┐
│  S3 Bucket      │  (PDF storage)
└─────────────────┘
```

### Deployment Steps (Summary)

1. **RDS Setup**: Create PostgreSQL 15 instance
2. **Backend**: Package with `eb init` and `eb deploy`
3. **Frontend**: Build static export, deploy to S3 + CloudFront
4. **Secrets**: Move to AWS Secrets Manager
5. **Bedrock**: Enable in AWS console, update IAM roles

## 🧪 Development Notes

### Adding New Asset Types

1. Update `AssetType` enum in `backend/app/models/asset.py`
2. Create provider in `backend/app/providers/`
3. Update `AssetService._calculate_current_value()`
4. Add UI form fields in `frontend/src/components/AddAssetModal.tsx`

### Updating Risk Model

1. Modify `scripts/train_model.py` with new features
2. Run `python scripts/train_model.py`
3. Update `ml/feature_extractor.py` to match features
4. Restart backend

### Customizing LLM Prompts

Edit `advisor_service.py` → `_generate_llm_advice()` method

## 📦 API Endpoints Reference

### Authentication
- `POST /auth/register` - Create account
- `POST /auth/login` - Get JWT token
- `GET /auth/me` - Get current user

### Assets
- `POST /assets` - Create asset
- `GET /assets` - List all assets
- `GET /assets/{id}` - Get one asset
- `PUT /assets/{id}` - Update asset
- `DELETE /assets/{id}` - Delete asset

### Portfolio
- `POST /portfolio/refresh` - Update all prices
- `GET /portfolio/summary` - Totals and allocation
- `GET /portfolio/features` - ML features

### Risk & Advice
- `POST /risk/predict` - ML risk classification
- `POST /advisor` - AI recommendations

### Export
- `GET /export/pdf` - Download PDF report

## 🐛 Troubleshooting

### Database Connection Error

```bash
# Check if PostgreSQL is running
docker ps

# Restart if needed
docker-compose restart

# Check logs
docker-compose logs postgres
```

### Port Already in Use

```bash
# Backend (8000)
lsof -ti:8000 | xargs kill -9

# Frontend (3000)
lsof -ti:3000 | xargs kill -9
```

### JWT Token Invalid

- Check `.env` has correct `JWT_SECRET_KEY`
- Token expires after 30 minutes - login again
- Clear localStorage in browser DevTools

### Prices Not Updating

- yfinance has rate limits - wait 10 seconds between refreshes
- Ensure symbol format is correct (RELIANCE.NS, not RELIANCE)
- Check console logs for provider errors

### ML Model Not Found

```bash
cd backend
python scripts/train_model.py
```

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [yfinance Documentation](https://github.com/ranaroussi/yfinance)
- [mfapi.in Documentation](https://www.mfapi.in/)

## 📄 License

This is a demonstration project for educational purposes.

## 🤝 Contributing

This is a complete standalone application. For production use:
1. Add comprehensive test suite
2. Implement rate limiting
3. Add Sentry for error tracking
4. Set up CI/CD pipeline
5. Enable HTTPS/SSL
6. Add user email verification
7. Implement forgot password flow
8. Add audit logging

---

**Built with ❤️ for the Indian fintech ecosystem**
