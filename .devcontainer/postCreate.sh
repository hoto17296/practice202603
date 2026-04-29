#!/bin/bash -eu

[ ! -d "${UV_PROJECT}/.venv" ] && uv venv ${UV_PROJECT}/.venv

uv sync

bun install --cwd frontend