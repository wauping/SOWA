FROM python:3.11.5

WORKDIR /backend

COPY requirements.txt /backend
RUN pip3 install --upgrade pip -r requirements.txt

COPY . /backend

EXPOSE 5000