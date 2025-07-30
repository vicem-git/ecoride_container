FROM fedora:latest

RUN dnf install -y libpq libpq-devel

RUN dnf install -y glibc-langpack-fr \
 && localedef -i fr_FR -f UTF-8 fr_FR.UTF-8

ENV LANG=fr_FR.UTF-8
ENV LC_ALL=fr_FR.UTF-8

RUN dnf install -y python3 python3-pip python3-devel gcc openssl-devel npm

WORKDIR /ecoride_container

# python venv
COPY ./ecoride_flask/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ./ecoride_flask ./ecoride_flask

WORKDIR /ecoride_container/ecoride_flask
RUN npm install

# ports
EXPOSE 5000 5173

# run :)
CMD ["bash"]
