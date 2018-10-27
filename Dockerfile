FROM bamos/openface

RUN pip install "tornado<5" "tqdm"

RUN curl -sL https://deb.nodesource.com/setup_8ee.x | sudo -E bash -

WORKDIR /app

ADD . .

CMD python app.py2npm