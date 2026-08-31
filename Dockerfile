# Use a slim Python base image
FROM python:3-alpine

# Set the working directory in the container
WORKDIR /app

# Copy your code and requirements
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt \
    && adduser -D botuser \
    && chown -R botuser:botuser /app

# Run as a non-root user
USER botuser

# Run the bot
CMD ["python", "bot.py"]