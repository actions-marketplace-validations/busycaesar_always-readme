FROM python:3.11-slim

COPY req.txt req.txt
RUN pip install --no-cache-dir -r req.txt

COPY src/ src/

ENTRYPOINT [ "python", "/src/update_readme.py" ]