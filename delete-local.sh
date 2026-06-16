#!/usr/bin/env bash
set -euo pipefail

kubectl delete namespace rescuehub --ignore-not-found=true
