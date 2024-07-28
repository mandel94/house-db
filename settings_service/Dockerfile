FROM python:3.12-slim as base

# Install dependencies

WORKDIR /app

COPY requirements.txt .


RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code

COPY /server .

# Run the application

CMD ["python", "main.py"]

