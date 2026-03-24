# Web UI Dashboard

The AI Engine provides a modern Next.js interface for monitoring and control, giving you a real-time window into the system's operations.

## Features

### 1. Real-time Logs

- **Streaming**: Uses WebSockets backed by Redis Pub/Sub to stream logs instantly.
- **Visuals**: Color-coded log levels (INFO, WARNING, ERROR) for easy scanning.
- **Control**: Auto-scroll toggle to pause/resume the stream.

### 2. System Status

- **Health Indicators**: Visual checks for API, Redis, and Database connectivity.
- **Environment**: Displays current environment (Dev/Prod) and configuration mode.

### 3. Bug Visualization

- **List View**: See all detected bugs in a structured list.
- **Priority**: Bugs are tagged with severity (Critical, High, Medium, Low).
- **Details**: Expand to see the specific file, line number, and error message.

### 4. Feature Recommendations

- **Interactive Reports**: View results from the Competitive Analysis.
- **Natural Language**: Read AI-generated summaries of why a feature matters.
- **Action**: Select features to generate an implementation plan.

## Components

The dashboard is built with **Next.js 14**, **shadcn/ui**, and **TailwindCSS**.

- `LogsDisplay`: Handles the WebSocket connection.
- `StatusMonitor`: Polls the `/status` endpoint for health checks.
- `IdentifiedBugs`: Renders the bug queue state.
