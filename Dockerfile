# Test Dockerfile — builds in ~60 seconds
# Serves a static HTML file via Python's http.server on port 8080

FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# Layer 1: apt update + install packages (~20-30s)
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    python3 \
    python3-pip \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Layer 2: compile a small C program to burn a few seconds (~10s)
RUN echo '#include <stdio.h>\nint main(){printf("ok\n");}' > /tmp/test.c \
    && gcc -O0 /tmp/test.c -o /usr/local/bin/testbin \
    && rm /tmp/test.c

# Layer 3: install a couple of Python packages (~15-20s)
RUN pip3 install --no-cache-dir --break-system-packages \
    requests \
    httpx

# Layer 4: generate some dummy files (~5s)
RUN mkdir -p /app && \
    for i in $(seq 1 500); do \
        echo "file $i: $(date)" > /app/file_$i.txt; \
    done

# Copy in the HTML file
WORKDIR /app
COPY index.html ./

EXPOSE 8080

CMD ["python3", "-m", "http.server", "8080", "--directory", "/app"]