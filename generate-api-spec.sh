#!/bin/bash -eu

CWD=$(cd $(dirname $0);pwd)

cd ${CWD}/backend
spec=$(
  JWT_PRIVATE_KEY=dummy PASSWORD_PEPPER=dummy \
  python -c "import json; from app import app; print(json.dumps(app.openapi()))"
)

cd ${CWD}/frontend
echo ${spec} | bunx openapi-typescript -o src/api-spec.d.ts