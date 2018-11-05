FROM bamos/openface

WORKDIR /app

RUN pip install "tornado<5" "tqdm"

RUN curl -sL https://deb.nodesource.com/setup_8.x | bash -

RUN apt-get install -y nodejs

ADD . .

RUN cd static_app && npm i && npm run build

CMD python app.py2npm