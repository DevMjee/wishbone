FROM python:3.13-slim

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY dashboard.py .

CMD [ "streamlit", "run", "dashboard.py" ]