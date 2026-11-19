FROM python:3.11-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN groupadd -g 10001 lab && useradd --no-create-home -u 10001 -g 10001 lab
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py internal_service.py public_service.py test_lab.py ./
USER 10001:10001
CMD ["python", "app.py"]
