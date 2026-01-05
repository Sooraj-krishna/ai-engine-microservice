# Setup & Installation Guide

## Prerequisites

### Required Software

- **Python 3.10 or higher**
- **Node.js 18 or higher**
- **npm or yarn**
- **Git**

### Required Accounts & API Keys

1. **GitHub Account**

   - Personal Access Token with `repo` permissions
   - Repository for your website code

2. **Google Gemini API**

   - API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Model: `gemini-1.5-flash` (recommended) or `gemini-pro`

3. **Google Analytics (Optional)**
   - GA4 property ID
   - Service account JSON key with Analytics API access

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/ai-engine-microservice.git
cd ai-engine-microservice
```

### 2. Backend Setup

#### Create Python Virtual Environment

```bash
python3 -m venv venv

# Linux/macOS
source venv/bin/activate

# Windows
venv\\Scripts\\activate
```

#### Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Key Dependencies**:

- `fastapi` - Web framework
- `playwright` - Browser automation
- `google-generativeai` - Gemini AI
- `PyGithub` - GitHub API
- `lighthouse-python` - Performance auditing

#### Install Playwright Browsers

```bash
playwright install
```

### 3. Frontend Setup

```bash
cd ai-engine-ui
npm install
cd ..
```

### 4. Environment Configuration

#### Copy Environment Template

```bash
cp .env.example .env
```

#### Edit `.env` File

```bash
# Required Configuration
WEBSITE_URL=https://yoursite.com
GITHUB_TOKEN=ghp_your_github_personal_access_token
GITHUB_REPO=yourusername/yourrepo
GEMINI_API_KEY=your_gemini_api_key_here

# Monitoring Mode
MONITORING_MODE=simple  # Options: simple, ga_only, ga_logs

# Competitive Analysis
COMPETITOR_URLS=https://competitor1.com,https://competitor2.com
ENABLE_COMPETITIVE_ANALYSIS=true

# Optional: Google Analytics
GA4_PROPERTY_ID=123456789
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json

# AI Model Settings
GEMINI_MODEL=gemini-1.5-flash
```

See [CONFIGURATION.md](./CONFIGURATION.md) for detailed configuration options.

### 5. Verify Installation

```bash
# Start backend
cd src
python3 main_with_config.py
```

You should see:

```
[INFO] Starting Enhanced AI Engine Microservice with Safety Features...
[INFO] Website: https://yoursite.com
INFO:     Uvicorn running on http://0.0.0.0:8000
```

In a new terminal:

```bash
# Start frontend
cd ai-engine-ui
npm run dev
```

Visit:

- **Backend API**: http://localhost:8000
- **Frontend UI**: http://localhost:3000

## Configuration Details

### GitHub Token Setup

1. Go to GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token (classic)
3. Select scopes:
   - ✅ `repo` (Full control of private repositories)
4. Copy token to `.env` as `GITHUB_TOKEN`

### Google Gemini API Setup

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create new API key
3. Copy to `.env` as `GEMINI_API_KEY`

### Google Analytics Setup (Optional)

1. Create service account in Google Cloud Console
2. Enable Google Analytics Data API
3. Download JSON key file
4. Grant service account access to GA4 property
5. Set paths in `.env`:
   ```
   GA4_PROPERTY_ID=123456789
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
   ```

## Running the Application

### Development Mode

**Backend** (Terminal 1):

```bash
cd src
python3 main_with_config.py
```

**Frontend** (Terminal 2):

```bash
cd ai-engine-ui
npm run dev
```

### Production Mode

**Backend**:

```bash
cd src
uvicorn main_with_config:app --host 0.0.0.0 --port 8000
```

**Frontend**:

```bash
cd ai-engine-ui
npm run build
npm start
```

## Docker Deployment (Optional)

```bash
# Build image
docker build -t ai-engine .

# Run container
docker run -d \
  --env-file .env \
  -p 8000:8000 \
  ai-engine
```

## Verification Checklist

After setup, verify:

- [ ] Backend starts without errors
- [ ] Frontend loads at http://localhost:3000
- [ ] Can access API docs at http://localhost:8000/docs
- [ ] Status endpoint returns: `curl http://localhost:8000/status`
- [ ] UI shows "AI Engine Configuration" panel
- [ ] Real-time logs stream in UI
- [ ] Can trigger maintenance cycle via `/run` endpoint

## Common Issues

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000
# Kill process
kill -9 <PID>
```

### Module Not Found Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Playwright Browser Issues

```bash
# Reinstall browsers
playwright install --force
```

### Permission Errors

```bash
# Fix file permissions
chmod +x start-ui.sh
chmod +x setup_testing_deps.sh
```

See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for more solutions.

## Next Steps

1. **Configure your site**: Update `.env` with your website URL
2. **Test the system**: Run `POST /run` to trigger first maintenance cycle
3. **Review PRs**: Check GitHub for generated pull requests
4. **Set up monitoring**: Configure Google Analytics if needed
5. **Try competitive analysis**: Add competitor URLs and run analysis

Read [FEATURES.md](./FEATURES.md) to learn about all available features!
