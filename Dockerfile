FROM debian:stretch

ENV DEBIAN_FRONTEND noninteractive

### RUN set -ex; \

RUN apt-get update -qq; \
    apt-get install -y -qq git \
    apt-utils \
    wget \
    python3-pip \
    ncbi-blast+ \
    libz-dev \
    ; \
    rm -rf /var/cache/apt/* /var/lib/apt/lists/*;

ENV DEBIAN_FRONTEND Teletype

# Install python dependencies
RUN pip3 install -U biopython==1.73 tabulate cgecore==1.4.2;

# Install kma
RUN git clone --branch 1.0.1 --depth 1 https://bitbucket.org/genomicepidemiology/kma.git; \
    cd kma && make; \
    mv kma* /bin/

COPY virulencefinder.py /usr/src/virulencefinder.py

# TEST setup
RUN mkdir /database /test
COPY test/database/ /database/
COPY test/test* test/
COPY virulencefinder.py /usr/src/virulencefinder.py

RUN chmod 755 /usr/src/virulencefinder.py; \
    chmod 755 test/test.sh

ENV PATH $PATH:/usr/src
# Setup .bashrc file for convenience during debugging
RUN echo "alias ls='ls -h --color=tty'\n"\
"alias ll='ls -lrt'\n"\
"alias l='less'\n"\
"alias du='du -hP --max-depth=1'\n"\
"alias cwd='readlink -f .'\n"\
"PATH=$PATH\n">> ~/.bashrc

WORKDIR /workdir

# Execute program when running the container
ENTRYPOINT ["/usr/src/virulencefinder.py"]
