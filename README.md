# 🤖 AI-Powered Website Maintenance Microservice

## 🚀 Overview
An autonomous system that acts as a permanent AI developer for your codebase. It continuously detects, analyzes, and fixes website issues using AI — significantly reducing manual debugging and maintenance effort. By integrating directly with your repository and analytics, it automatically handles security patches, performance problems, and feature updates.

## 🔥 Key Highlights
- ✅ **85%+ automated issue resolution** (validated fixes that pass all tests)
- ⚡ **~2-minute autonomous fix cycles** (from detection to PR creation)
- 🧠 **AI-driven decision making using Gemini** (1.5 Pro and Flash models)
- 🔌 **35+ FastAPI endpoints** (handling everything from GitHub integrations to WebSockets)
- 🏗 **~28K lines of production backend code**

## 🧠 What Makes It Interesting
Unlike traditional monitoring tools, this system doesn’t just detect issues — it attempts to **fix them automatically** and validates the results through a multi-stage pipeline. Every AI-generated fix is sandboxed, statically validated (catching undefined runtime errors via regex heuristics), tested in a headless browser, and protected by an automatic rollback manager if degradation occurs.

## 🛠 Tech Stack
- **Backend:** Python, FastAPI
- **Async Processing:** Celery, Redis (for background task queuing and state)
- **Frontend:** Next.js (React), Tailwind CSS, shadcn/ui
- **Database:** PostgreSQL (for persisting issue states and rollback histories)
- **AI Integration:** Google Gemini API (Code generation, planning, and vision for UI analysis)
- **Testing/Analysis:** Playwright, Lighthouse, Axe-core, AST Code Analyzers

## ⚙️ System Architecture
- Asynchronous task queues using Celery (3 workers)
- Multi-stage validation pipeline for AI outputs (Security → Syntax → Build → Execution)
- Modular microservice design for scalability
- Automated PR integration with GitHub and safety rollbacks

```mermaid
graph TD
    A[Next.js Dashboard] -->|REST / WebSockets| B(FastAPI Server)
    B --> C{Celery Task Queue}
    C -->|State/Messaging| D[(Redis)]
    
    C --> E[Worker 1: Bug Detection]
    E -->|Lighthouse / Axe / Playwright| H[Target Website]
    
    C --> F[Worker 2: AI Generation]
    F -->|Prompt Engineering| I[Google Gemini API]
    
    C --> G[Worker 3: Validation & CI/CD]
    F --> G
    G -->|AST Check / Build Test| J[Build Validator]
    J -->|Submit PR| K[GitHub Repository]
    K --> L[Rollback Manager]
    L -.->|Monitors Metrics| H
```

## 🖥 Demo
<img width="1366" height="768" alt="Screenshot from 2026-03-25 00-06-38" src="https://github.com/user-attachments/assets/b4f617b4-401e-4c7c-8846-4ec4d1e69573" />
<img width="1366" height="768" alt="Screenshot from 2026-03-25 00-06-45" src="https://github.com/user-attachments/assets/b6d78386-5511-468e-b09c-b55ba3258170" />
<img width="1366" height="768" alt="Screenshot from 2026-03-25 00-06-52" src="https://github.com/user-attachments/assets/f768115f-6463-47b3-9c85-dc3aff2a91ac" />
<img width="1366" height="768" alt="Screenshot from 2026-03-25 00-07-04" src="https://github.com/user-attachments/assets/e1d0c418-6ec7-45c5-994e-ae75799878c5" />
<img width="1366" height="768" alt="Screenshot from 2026-03-25 00-07-10" src="https://github.com/user-attachments/assets/2de0f09e-ba5b-43de-b104-8f36a25b6821" />
<img width="1366" height="768" alt="Screenshot from 2026-03-25 00-07-27" src="https://github.com/user-attachments/assets/013a66da-f63a-47c7-9884-2a4909758a4d" />
<img width="1366" height="768" alt="Screenshot from 2026-03-25 00-10-03" src="https://github.com/user-attachments/assets/2513475c-1c90-46a2-a0dd-371899a8f8ea" />
<img width="1366" height="768" alt="Screenshot from 2026-03-25 00-13-08" src="https://github.com/user-attachments/assets/c98ce6e0-bdaa-4b57-9de5-0973ce129e95" />
<img width="1366" height="768" alt="Screenshot from 2026-03-25 00-13-14" src="https://github.com/user-attachments/assets/735520b6-33c2-48d6-b398-289fdd0afc3a" />
<img width="1366" height="768" alt="Screenshot from 2026-03-25 00-13-20" src="https://github.com/user-attachments/assets/5e3b72d1-0f2c-4e9b-852d-44922ad0eaa2" />
<img width="1366" height="768" alt="image" src="https://github.com/user-attachments/assets/4b10c310-3131-4eb2-8cee-69aaa20aa313" />


## 💡 Key Features
- **Automated issue detection and fixing:** Continuously monitors for broken links, UI/UX bugs, and console errors, automatically generating and testing code fixes.
- **Security and performance analysis (6 vulnerability categories):** Scans the repository for hardcoded credentials, SQL injections, large bundle sizes, and memory leaks.
- **10+ Lighthouse/Web Vitals checks:** Evaluates LCP, FID, CLS, and ensures mobile responsiveness, accessibility, and SEO compliance.
- **Real-time monitoring dashboard:** Next.js interface featuring WebSocket-based live log streaming, bug queue status, and auto-approval configurations.

## 🎯 Why I Built This
To explore autonomous systems that reduce repetitive debugging and leverage AI for real-world problem solving. The goal was to eliminate the never-ending "developer bill" for standard website maintenance by creating an intelligent agent capable of maintaining code quality 24/7.

## 📌 Future Improvements
- Support for more LLM providers (OpenAI, Anthropic, local models)
- Advanced self-healing workflows (dynamic A/B testing of multiple fixes)
- Scalable distributed worker architecture for multi-site deployments
