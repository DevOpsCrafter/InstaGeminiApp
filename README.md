# Astroboli - Automated AI Instagram Bot

## Overview
This repository contains two projects:
1.  **iOSGeminiApp**: A manual iOS app to generate and share images.
2.  **Astroboli Bot**: A fully automated Python bot that posts to Instagram daily.

## 🚀 Astroboli Bot Setup (Zero-Input Automation)

To get the daily bot running, you need to configure **GitHub Secrets**.

### Step 1: Get Your API Keys

#### 1. Gemini API Key (`GEMINI_API_KEY`)
*   **Primary Link**: [**Google AI Studio**](https://aistudio.google.com/)
    *   *Instructions*: Sign in, then look for **"Get API key"** in the top-left sidebar.

#### 2. Instagram/Meta Setup (Simplified Process)

**Step A: Create Your Meta App** (5 minutes)
1. Go to [**Meta Developers - My Apps**](https://developers.facebook.com/apps/)
2. Click **"Create App"** → Select **"Business"**
3. When asked, select your **existing Business Portfolio** (your Ads account)
4. Name it "Astroboli Bot" and click **Create App**

**Step B: Add Instagram Product**
1. In your app dashboard, click **"Add Product"**
2. Find **Instagram** and click **"Set Up"**
3. Also add **Instagram Graph API** if shown separately

**Step C: Get App Credentials**
1. Go to **Settings** → **Basic** (in the left sidebar)
2. Copy your **App ID** and **App Secret** (click "Show" to reveal it)
3. Save these - you'll need them for token generation

**Step D: Get Your Instagram User ID**
1. Go to [**Instagram Professional Dashboard**](https://www.instagram.com/accounts/login/?next=/accounts/manage_access/)
2. Find your Instagram User ID in your profile settings, or
3. Use this quick method: Visit [**Find My Instagram ID**](https://www.instagram.com/developer/) and follow the instructions

> **Note**: After creating the app, you'll use a helper script to generate your access token automatically.



### Step 2: Generate Access Token

After creating your Meta app, use the helper script to get your access token:

```powershell
python generate_token.py
```

The script will:
1. Ask for your App ID and App Secret
2. Generate an OAuth link for you to click
3. Guide you through getting a short-lived token
4. Help you exchange it for a long-lived token (valid 60 days)

Copy the final long-lived token - you'll add it to `secrets.env` in the next step.

### Step 3: Add Secrets to GitHub
1.  Go to this repository on GitHub.
2.  Click **Settings** > **Secrets and variables** > **Actions**.
3.  Click **New repository secret**.
4.  Add the following three secrets:
    -   `GEMINI_API_KEY`
    -   `IG_ACCESS_TOKEN`
    -   `IG_USER_ID`

### Step 3: Run the Bot
-   The bot is scheduled to run automatically every day at 10:00 UTC.
-   To test it immediately:
    1.  Go to the **Actions** tab.
    2.  Select **Daily Astroboli Post** on the left.
    3.  Click **Run workflow**.

---

## 📱 iOS App Setup (Manual)
1.  Open `iOSGeminiApp.xcodeproj` (or build `project.yml` with `xcodegen`).
2.  Run on iPhone.
3.  Tap "Generate & Post".
