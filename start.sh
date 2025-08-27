#!/bin/bash

echo "🚀 Starting JobPost Helper MVP..."

# Install dependencies if needed
echo "📦 Installing dependencies..."
pip3 install --break-system-packages -r requirements.txt

# Start the backend
echo "🔧 Starting backend server..."
python3 main.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Check if backend is running
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is running on http://localhost:8000"
else
    echo "❌ Backend failed to start"
    exit 1
fi

echo ""
echo "🎉 JobPost Helper MVP is ready!"
echo "📱 Open index.html in your browser"
echo "🔧 Backend API: http://localhost:8000"
echo "📊 Health Check: http://localhost:8000/health"
echo "📁 Output files will be saved in the 'output' directory"
echo ""
echo "Press Ctrl+C to stop the application"

# Wait for user to stop
wait
