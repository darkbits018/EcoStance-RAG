FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

# Build arguments for environment variables
ARG VITE_API_BASE_URL=http://localhost:8000/api/v1
ARG VITE_ENVIRONMENT=development
ARG VITE_BYPASS_AUTH=false

ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_ENVIRONMENT=$VITE_ENVIRONMENT
ENV VITE_BYPASS_AUTH=$VITE_BYPASS_AUTH

EXPOSE 9002

# Run in dev mode for easy local testing without Nginx
CMD ["npm", "run", "dev", "--", "--port", "9002", "--host", "0.0.0.0"]
