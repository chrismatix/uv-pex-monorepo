# Python mono-repo using UV, Pex, and Grog

![build](https://github.com/chrismatix/uv-pex-monorepo/actions/workflows/release.yaml/badge.svg)

This repository contains an example of a monorepo setup using uv and pex for building python executables.
The docker builds are handled with Earthly, but could be easily replaced with plain Dockerfiles.

## Motivation

UV supports the dev part of python mono-repositories through [workspaces](https://docs.astral.sh/uv/concepts/projects/workspaces/).However, when it comes to shipping our code we want to bundle our 
code in such a way that each docker image only contains the necessary dependencies.

While the [related uv proposal](https://github.com/astral-sh/uv/issues/5802) for `uv bundle` is still in the future this repository provides a recipe for how to bundle uv workspaces into executables that can be easily copied into docker images.

## How does it work?

Check out this blog post for a full walk-through: [Building the Fastest Python CI](https://chrismati.cz/posts/building-the-fastest-python-ci/) 

## The example repository

The repository consists of a library `lib/format` that is consumed by two different targets `server` and `cli` that each
bring their own additional dependencies. 

### Building

To produce the `pex` for either target you can run:

```shell
grog build //server:pex
```

This will create a `dist/bin.pex` file in the `server` package folder.
Now we can create the image by running `earthly +build` from that same directory.

### Testing

Each workspace maintains its own tests that can be run with `uv run pytest`. 
To run all tests, you can run `grog test` script.

## Comparison with other tools

I took this table [from](https://github.com/JasperHG90/uv-monorepo) here, but it perfectly echoes my sentiment.

While pants (or if you are very experienced Bazel) is the ultimate solution, it has a very steep learning curve
and is thus hard to adopt for small to medium-sized teams.

On the other end of the spectrum poetry provides a good development experience, but it relies on many non-standard
features and lacks good support for mono-repositories.
UV being the long awaited messiah of the python eco-system not only supports mono-repos via workspaces, but also
provides a global lock file and top performance.

|                  | Poetry              | UV/Pex/Grog  | Pants           |
|------------------|---------------------|--------------|-----------------|
| Simplicity       | 😃                  | 😃           | 😭              |
| Single lock file | 😭                  | 😍           | 🚀              |
| CI/CD            | 🤨                  | 🚀           | 🙂              |
| Docker builds    | 🤔                  | 😍           | 😭➡️🙂          |
| Speed            | 🤮                  | 🥰           | 😌              |
| Caching          | 🤷                  | 🥰           | 🥰              |
| Reproducability  | 🤷                  | 👍           | 🥰              |
| **Verdict**      | Woefully inadequate | Happy medium | Too complicated |

Overall, the recipe in this repository lacks many important aspects that are implemented by a "real" mono-repository
build tool such as Pants or Bazel. Instead, it provides a low-lift first step towards the right direction.

In fact, once you have this setup pants is not too far off since it also uses a global lock file and packages all python executables using pex.
