FROM oven/bun:1

WORKDIR /workspace

# Common Packages
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    bash-completion ca-certificates curl dnsutils git gnupg2 htop iputils-ping jq less lsb-release lsof net-tools openssh-client procps \
  && rm -rf /var/lib/apt/lists/*

# Nginx
RUN apt-get update \
  && apt-get install -y --no-install-recommends nginx \
  && rm -rf /var/lib/apt/lists/*
COPY nginx.conf /etc/nginx/sites-available/default

# Python
COPY --from=ghcr.io/astral-sh/uv /uv /usr/local/bin/uv
RUN uv python install 3.14
ENV PATH=/workspace/.venv/bin:${PATH}
ENV PYTHONPATH=/workspace/backend