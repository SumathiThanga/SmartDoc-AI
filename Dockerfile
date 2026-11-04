
FROM python:3.11-slim

WORKDIR /app

# Install Python dependencies
COPY Requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r Requirements.txt

# Copy backend application files
COPY . .

# Create folders for uploaded documents and vector data
RUN mkdir -p Documents vector_store

EXPOSE 8000

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
