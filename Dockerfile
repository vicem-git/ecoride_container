FROM fedora:latest


RUN dnf install -y python3 python3-pip python3-devel gcc openssl-devel npm

WORKDIR /ecoride_container
COPY . .

# python venv
RUN python3 -m venv venv
ENV PATH="/ecoride_container/venv/bin:$PATH"
COPY ./ecoride_flask/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /ecoride_container/ecoride_flask
RUN npm install

# ports
EXPOSE 5000 5173

# run :)
CMD ["bash"]
