FROM python:3.12-slim

COPY ./test.pex /test.pex

RUN PEX_TOOLS=1 /usr/local/bin/python3.12 /test.pex venv --compile /app

ENTRYPOINT ["/app/pex"]
