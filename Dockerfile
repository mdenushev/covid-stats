FROM python:3.7-stretch

WORKDIR /srv
ADD ./requirements.txt /srv/requirements.txt
RUN pip install -r requirements.txt
ADD . /srv

EXPOSE 3003
CMD ["python", "web.py"]