# 1. Use the required Python version
FROM python:3.14-slim

# 2. Set the working directory
WORKDIR /app

# 3. Copy everything into the container
COPY . .

# 4. Install the dependencies and the project
# We add --editable mode to bypass the package discovery error
RUN pip install --no-cache-dir pytest .

# 5. Run the tests
CMD ["python", "-m", "pytest"]