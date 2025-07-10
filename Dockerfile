# 1. Use an official Python runtime as a parent image
FROM python:3.11-slim

# 2. Set the working directory in the container
WORKDIR /app

# 3. Install Poetry
RUN pip install "poetry>=1.2.0"

# 4. Copy only the dependency definition files
COPY pyproject.toml poetry.lock* ./

# 5. Install project dependencies
RUN poetry config virtualenvs.create false && \
    poetry install --no-root --only main

# 6. Copy the rest of the application's code
COPY ./backend /app

# 7. Expose the port the app runs on
EXPOSE 8000 