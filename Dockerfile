# AI Employee Vault — Gold Cloud
# Hugging Face Spaces — Docker SDK
#
# HF Space configuration (paste into your Space's README.md frontmatter):
#
#   ---
#   title: AI Employee Vault Gold Cloud
#   emoji: 🤖
#   colorFrom: yellow
#   colorTo: gold
#   sdk: docker
#   app_port: 7860
#   pinned: false
#   ---
#
# Local build & run:
#   docker build -t vault-gold .
#   docker run -p 7860:7860 --env-file .env vault-gold

FROM python:3.11-slim

WORKDIR /app

# Install Python dependencies (cached layer — only rebuilds when requirements change)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create runtime vault directories
# (stateless on HF free tier — use Neon DB for persistent state)
RUN mkdir -p \
    Inbox \
    Needs_Action \
    Done \
    Personal \
    Business \
    Pending_Approval \
    Approved \
    Rejected \
    Failed_Tasks \
    Logs \
    Briefings \
    Plans

# HF Spaces requires port 7860
EXPOSE 7860

# Launch FastAPI via uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
