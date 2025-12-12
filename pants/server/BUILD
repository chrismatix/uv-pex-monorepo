python_sources(
  name="lib",
  sources=["server/**/*.py"],
  dependencies=[
    "lib/format:lib",
    "lib/proto:pb",
  ],
)

python_tests(
  name="tests",
  sources=["tests/**/*.py"],
  dependencies=[
    ":lib",
    "lib/format:lib",
    "lib/proto:pb",
    "3rdparty:reqs#httpx",
  ],
)

pex_binary(
  name="server_bin",
  script="uvicorn",
  args=[
    "server.app:app",
    "--host",
    "0.0.0.0",
    "--port",
    "8080",
    "--log-level",
    "warning",
    "--workers",
    "3",
  ],
  include_tools=True,
  layout="packed",
  output_path="server.pex",
  dependencies=[":lib", "3rdparty:reqs#uvicorn"],
)

docker_image(
    name="docker",
)
