protobuf_sources(
  name="proto",
  sources=["schema/*.proto"],
  grpc=True,
)

python_sources(
  name="pb",
  sources=["pb/*.py"],
  dependencies=[":proto"],
)
