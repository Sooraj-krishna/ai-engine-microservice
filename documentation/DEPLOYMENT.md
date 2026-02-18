# Deploying to Render

The AI Engine Microservice is configured for seamless deployment on [Render](https://render.com) using Infrastructure as Code (IaC) via the `render.yaml` file.

## 📋 Prerequisites

1.  A [Render](https://render.com) account.
2.  This repository pushed to your GitHub account.
3.  A **Google Gemini API Key**.
4.  A **GitHub Personal Access Token** (for the AI to create PRs).

## 🚀 Deployment Steps

### 1. Connect to Render

1.  Go to the [Render Dashboard](https://dashboard.render.com/).
2.  Click **New +** and select **Blueprint**.
3.  Connect your GitHub repository.
4.  Give Render permission to access the repo.

### 2. Configure the Blueprint

Render will automatically detect the `render.yaml` file and propose the following services:

- **ai-engine-microservice**: The main web service (FastAPI + Next.js).
- **ai-engine-redis**: A Redis instance for background tasks and caching.

### 3. Set Environment Variables

The `render.yaml` file defines placeholders for sensitive keys. You will be prompted to enter values for these during the setup:

| Variable          | Description                                             |
| :---------------- | :------------------------------------------------------ |
| `GEMINI_API_KEY`  | Your Google Gemini API key.                             |
| `GITHUB_TOKEN`    | Personal Access Token (PAT) with `repo` scope.          |
| `GITHUB_REPO`     | Your repository name (e.g., `yourname/ai-engine`).      |
| `WEBSITE_URL`     | The URL of the site you want to monitor.                |
| `MONITORING_MODE` | Set to `simple` or `comprehensive` (default: `simple`). |
| `ENVIRONMENT`     | Set to `production`.                                    |

### 4. Deploy

Click **Apply** or **Create Resources**. Render will:

1.  Provision the Redis instance.
2.  Build the Docker image (installing Python/Node.js dependencies).
3.  Deploy the service.

The deployment typically takes 3-5 minutes.

## 🛠️ Configuration Details

### `render.yaml`

defines the infrastructure.

- **Runtime**: Docker
- **Region**: Defaults to Oregon (us-west-2), configurable.
- **Plan**: Free tier (configurable in YAML).

### `Dockerfile`

The project uses a multi-stage `Dockerfile`:

1.  **Stage 1 (Frontend)**: Builds the Next.js UI static export.
2.  **Stage 2 (Backend)**: Installs Python dependencies, Playwright browsers, and serving the static UI files via FastAPI.

## 🔍 Troubleshooting

### Build Failures

- **Timeout**: If the build takes too long, ensure you are not installing unnecessary heavy dependencies.
- **Playwright**: The Dockerfile includes `playwright install --with-deps chromium`. If browser checks fail, check the build logs to ensure this step succeeded.

### Runtime Errors

- **Missing Variables**: Check the **Environment** tab in the Render dashboard to ensure all keys are set.
- **Redis Connection**: The app expects `REDIS_URL`. Render automatically injects this environment variable when you link the Redis service in the blueprint.

## 🔄 Updates

Because this is a **Blueprint** deployment:

- Pushing to your GitHub `main` branch will automatically trigger a new deployment.
- Changes to `render.yaml` will prompt you to approve infrastructure changes in the Render dashboard.
