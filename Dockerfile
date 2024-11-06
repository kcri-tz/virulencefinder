FROM python:3.10-slim-bullseye

ENV INSIDE_DOCKER true
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update -qq; \
    apt-get install --no-install-recommends -y -qq git \
    build-essential \
    wget \
    ncbi-blast+ \
    libz-dev \
    procps \
    ; \
    rm -rf /var/cache/apt/* /var/lib/apt/lists/*;

# Install KMA
RUN cd /usr/src/; \
    git clone --depth 1 -b 1.4.11 https://bitbucket.org/genomicepidemiology/kma.git; \
    cd kma && make; \
    mv kma /usr/bin/; \
    cd ..; \
    rm -rf kma/;

ENV VIRULENCEFINDER_VERSION 3.0.2

# Install VirulenceFinder
RUN pip install --no-cache-dir virulencefinder==$VIRULENCEFINDER_VERSION

# Install database
RUN cd /; \
    mkdir databases; \
    cd /databases/; \
    git clone -b virulencefinder-$VIRULENCEFINDER_VERSION --depth 1 https://git@bitbucket.org/genomicepidemiology/virulencefinder_db.git; \
    cd /databases/virulencefinder_db; \
    python INSTALL.py; \
    rm -rf .git;

# Setup environment
RUN cd /; \
    mkdir app;
WORKDIR /app

# Environmental variables
ENV CGE_VIRULENCEFINDER_DB /databases/virulencefinder_db/

# Execute program when running the container
ENTRYPOINT ["python", "-m", "virulencefinder"]