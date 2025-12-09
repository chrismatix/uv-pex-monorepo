python_sources(
  name="lib",
  sources=["cli/**/*.py"],
  dependencies=["lib/format:lib"],
)

pex_binary(
  name="cli_bin",
  entry_point="main:app",
  include_tools=True,
  layout="packed",
  output_path="cli.pex",
  dependencies=[":lib"],
)

docker_image(
    name="docker",
)
