# Use the official lightweight Python image.
FROM python:3.9-slim

# Install any system dependencies if needed. For example, gcc for compiling some packages.
RUN apt-get update && apt-get install -y gcc

# Set the working directory.
WORKDIR /app

# Copy requirements.txt into the container.
COPY requirements.txt .

# Install Python dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# You can set a default command. Since you'll override this when running user code,
# it's fine to leave it as python.
CMD ["python"]
