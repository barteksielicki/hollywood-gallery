FROM bamos/openface

RUN pip install "tornado<5" "tqdm"

WORKDIR /app

ADD . .