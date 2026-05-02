# Deployment Guide

See `README.md` for the full deployment guide.

## Google Cloud Run (Backend API)

### Quick Deploy (Source-based)
```bash
gcloud run deploy civicpath --source . --region us-central1 --allow-unauthenticated
```

### CI/CD Deploy (Cloud Build)
```bash
gcloud builds submit --config cloudbuild.yaml
```

`cloudbuild.yaml` handles:
1. Building the Docker image
2. Pushing to Artifact Registry
3. Deploying to Cloud Run

### Environment Variables
Configure via Cloud Run Console or CLI:
```bash
gcloud run services update civicpath \
  --set-env-vars "GEMINI_API_KEY=...,FIREBASE_PROJECT_ID=..."
```

## Firebase (Firestore Database)

### Setup
1. Create a Firebase project at https://console.firebase.google.com
2. Enable Firestore in the Firebase console
3. Download the service account JSON from Project Settings > Service Accounts
4. Set `FIREBASE_CREDENTIALS_PATH` to the JSON file path (local) or use Application Default Credentials on Cloud Run

### Firestore Security Rules
Deploy rules:
```bash
firebase deploy --only firestore:rules
```

### On Cloud Run
Cloud Run automatically picks up Firebase credentials via the GCP service account attached to the Cloud Run service — no `FIREBASE_CREDENTIALS_PATH` needed if both are in the same project.
