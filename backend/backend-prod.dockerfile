# Dockerfile for production
FROM chrisdare/serenity-data-bridge-backend:latest

WORKDIR /app/

COPY ./ /app
# update the start and reload script
# RUN rm /start-reload.sh
COPY ./scripts/start-reload.sh /start-reload.sh
RUN chmod +x /start-reload.sh
ENV PYTHONPATH=/app/app/
