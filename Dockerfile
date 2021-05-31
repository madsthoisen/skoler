FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY . .
CMD ["gunicorn", "--workers=2", "--threads=1", "-b 0.0.0.0:8000", "app:server"]