FROM python:3.9-slim

WORKDIR /app
# Install Python dependencies.
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copy the rest of the codebase into the image
COPY . .

CMD ["gunicorn", "--workers=2", "--threads=1", "-b 0.0.0.0:8000", "app:server"]