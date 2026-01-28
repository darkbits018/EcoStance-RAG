FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

# Build arguments for environment variables
ARG VITE_CRM_API_BASE_URL=http://localhost:9001/api/v1
ARG VITE_ENVIRONMENT=development

ENV VITE_CRM_API_BASE_URL=$VITE_CRM_API_BASE_URL
ENV VITE_ENVIRONMENT=$VITE_ENVIRONMENT

EXPOSE 9003

# Run in dev mode for easy local testing without Nginx
CMD ["npm", "run", "dev", "--", "--port", "9003", "--host", "0.0.0.0"]
