FROM python:3.11

RUN apt-get update && \
    apt-get -y install gcc mono-mcs && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

EXPOSE 8501

COPY app.py backend.py wishbone_logo.png pages ./

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]