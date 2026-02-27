#!/usr/bin/env bash
set -euo pipefail

REPO="${GITHUB_REPO:-shemaobt/tripod-backend}"
GCP_PROJECT_ID="${GCP_PROJECT_ID:-$(gcloud config get-value project 2>/dev/null)}"
SECRETS_PROJECT_ID="${SECRETS_PROJECT_ID:-shemaobt-secrets}"
GCP_SA_KEY_SECRET_NAME="${GCP_SA_KEY_SECRET_NAME:-tripod_backend_github_actions_sa_key}"
GCP_SA_KEY_FILE="${GCP_SA_KEY_FILE:-}"
GCP_SA_EMAIL="${GCP_SA_EMAIL:-}"
KEY_FILE=""

cleanup() {
  [ -n "$KEY_FILE" ] && [ -f "$KEY_FILE" ] && rm -f "$KEY_FILE"
}
trap cleanup EXIT

if [ -z "$GCP_PROJECT_ID" ]; then
  echo "::error::GCP_PROJECT_ID is not set and could not get from gcloud config. Set GCP_PROJECT_ID or run gcloud config set project PROJECT_ID"
  exit 1
fi

SECRETS_PROJECT_NUMBER="$(gcloud projects describe "$SECRETS_PROJECT_ID" --format='value(projectNumber)' 2>/dev/null)" || true
if [ -z "$SECRETS_PROJECT_NUMBER" ]; then
  echo "::error::Could not get project number for $SECRETS_PROJECT_ID. Set SECRETS_PROJECT_ID or ensure the project exists and you have access."
  exit 1
fi

if [ -n "$GCP_SA_EMAIL" ] && [ -z "$GCP_SA_KEY_FILE" ] && ! gcloud secrets versions access latest --secret="$GCP_SA_KEY_SECRET_NAME" --project="$SECRETS_PROJECT_ID" &>/dev/null; then
  echo "Creating key for $GCP_SA_EMAIL and storing in Secret Manager..."
  KEY_FILE="$(mktemp)"
  gcloud iam service-accounts keys create "$KEY_FILE" --iam-account="$GCP_SA_EMAIL" --project="$GCP_PROJECT_ID"
  if gcloud secrets describe "$GCP_SA_KEY_SECRET_NAME" --project="$SECRETS_PROJECT_ID" &>/dev/null; then
    gcloud secrets versions add "$GCP_SA_KEY_SECRET_NAME" --data-file=- --project="$SECRETS_PROJECT_ID" < "$KEY_FILE"
  else
    gcloud secrets create "$GCP_SA_KEY_SECRET_NAME" --data-file=- --project="$SECRETS_PROJECT_ID" < "$KEY_FILE"
  fi
  echo "Key stored in $SECRETS_PROJECT_ID/$GCP_SA_KEY_SECRET_NAME"
fi

echo "Setting GitHub repository secrets for $REPO..."
echo "GCP_PROJECT_ID=$GCP_PROJECT_ID"
echo "SECRETS_PROJECT_NUMBER=$SECRETS_PROJECT_NUMBER"

gh secret set GCP_PROJECT_ID --repo "$REPO" --body "$GCP_PROJECT_ID"
gh secret set SECRETS_PROJECT_NUMBER --repo "$REPO" --body "$SECRETS_PROJECT_NUMBER"

if [ -n "$GCP_SA_KEY_FILE" ] && [ -f "$GCP_SA_KEY_FILE" ]; then
  echo "Using GCP_SA_KEY from file: $GCP_SA_KEY_FILE"
  gh secret set GCP_SA_KEY --repo "$REPO" < "$GCP_SA_KEY_FILE"
elif gcloud secrets versions access latest --secret="$GCP_SA_KEY_SECRET_NAME" --project="$SECRETS_PROJECT_ID" &>/dev/null; then
  echo "Downloading GCP_SA_KEY from Secret Manager: $GCP_SA_KEY_SECRET_NAME"
  gcloud secrets versions access latest --secret="$GCP_SA_KEY_SECRET_NAME" --project="$SECRETS_PROJECT_ID" | gh secret set GCP_SA_KEY --repo "$REPO"
else
  echo "::error::GCP_SA_KEY not found. Either: (1) Store the service account key JSON in GCP Secret Manager as $GCP_SA_KEY_SECRET_NAME in project $SECRETS_PROJECT_ID, or (2) Set GCP_SA_KEY_FILE to the path of the key JSON file, or (3) Set GCP_SA_EMAIL to create a key and store it (e.g. tripod-backend-github-deployer@PROJECT.iam.gserviceaccount.com)."
  exit 1
fi

echo "Secrets set. Triggering deploy workflow..."
gh workflow run "Deploy tripod-backend to Cloud Run" --repo "$REPO" --ref main
