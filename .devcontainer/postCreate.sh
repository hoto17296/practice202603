#!/bin/bash -eu

WORKSPACE_DIR=$(cd $(dirname $0)/..; pwd)

[ ! -d "${WORKSPACE_DIR}/.venv" ] && uv venv ${WORKSPACE_DIR}/.venv

uv sync