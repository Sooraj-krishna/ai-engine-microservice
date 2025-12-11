#!/bin/bash

echo "🚀 Starting AI Engine Microservice with Web UI"
echo "=============================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python 3.10+ first."
    exit 1
fi

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if npm is available
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Install UI dependencies if needed
if [ ! -d "ai-engine-ui/node_modules" ]; then
    echo "📦 Installing UI dependencies..."
    cd ai-engine-ui
    npm install
    cd ..
fi

echo "🔧 Starting AI Engine Backend..."
cd src
python3 main_with_config.py &
BACKEND_PID=$!
cd ..

echo "⏳ Waiting for backend to start..."
sleep 5

echo "🌐 Starting Web UI..."
cd ai-engine-ui
npm run dev &
UI_PID=$!
cd ..

echo ""
echo "🎉 AI Engine Microservice is now running!"
echo ""
echo "📊 Web UI: http://localhost:3000"
echo "🔧 API Backend: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both services"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $BACKEND_PID 2>/dev/null
    kill $UI_PID 2>/dev/null
    echo "✅ Services stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for both processes
wait
