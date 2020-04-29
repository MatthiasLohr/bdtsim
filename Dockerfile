
FROM python:3.8 AS builder
COPY ./dist/*.tar.gz /tmp/bdtsim.tar.gz
ENV PATH="/opt/bdtsim/bin:$PATH"
RUN python -m venv /opt/bdtsim \
    && pip install --no-cache-dir /tmp/bdtsim.tar.gz

FROM python:3.8-slim
ENV PATH="/opt/bdtsim/bin:$PATH"
COPY --from=builder /opt/bdtsim /opt/bdtsim
ENTRYPOINT ["/opt/bdtsim/bin/bdtsim"]
