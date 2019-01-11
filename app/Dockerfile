FROM bamos/openface

WORKDIR /app

RUN pip install "pandas" "tornado<5" "tqdm"

RUN curl -sL https://deb.nodesource.com/setup_8.x | bash -

RUN apt-get install -y nodejs

ADD . .

RUN cd ui && npm i && npm run build

CMD cd server && python app.py