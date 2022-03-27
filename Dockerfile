FROM python:3.10
EXPOSE 8501
COPY requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt
WORKDIR app
COPY . .
CMD streamlit run app.py
