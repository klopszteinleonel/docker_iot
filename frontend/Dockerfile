FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV FLASK_APP=app.py
# Set unbuffered output to see Python logs immediately
ENV PYTHONUNBUFFERED=1 
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
