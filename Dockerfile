FROM python:3.11-slim

WORKDIR /app
COPY process_csv.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "process_csv.py"]