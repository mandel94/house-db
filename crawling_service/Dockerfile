FROM python:3.12 AS base

# Set the working directory

WORKDIR /app

# Copy the requirements file

COPY requirements.txt .

# Install the dependencies

RUN pip install --no-cache-dir -r requirements.txt


# Copy the source code

COPY . /app

# Set the entrypoint

ENTRYPOINT ["python", "main.py"]
