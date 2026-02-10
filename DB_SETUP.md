# Firebase Configuration Guide

This project supports both **Mock Mode** (for valid isolated testing) and **Real Firebase Mode** (for production/integration).

## How to Connect the Shared Database

To connect this Pharmacy Portal to the shared Firestore database used by the Doctor and Patient portals, follow these steps:

### Option 1: Using a Credentials File (Local Development)

1. Obtain the **Firebase Service Account Key** (usually `serviceAccountKey.json`) from the project administrator or Firebase Console.
2. Rename the file to `firebase-service-account.json` and place it in the `backend/` root directory. 
   *(Note: Do not use `pharmacy_credentials.json` - that file is for user login data).*
3. The application will automatically detect it and switch to **Real DB Mode**.

### Option 2: Using Environment Variables (Deployment - Render/Vercel)

Set the following environment variable in your deployment dashboard:

- **Key**: `FIREBASE_CREDENTIALS`
- **Value**: Paste the *entire content* of the Service Account JSON file as a string.

Alternatively, if you have the file hosted securely or prefer the standard Google path:
- **Key**: `GOOGLE_APPLICATION_CREDENTIALS`
- **Value**: `/path/to/your/credentials.json`

## Database Schema (Automatic)

When the application runs in Real DB Mode, it will automatically read/write to the following collections:

- `pharmacy_orders`
- `pharmacy_inventory`
- `pharmacies` (for profile info)
- `users` (for auth linking)

No manual SQL migration is needed as Firestore is NoSQL.

## Verifying Connection

When the backend starts, check the logs (terminal output). You should see:
> ✅ Firebase initialized successfully (REAL DB MODE)

If you see:
> ⚠️ No Firebase credentials found. Running in MOCK MODE.
Then check your file path or environment variables.
