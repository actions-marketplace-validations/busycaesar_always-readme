FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

COPY req.txt req.txt
RUN pip install --no-cache-dir -r req.txt

COPY src/ src/

ENTRYPOINT [ "python", "/src/update_readme.py" ]