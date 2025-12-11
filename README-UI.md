# 🤖 AI Engine Microservice with Web UI

A complete self-maintaining SaaS solution with an intuitive web interface for configuration, monitoring, and control.

## 🌟 Features

### Backend (FastAPI)
- **Automated Code Analysis**: Detects performance, security, and UX issues
- **AI-Powered Fixes**: Uses Google Gemini AI for intelligent code generation
- **GitHub Integration**: Automatically creates pull requests with fixes
- **Safety Systems**: Validation, rollback protection, and change tracking
- **Multi-Source Monitoring**: Google Analytics, server logs, and system metrics

### Frontend (Next.js)
- **Configuration Management**: Easy setup of all required credentials
- **Real-time Logs**: Live monitoring with filtering and export
- **Status Dashboard**: Comprehensive system health monitoring
- **One-Click Operations**: Start maintenance cycles with a single click
- **Responsive Design**: Works on desktop and mobile devices

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)
```bash
# Clone and start everything
git clone <your-repo>
cd ai-engine-microservice
./start-ui.sh
```

### Option 2: Manual Setup

#### 1. Start the Backend
```bash
cd src
python3 main_with_config.py
```

#### 2. Start the Web UI
```bash
cd ai-engine-ui
npm install
npm run dev
```

#### 3. Access the Interface
- **Web UI**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📋 Prerequisites

- **Python 3.10+** with pip
- **Node.js 18+** with npm
- **Git** for repository access
- **GitHub Personal Access Token** with repo permissions
- **Google Gemini API Key** for AI code generation
- **Google Analytics Property ID** (optional, for website monitoring)

## ⚙️ Configuration

### 1. Web UI Configuration
1. Open http://localhost:3000
2. Fill in the configuration form:
   - **Website URL**: Your website to monitor
   - **GitHub Repository**: Format: `username/repository-name`
   - **GitHub Token**: Personal access token
   - **Gemini API Key**: Google AI API key
   - **GA Property ID**: Google Analytics property ID
3. Click "Test Connection" to verify
4. Click "Save Config" to update the backend

### 2. Environment Variables
The system automatically creates a `.env` file with your configuration:
```env
WEBSITE_URL=https://your-website.com
GITHUB_REPO=username/repository-name
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
GEMINI_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxx
GA4_PROPERTY_ID=123456789
MONITORING_MODE=simple
```

## 🎯 How to Use

### 1. Initial Setup
1. **Configure**: Enter your credentials in the web UI
2. **Test**: Verify the connection to the AI Engine
3. **Save**: Store your configuration

### 2. Run Maintenance
1. **Click "Run Maintenance"** in the web UI
2. **Monitor Logs**: Watch real-time progress in the logs panel
3. **Check Status**: View system health and recent activity
4. **Review PRs**: Check your GitHub repository for created pull requests

### 3. Monitor Results
- **Logs Panel**: Real-time system logs with filtering
- **Status Monitor**: System health and configuration status
- **GitHub**: Review and merge generated pull requests

## 🔧 API Endpoints

### Configuration
- `POST /configure` - Update system configuration
- `GET /config` - Get current configuration

### Monitoring
- `GET /health` - System health check
- `GET /status` - Detailed system status
- `POST /run` - Trigger maintenance cycle

### Safety
- `POST /manual-rollback` - Manual rollback trigger
- `POST /receive-frontend-data` - Receive frontend monitoring data

## 🛡️ Safety Features

### Multi-Layer Protection
1. **Conservative Analysis**: Only suggests safe, additive changes
2. **Code Validation**: Multiple validation layers before approval
3. **Rollback Protection**: Automatic and manual rollback capabilities
4. **Change Tracking**: Complete audit trail of all modifications
5. **Safe Mode Only**: Only processes issues marked as safe

### Generated Utilities
The system creates new utility files instead of modifying existing code:
- `utils/ai-memory-optimizer.js` - Memory optimization
- `utils/ai-accessibility-helper.js` - Accessibility improvements
- `utils/ai-security-helper.js` - Security enhancements
- `utils/ai-performance-monitor.js` - Performance monitoring
- `utils/ai-error-handler.js` - Error handling utilities

## 📊 Monitoring & Logs

### Real-time Logs
- **Live Streaming**: See system activity in real-time
- **Log Filtering**: Filter by level (Info, Success, Warning, Error, Debug)
- **Export**: Download logs for analysis
- **Statistics**: View log level distribution

### Status Monitoring
- **System Health**: Overall system status
- **Environment**: Configuration status
- **Recent Activity**: Last run, PRs, errors
- **Safety Features**: Validation and rollback status

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web UI        │    │   AI Engine     │    │   External      │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│   Services      │
│   Port 3000     │    │   Port 8000     │    │   (GitHub, GA)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔍 Troubleshooting

### Common Issues

1. **Connection Failed**
   - Ensure the AI Engine backend is running on port 8000
   - Check firewall settings
   - Verify Python dependencies are installed

2. **Configuration Not Saving**
   - Check that all required fields are filled
   - Verify GitHub token has correct permissions
   - Ensure Gemini API key is valid

3. **Logs Not Updating**
   - Make sure the maintenance cycle is running
   - Check browser console for errors
   - Verify CORS settings

4. **Pull Requests Not Created**
   - Verify GitHub token has repo write permissions
   - Check repository name format (username/repo-name)
   - Ensure the repository exists and is accessible

### Debug Mode
- Check browser console for detailed error messages
- View backend logs in the terminal
- Use the `/status` endpoint to check system health

## 📁 Project Structure

```
ai-engine-microservice/
├── src/                          # Backend (FastAPI)
│   ├── main_with_config.py      # Main application with UI support
│   ├── configure_endpoint.py    # Configuration API
│   ├── analyzer.py              # Issue detection
│   ├── generator.py             # AI code generation
│   ├── github_handler.py        # GitHub integration
│   ├── validator.py             # Code validation
│   └── rollback_manager.py      # Rollback protection
├── ai-engine-ui/                 # Frontend (Next.js)
│   ├── src/
│   │   ├── app/
│   │   │   └── page.tsx         # Main page
│   │   └── components/          # React components
│   └── package.json
├── start-ui.sh                   # Startup script
└── README-UI.md                 # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly with both backend and frontend
5. Submit a pull request

## 📄 License

This project is part of the AI Engine Microservice and follows the same license terms.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the API documentation at http://localhost:8000/docs
3. Check the logs in the web UI
4. Create an issue in the repository

---

**Happy coding! 🚀** The AI Engine will help keep your codebase healthy and optimized automatically.
