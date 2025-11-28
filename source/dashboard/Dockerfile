FROM python:3.11

WORKDIR /app

RUN apt-get update && \
    apt-get -y install gcc mono-mcs && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

EXPOSE 8501

COPY pages ./pages
COPY .streamlit .streamlit/
COPY Homepage.py backend.py wishbone_logo.png ./

CMD ["streamlit", "run", "Homepage.py", "--server.port=8501", "--server.address=0.0.0.0"]