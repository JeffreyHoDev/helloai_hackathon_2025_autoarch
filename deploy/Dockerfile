FROM python:3.13-slim
WORKDIR /app

# Install the system-level dependencies
RUN apt-get update && \
    apt-get install -y libglib2.0-0 libpango-1.0-0 libpangoft2-1.0-0 graphviz && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN adduser --disabled-password --gecos "" myuser && \
    chown -R myuser:myuser /app

COPY . .

USER myuser

ENV PATH="/home/myuser/.local/bin:$PATH"

CMD ["uvicorn", "main:app", "--host","0.0.0.0" ,"--port", "8080"]