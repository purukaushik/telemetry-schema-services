# use base python
FROM python:2.7

# create app directory
RUN mkdir -p /app/
WORKDIR /app/

# install requirements
COPY requirements.txt /app/
RUN pip install --no-cache-dir --requirement requirements.txt

# expose 8080 for flask app
EXPOSE 8080

# copy application
COPY . /app/

# run start script
CMD ["bin/start"]
