FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

COPY sentences_to_notes.py .
COPY requirements.txt .

RUN pip install -r requirements.txt

ENV FLASK_APP=sentences_to_notes.py

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
