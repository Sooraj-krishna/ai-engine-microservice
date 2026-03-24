# AI Engine Microservice

> **Self-maintaining SaaS platform** that automatically detects bugs, analyzes performance, generates fixes, and implements competitive features - all powered by AI.

## 🚀 Overview

AI Engine Microservice is an intelligent automation platform that:

- **Monitors** your website for bugs, performance issues, and accessibility problems
- **Analyzes** competitor websites to identify missing features
- **Generates** code fixes automatically using AI
- **Validates** and tests all changes before deployment
- **Deploys** improvements via GitHub Pull Requests

## ✨ Key Features

### 🔍 Automated Bug Detection

- **Enhanced Bug Detection**: Lighthouse audits, Axe accessibility testing, JavaScript error detection
- **Performance Monitoring**: Core Web Vitals tracking (LCP, FID, CLS)
- **Error Tracking**: Console errors and crash detection

### 🤖 AI-Powered Fix Generation

- **Intelligent Code Generation**: Context-aware fixes using Gemini AI
- **Incremental Fixing**: Smart, targeted changes to existing code
- **Safe Utility Creation**: Additive improvements without breaking changes

### ✅ Safety & Validation

- **Multi-Layer Validation**: Syntax checking, execution testing, browser compatibility
- **Isolated Testing**: Fixes tested in sandbox before applying
- **Rollback Protection**: Automatic rollback if issues detected

### 🎯 Competitive Analysis

- **Feature Gap Detection**: Analyzes competitor sites to find missing features
- **AI-Powered Prioritization**: Ranks features by business impact and effort
- **Natural Language Reports**: Easy-to-understand recommendations

### 📊 Modern Web UI

- **Real-time Monitoring**: Live logs and system status
- **Configuration Dashboard**: Easy setup and management
- **Feature Recommendations**: Interactive competitive analysis results

## 📁 Project Structure

```
ai-engine-microservice/
├── src/                          # Backend Python microservice
│   ├── main_with_config.py      # FastAPI server with all features
│   ├── enhanced_bug_detector.py # Comprehensive bug detection
│   ├── improved_fixer.py        # Incremental code fixing
│   ├── generator.py             # AI fix generation
│   ├── validator.py             # Code validation system
│   ├── fix_tester.py            # Isolated fix testing
│   ├── competitive_analyzer.py  # Competitor analysis
│   ├── feature_extractor.py     # Feature detection from sites
│   ├── github_handler.py        # GitHub PR automation
│   └── ...
├── ai-engine-ui/                # Next.js web interface
│   ├── src/
│   │   ├── app/                 # Next.js pages
│   │   └── components/          # React components
│   └── ...
├── documentation/               # Project documentation (this folder)
├── tests/                       # pytest test suite
├── .env.example                 # Environment variables template
└── requirements.txt             # Python dependencies
```

## 🎯 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- GitHub account with repository access
- Google Gemini API key

### Installation

```bash
# 1. Clone repository
git clone https://github.com/yourusername/ai-engine-microservice.git
cd ai-engine-microservice

# 2. Install Python dependencies
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
pip install -r requirements.txt

# 3. Install UI dependencies
cd ai-engine-ui
npm install
cd ..

# 4. Configure environment
cp .env.example .env
# Edit .env with your credentials (see SETUP.md)

# 5. Start backend
cd src
python3 main_with_config.py

# 6. Start UI (new terminal)
cd ai-engine-ui
npm run dev
```

Visit http://localhost:3000 to access the UI!

## 📖 Documentation

Comprehensive guides available in the `documentation/` folder:

- **[SETUP.md](./SETUP.md)** - Installation and configuration
- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Deploying to Render
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - System design and components
- **[API.md](./API.md)** - REST API endpoints
- **[CONFIGURATION.md](./CONFIGURATION.md)** - Environment variables
- **[FEATURES.md](./FEATURES.md)** - Feature documentation
- **[CODE_DOCUMENTATION.md](./CODE_DOCUMENTATION.md)** - Per-file implementation details
- **[DEVELOPMENT.md](./DEVELOPMENT.md)** - Development guide
- **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)** - Common issues

## 🔑 Key APIs

```bash
# Trigger maintenance cycle
POST http://localhost:8000/run

# Check system status
GET http://localhost:8000/status

# Run competitive analysis
POST http://localhost:8000/analyze-competitors

# Get feature recommendations
GET http://localhost:8000/feature-recommendations
```

See [API.md](./API.md) for full API documentation.

## 🛡️ Safety Features

- **Code Validation**: All generated code is validated for syntax and safety
- **Isolated Testing**: Fixes tested in sandbox environment
- **Rollback Protection**: Automatic rollback if errors detected
- **Manual Approval**: Changes submitted as PRs for review
- **Audit Logging**: All actions logged for transparency

## 🤝 Contributing

We welcome contributions! Please see [DEVELOPMENT.md](./DEVELOPMENT.md) for guidelines.

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- **Issues**: GitHub Issues for bug reports
- **Documentation**: See `documentation/` folder
- **Troubleshooting**: [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)

## 🎉 Acknowledgments

Built with:

- **FastAPI** - Modern Python web framework
- **Next.js** - React framework for UI
- **Playwright** - Browser automation
- **Google Gemini** - AI code generation
- **Lighthouse** - Performance auditing
