#!/bin/bash
set -e

NAMESPACE="cep"

echo "Running kubeops health..."
poetry run kubeops health -n $NAMESPACE

echo "Running kubeops audit..."
poetry run kubeops audit -n $NAMESPACE

echo "Testing deployment failure and automatic rollback..."
# Intentionally cause a failure by setting a bad image
kubectl set image deployment/cep-order-service order=cloud-event-platform-order-service:bad-tag -n $NAMESPACE || true

echo "Running kubeops deploy to verify and trigger rollback..."
poetry run kubeops deploy -n $NAMESPACE -d cep-order-service --auto-rollback --timeout 30 || true

echo "Verifying successful recovery..."
poetry run kubeops health -n $NAMESPACE
