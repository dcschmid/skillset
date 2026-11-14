FROM node:latest
# FLAW fixture: floating tag, root user, baked secret, no healthcheck
ENV APP_DB_PASSWORD=test-onl*****-password
COPY . /app
WORKDIR /app
RUN npm install
EXPOSE 3000
CMD ["node", "server.js"]
