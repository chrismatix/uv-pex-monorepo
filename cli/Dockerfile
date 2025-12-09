FROM python:3.12-slim as builder

# Copy the pex file and create the virtual environment
COPY ./dist/bin.pex /bin.pex
RUN PEX_TOOLS=1 /usr/local/bin/python3.12 /bin.pex venv --collisions-ok --compile /app

# Final image
FROM python:3.12-slim

# Copy the app from the builder stage
COPY --from=builder /app /app

ENTRYPOINT ["/app/pex"]1
