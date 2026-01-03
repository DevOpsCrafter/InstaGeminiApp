# Astroboli - Automated AI Instagram Bot

## Overview
This repository contains two projects:
1.  **iOSGeminiApp**: A manual iOS app to generate and share images.
2.  **Astroboli Bot**: A fully automated Python bot that posts to Instagram daily.

## 🚀 Astroboli Bot Setup (Zero-Input Automation)

To get the daily bot running, you need to configure **GitHub Secrets**.

### Step 1: Get Your API Keys (Direct Links)

#### 1. Gemini API Key (`GEMINI_API_KEY`)
*   **Link**: [**Google AI Studio - Get API Key**](https://aistudio.google.com/app/apikey)
*   **Action**: Click "Create API Key" and copy the string.

#### 2. Instagram/Meta Setup (`IG_ACCESS_TOKEN` & `IG_USER_ID`)
*   **Link 1 - Create App**: [**Meta Developers - My Apps**](https://developers.facebook.com/apps/)
    *   Click "Create App" > **Business** > name it "Astroboli".
    *   Add Product > **Instagram Graph API** > "Set Up".
*   **Link 2 - Get Token & ID**: [**Graph API Explorer**](https://developers.facebook.com/tools/explorer/)
    *   **Meta App**: Select "Astroboli".
    *   **User or Page**: Select "Get User Access Token".
    *   **Permissions**: Add `instagram_basic` and `instagram_content_publish`.
    *   **Generate Access Token**: Click "Generate Access Token". Use this as your `IG_ACCESS_TOKEN` (Note: This is short-lived; for a permanent bot, you enter this token into the [Access Token Debugger](https://developers.facebook.com/tools/debug/accesstoken/) to extending it).
    *   **Get User ID**: In the top bar, type `me/accounts` and click Submit. Copy the `id` of your Instagram account.


### Step 2: Add Secrets to GitHub
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
