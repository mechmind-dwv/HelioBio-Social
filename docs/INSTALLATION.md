# HelioBio-Social Installation Guide

Complete guide for setting up the HelioBio-Social research platform.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Manual Installation](#manual-installation)
4. [Docker Installation](#docker-installation)
5. [Configuration](#configuration)
6. [Verification](#verification)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software
- **Python 3.9+** - [Download](https://www.python.org/downloads/)
- **Node.js 16+** - [Download](https://nodejs.org/)
- **Git** - [Download](https://git-scm.com/)

### Optional (Recommended)
- **PostgreSQL 13+** - For production database
- **Redis 6+** - For caching
- **Docker & Docker Compose** - For containerized deployment

### System Requirements
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB for application + data
- **OS**: Linux, macOS, or Windows (WSL2 recommended)

---

## Quick Start

### Option 1: Automated Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-username/HelioBio-Social.git
cd HelioBio-Social

# Run automated setup
chmod +x quickstart.sh
./quickstart.sh

# Start all services
./start_all.sh
```

Access the application:
- **Dashboard**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Jupyter Lab**: http://localhost:8888

### Option 2: Docker (Easiest)

```bash
# Clone repository
git clone https://github.com/your-username/HelioBio-Social.git
cd HelioBio-Social

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Start with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f
```

---

## Manual Installation

### 1. Clone Repository

```bash
git clone https://github.com/your-username/HelioBio-Social.git
cd HelioBio-Social
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Setup database (if PostgreSQL installed)
python setup_db.py

# Start backend
uvicorn main:app --reload --port 8000
```

Backend will be available at: http://localhost:8000

### 3. Frontend Setup

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

Frontend will be available at: http://localhost:3000

### 4. Jupyter Analysis Setup

Open a new terminal:

```bash
cd analysis

# Activate backend virtual environment
source ../backend/venv/bin/activate

# Install Jupyter
pip install jupyter jupyterlab

# Start Jupyter Lab
jupyter lab
```

Jupyter will be available at: http://localhost:8888

---

## Docker Installation

### Prerequisites
- Docker 20.10+
- Docker Compose 1.29+

### Setup

1. **Clone and configure**:
```bash
git clone https://github.com/your-username/HelioBio-Social.git
cd HelioBio-Social
cp .env.example .env
```

2. **Edit `.env` file** with your API keys:
```bash
nano .env  # or use your preferred editor
```

3. **Build and start services**:
```bash
docker-compose up -d
```

4. **Check status**:
```bash
docker-compose ps
```

All services should show "Up" status.

### Docker Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f [service_name]

# Restart a service
docker-compose restart [service_name]

# Access database
docker-compose exec database psql -U heliobio

# Access backend shell
docker-compose exec backend bash

# Rebuild after code changes
docker-compose up -d --build
```

---

## Configuration

### Environment Variables

Create `.env` file in project root:

```bash
# Application
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=your-secret-key-here

# Database (if using local PostgreSQL)
DATABASE_URL=postgresql+asyncpg://heliobio:password@localhost:5432/heliobio

# Redis (if using local Redis)
REDIS_URL=redis://localhost:6379/0

# External APIs
NOAA_API_KEY=your-noaa-key
NASA_API_KEY=DEMO_KEY
WHO_API_URL=https://ghoapi.azureedge.net/api
GOOGLE_TRENDS_API_KEY=your-google-key

# Analysis Parameters
CORRELATION_MIN_OBSERVATIONS=30
ALPHA_LEVEL=0.05
FDR_METHOD=fdr_bh
```

### API Keys

#### NOAA Space Weather API
- **Free**: No key required for most endpoints
- **URL**: https://www.swpc.noaa.gov/products

#### NASA API
- **Free**: Get key at https://api.nasa.gov/
- **Default**: DEMO_KEY (rate limited)

#### Google Trends
- **Free**: Use `pytrends` library (no key needed)
- **Alternative**: Use official API with key

### Database Configuration

#### SQLite (Development)
```python
DATABASE_URL=sqlite+aiosqlite:///./heliobio.db
```

#### PostgreSQL (Production)
```bash
# Install PostgreSQL
sudo apt install postgresql  # Linux
brew install postgresql      # Mac

# Create database
sudo -u postgres psql
CREATE DATABASE heliobio;
CREATE USER heliobio WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE heliobio TO heliobio;
\q

# Update .env
DATABASE_URL=postgresql+asyncpg://heliobio:your_password@localhost:5432/heliobio
```

#### TimescaleDB (Recommended for Time Series)
```bash
# Install TimescaleDB extension
sudo add-apt-repository ppa:timescale/timescaledb-ppa
sudo apt update
sudo apt install timescaledb-postgresql-14

# Enable extension
psql -U heliobio -d heliobio
CREATE EXTENSION IF NOT EXISTS timescaledb;
```

---

## Verification

### Check Backend

```bash
# Health check
curl http://localhost:8000/health

# Expected response:
{
  "status": "healthy",
  "version": "2.0.1",
  "timestamp": "2025-XX-XXTXX:XX:XX"
}

# API documentation
open http://localhost:8000/docs
```

### Check Frontend

```bash
# Open in browser
open http://localhost:3000

# Should see HelioBio-Social dashboard
```

### Test API Endpoints

```python
import requests

# Test solar data endpoint
response = requests.get('http://localhost:8000/api/v1/solar/current')
print(response.json())

# Test correlation endpoint
response = requests.post('http://localhost:8000/api/v1/correlation/analyze', json={
    'solar_variable': 'kp_index',
    'target_variable': 'anxiety_searches',
    'start_date': '2024-01-01',
    'end_date': '2024-12-31',
    'method': 'pearson'
})
print(response.json())
```

### Run Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# Analysis notebooks
cd analysis
jupyter nbconvert --execute --to notebook notebooks/*.ipynb
```

---

## Troubleshooting

### Common Issues

#### 1. Port Already in Use

```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9  # Mac/Linux
netstat -ano | findstr :8000   # Windows

# Or use different port
uvicorn main:app --port 8001
```

#### 2. Database Connection Failed

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql  # Linux
brew services list                # Mac

# Verify credentials
psql -U heliobio -d heliobio -h localhost

# Reset database
python backend/setup_db.py --reset
```

#### 3. Module Not Found

```bash
# Reinstall dependencies
cd backend
pip install -r requirements.txt --force-reinstall

cd frontend
rm -rf node_modules package-lock.json
npm install
```

#### 4. API Key Errors

```bash
# Check .env file exists
ls -la .env

# Verify environment variables loaded
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('NOAA_API_KEY'))"
```

#### 5. Docker Issues

```bash
# Reset Docker
docker-compose down -v
docker system prune -a
docker-compose up -d --build

# Check logs
docker-compose logs -f backend
```

### Getting Help

If you encounter issues:

1. **Check logs**:
   ```bash
   # Backend logs
   tail -f backend/logs/app.log
   
   # Docker logs
   docker-compose logs -f
   ```

2. **Search existing issues**: [GitHub Issues](https://github.com/your-username/HelioBio-Social/issues)

3. **Create new issue**: Include:
   - OS and versions (Python, Node, Docker)
   - Error messages
   - Steps to reproduce
   - Logs

4. **Community**: Join discussions on GitHub

---

## Next Steps

After successful installation:

1. **Configure API Keys**: Edit `.env` with real API credentials
2. **Explore Dashboard**: Open http://localhost:3000
3. **Read API Docs**: Visit http://localhost:8000/docs
4. **Run Analysis**: Open Jupyter Lab and try example notebooks
5. **Customize**: Modify code to fit your research needs

---

## Production Deployment

For production deployment, see:
- [DEPLOYMENT.md](DEPLOYMENT.md) - Production setup guide
- [docker/README.md](docker/README.md) - Docker production config
- [deployment/kubernetes/](deployment/kubernetes/) - Kubernetes manifests

Key considerations:
- Use PostgreSQL with TimescaleDB
- Enable Redis caching
- Set `DEBUG=false`
- Use strong `SECRET_KEY`
- Configure HTTPS/SSL
- Set up monitoring (Prometheus, Grafana)
- Implement rate limiting
- Regular database backups

---

## Updating

To update to latest version:

```bash
# Pull latest code
git pull origin main

# Update backend dependencies
cd backend
pip install -r requirements.txt --upgrade

# Update frontend dependencies
cd frontend
npm update

# Restart services
docker-compose restart  # if using Docker
# or restart manually
```

---

## Support

- **Documentation**: [docs/](docs/)
- **GitHub**: [HelioBio-Social Repository](https://github.com/your-username/HelioBio-Social)
- **Issues**: [Report a bug](https://github.com/your-username/HelioBio-Social/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/HelioBio-Social/discussions)

---

**Happy Researching! 🌞🌍**
