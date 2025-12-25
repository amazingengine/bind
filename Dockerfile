# syntax=docker/dockerfile:1
FROM node:22-alpine

# Install useful tools
RUN apk add --no-cache bash git curl wget ripgrep less
# Install Gemini CLI (global)
RUN npm install -g @google/gemini-cli

# Default workdir that's bind-mounted by compose
WORKDIR /workspace

# Helpful default: print versions on container start if run without override
CMD ["/bin/bash", "-lc", "echo Node: $(node -v); echo NPM: $(npm -v); echo 'Run: gemini'; exec bash"]
