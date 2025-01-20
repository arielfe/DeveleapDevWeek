# Base image for Node.js
FROM node:18 AS build

# Set working directory
WORKDIR /frontend

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install --frozen-lockfile --no-audit

# Copy the rest of the application code
COPY . .

# Build the app with the VITE_API_URL argument
ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL}
RUN npm run build

# Final production image
FROM node:18 AS production

# Set working directory
WORKDIR /frontend

# Copy the built app from the build stage
COPY --from=build /frontend/dist ./dist

# Install serve to serve the built app
RUN npm install -g serve

# Expose the port
EXPOSE 3000

# Default command to serve the app
CMD ["serve", "-s", "dist"]
