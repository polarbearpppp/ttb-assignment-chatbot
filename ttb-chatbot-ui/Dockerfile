# Stage 1: Build
FROM node:20-slim AS build
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install ALL dependencies (including devDependencies like TypeScript/Vite)
RUN npm install

# Copy the source code
COPY . .

# RUN BUILD - We add an environment variable to ensure it knows it's production
RUN npm run build

# Stage 2: Serve
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]