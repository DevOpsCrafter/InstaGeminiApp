import urllib.parse

print("=" * 60)
print("Instagram Access Token Generator")
print("=" * 60)
print()

# Get credentials
app_id = input("Enter your App ID: ").strip()
app_secret = input("Enter your App Secret: ").strip()
redirect_uri = "https://localhost/"  # Standard for testing

print("\n" + "=" * 60)
print("STEP 1: Get Authorization Code")
print("=" * 60)

# Generate OAuth URL
oauth_url = (
    f"https://www.facebook.com/v19.0/dialog/oauth?"
    f"client_id={app_id}&"
    f"redirect_uri={urllib.parse.quote(redirect_uri)}&"
    f"scope=instagram_basic,instagram_content_publish,pages_show_list,pages_read_engagement&"
    f"response_type=code"
)

print("\n1. Click this link to authorize:")
print(f"\n{oauth_url}\n")
print("2. After clicking 'Continue', you'll be redirected to a localhost page")
print("3. Copy the ENTIRE URL from your browser address bar (it will contain '?code=...')")
print("4. Paste it below:\n")

redirect_response = input("Paste the full redirect URL here: ").strip()

# Extract code
try:
    code = redirect_response.split("code=")[1].split("&")[0]
    print(f"\n✓ Authorization code extracted: {code[:20]}...")
except:
    print("\n❌ Error: Could not find 'code=' in the URL. Please try again.")
    exit(1)

print("\n" + "=" * 60)
print("STEP 2: Exchange Code for Access Token")
print("=" * 60)

# Generate token exchange URL
token_url = (
    f"https://graph.facebook.com/v19.0/oauth/access_token?"
    f"client_id={app_id}&"
    f"redirect_uri={urllib.parse.quote(redirect_uri)}&"
    f"client_secret={app_secret}&"
    f"code={code}"
)

print("\nRun this command in your browser or use curl:\n")
print(f"{token_url}\n")
print("Copy the response and you'll have your SHORT-LIVED access token.")
print("\n" + "=" * 60)
print("STEP 3: Get Long-Lived Token (60 days)")
print("=" * 60)

short_token = input("\nPaste your short-lived access token here: ").strip()

long_lived_url = (
    f"https://graph.facebook.com/v19.0/oauth/access_token?"
    f"grant_type=fb_exchange_token&"
    f"client_id={app_id}&"
    f"client_secret={app_secret}&"
    f"fb_exchange_token={short_token}"
)

print("\nVisit this URL to get your LONG-LIVED token:\n")
print(f"{long_lived_url}\n")

print("=" * 60)
print("DONE! Save your long-lived token to secrets.env")
print("=" * 60)
