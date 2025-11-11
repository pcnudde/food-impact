FROM python:3.11-slim

WORKDIR /app
RUN apt-get update && apt-get install -y zip && rm -rf /var/lib/apt/lists/*


COPY requirements.txt .
COPY processing/ .
RUN mkdir output

RUN pip install --no-cache-dir -r requirements.txt

RUN chmod +x process.sh
# Fix potential Windows line endings
RUN sed -i 's/\r$//' process.sh

# Use shell form instead of exec form for ENTRYPOINT
ENTRYPOINT ["sh", "process.sh"]

# docker build -t food-impact .
#  docker run -v $(pwd):/app/host -e OPENAI_API_KEY=$OPENAI_API_KEY -it food-impact
