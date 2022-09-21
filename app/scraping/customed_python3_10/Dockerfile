FROM python:3.10

# to process fast
ENV TERM xterm

# install python external modules
COPY requirements.txt /usr/src
WORKDIR /usr/src
RUN pip install --upgrade pip \
    && pip install --upgrade setuptools \
    && pip install -r requirements.txt 
