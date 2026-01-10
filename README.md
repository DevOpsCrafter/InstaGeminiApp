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

#### 2. Email Setup (Gmail App Password)

Since Meta Developer access has restrictions, we're using **email delivery** instead. The bot will email you the generated image daily.

**Step A: Enable 2-Factor Authentication** (IF NOT ALREADY DONE)
1. Go to [**Google Account Security**](https://myaccount.google.com/security)
2. Click **2-Step Verification** → **Get Started**
3. Follow the prompts to set it up

**Step B: Create App Password**
1. Go to [**App Passwords**](https://myaccount.google.com/apppasswords)
2. In the dropdown, select **Mail** (or type "Astroboli Bot")
3. Click **Generate**
4. **Copy the 16-character password** (format: `xxxx xxxx xxxx xxxx`)
5. Save this - it's your `EMAIL_PASSWORD`

**What you'll need:**
- `YOUR_EMAIL`: Your Gmail address (e.g., `yourname@gmail.com`)
- `EMAIL_PASSWORD`: The 16-character app password you just created
### Step 2: Configure Your Credentials
1.  Go to this repository on GitHub.
2.  Click **Settings** > **Secrets and variables** > **Actions**.
3.  Click **New repository secret**.
4.  Add the following three secrets:
    -   `GEMINI_API_KEY`
    -   `YOUR_EMAIL`
    -   `EMAIL_PASSWORD`

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
