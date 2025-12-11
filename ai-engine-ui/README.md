# AI Engine Microservice - Web UI

A modern Next.js web interface for the AI Engine Microservice that provides self-maintaining SaaS capabilities with automated code fixes.

## Features

- **Configuration Management**: Easy setup of GitHub token, repository, website URL, and API keys
- **Real-time Logs**: Live monitoring of system logs with filtering and export capabilities
- **Status Monitoring**: Comprehensive system health and status monitoring
- **Maintenance Control**: One-click maintenance cycle triggering
- **Safety Features**: Visual indicators for validation and rollback protection

## Quick Start

### 1. Install Dependencies
```bash
npm install
```

### 2. Start the Development Server
```bash
npm run dev
```

### 3. Start the AI Engine Backend
In another terminal, navigate to the main project directory:
```bash
cd ../src
python main_with_config.py
```

### 4. Access the Web Interface
Open [http://localhost:3000](http://localhost:3000) in your browser.

## Configuration

1. **Fill in the Configuration Form**:
   - Website URL: The website you want to monitor
   - GitHub Repository: Your repository (format: username/repo-name)
   - GitHub Token: Personal access token with repo permissions
   - Gemini API Key: Google Gemini API key for AI code generation
   - Google Analytics Property ID: For website analytics monitoring

2. **Test Connection**: Click "Test Connection" to verify the AI Engine is running

3. **Save Configuration**: Click "Save Config" to update the backend configuration

4. **Run Maintenance**: Click "Run Maintenance" to start the AI maintenance cycle

## Features Overview

### Configuration Panel
- Input validation for all required fields
- Real-time connection testing
- Secure token storage (tokens are not displayed in full)

### Status Monitor
- System health indicators
- Environment configuration status
- Recent activity tracking
- Safety feature status

### Logs Display
- Real-time log streaming
- Log level filtering (Info, Success, Warning, Error, Debug)
- Auto-scroll functionality
- Log export capabilities
- Log statistics

## API Endpoints

The UI communicates with the AI Engine backend through these endpoints:

- `GET /health` - System health check
- `GET /status` - Detailed system status
- `POST /configure` - Update configuration
- `POST /run` - Trigger maintenance cycle
- `GET /config` - Get current configuration

## Safety Features

- **Validation**: All generated code is validated before application
- **Rollback Protection**: Automatic rollback capabilities for problematic changes
- **Safe Mode**: Only processes issues marked as safe
- **Change Tracking**: Complete audit trail of all changes

## Development

### Project Structure
```
src/
├── app/
│   └── page.tsx          # Main page component
├── components/
│   ├── Header.tsx        # Header component
│   ├── ConfigurationForm.tsx  # Configuration form
│   ├── LogsDisplay.tsx   # Logs display component
│   └── StatusMonitor.tsx # Status monitoring component
└── ...
```

### Technologies Used
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first CSS framework
- **Lucide React**: Beautiful icons
- **Axios**: HTTP client for API calls

## Troubleshooting

### Common Issues

1. **Connection Failed**: Make sure the AI Engine backend is running on port 8000
2. **Configuration Not Saving**: Check that all required fields are filled
3. **Logs Not Updating**: Ensure the maintenance cycle is running
4. **CORS Errors**: The backend includes CORS middleware for localhost:3000

### Debug Mode
Enable debug logging by checking the browser console for detailed error messages.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of the AI Engine Microservice and follows the same license terms.
