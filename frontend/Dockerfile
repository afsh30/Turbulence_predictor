FROM node:18-alpine

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

# Expose Vite's default port
EXPOSE 5173

# Run Vite development server, bounded to 0.0.0.0 to be accessible outside the container
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
