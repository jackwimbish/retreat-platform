FROM node:18-slim

# Install required build dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    make \
    g++ \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Enable Corepack for Yarn 3 support
RUN corepack enable

# Copy package files
COPY package.json yarn.lock ./

# Copy yarn configuration if it exists, or create a basic one
COPY .yarnrc.yml* ./
RUN if [ ! -f .yarnrc.yml ]; then \
    echo "nodeLinker: node-modules" > .yarnrc.yml; \
    fi

# Copy .yarn directory if it exists, or initialize Yarn 3
COPY .yarn* ./.yarn/
RUN if [ ! -d .yarn ]; then \
    yarn set version 3.2.3; \
    fi

# Install dependencies without running postinstall
RUN yarn install --mode=skip-build

# Copy patches and Makefile needed for postinstall
COPY patches ./patches
COPY Makefile ./

# Copy all remaining frontend files
COPY . .

# Run postinstall/patches manually with error handling
RUN yarn run postinstall || \
    (echo "Postinstall failed, trying patches directly..." && \
     yarn run patches || \
     echo "Patches failed, continuing anyway...")

# Expose the development server port
EXPOSE 3000

# Don't pre-build, let the start script handle it
CMD ["sh", "-c", "NODE_ENV=production yarn build && NODE_ENV=production node build/server.js"]