# Use a slim Python base image
FROM python:3-alpine

# Set the working directory in the container
WORKDIR /app

# Copy your code and requirements
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the bot
CMD ["python", "bot.py"]