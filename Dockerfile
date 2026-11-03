FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=10000

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY models/ ./models/
COPY data/products.csv ./data/products.csv

EXPOSE 10000

CMD ["sh", "-c", "exec streamlit run app/streamlit_app.py --server.address=0.0.0.0 --server.port=${PORT:-10000} --server.headless=true --server.enableCORS=false --server.enableXsrfProtection=true"]
