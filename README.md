# iOSGeminiApp – Quick Free‑Cost Gemini App + Share‑Sheet Flow

## Overview
This repository contains a **single‑screen SwiftUI iOS app** that:
1. Launches the **Gemini image‑generation app** (via a custom URL scheme – `gemini://`).
2. Lets the user pick the image they just saved to the Photos library.
3. Shares that image to **Instagram** using the native iOS share sheet, pre‑filled with a caption that includes **exactly five hashtags**.
4. All of this happens with **one tap** from the user’s perspective.

The code is deliberately minimal so you can drop it into a fresh Xcode SwiftUI project and run on an iPhone 15 (or any iOS 15+ device).

---
## Project Structure
```
📁 iOSGeminiApp/
├─ .gitignore                # Xcode‑specific ignore patterns
├─ Info.plist                # Permissions + Instagram URL scheme
├─ ContentView.swift         # UI + core flow (button, picker, sharing)
└─ README.md                 # This file (setup instructions)
```

---
## Prerequisites
- **Xcode 15** (or later) on macOS – required to build iOS 15+ apps.
- **Gemini app** installed from the App Store (search for *Gemini – AI Image Generator*). The app must support the `gemini://` URL scheme; if it does not, the user will need to open the app manually.
- An **Instagram app** installed on the device (the share sheet will open it automatically).
- A **GitHub** account if you want to push the repo; otherwise you can just keep the folder locally.

---
## Step‑by‑Step Setup
1. **Create a new Xcode project**
   - Open Xcode → *File → New → Project*.
   - Choose **App** under iOS → **SwiftUI** interface → **Swift** language.
   - Name the project `iOSGeminiApp` (or any name you like) and set the bundle identifier to something unique, e.g., `com.yourname.iOSGeminiApp`.
   - Choose a location inside `c:\Users\Pushkar\Documents\Dev\AntiGravity\iOSGeminiApp` (the folder we created).
2. **Replace the generated files**
   - Delete the default `ContentView.swift` that Xcode created.
   - Copy the `ContentView.swift` from this repository into the project’s *iOSGeminiApp* group.
   - Replace the automatically generated `Info.plist` with the one provided here (or merge the two, ensuring the keys `NSPhotoLibraryUsageDescription` and `LSApplicationQueriesSchemes` are present).
   - Add the `.gitignore` file at the root of the project (it will not be part of the Xcode build but is useful for version control).
3. **Add the Instagram URL scheme** (optional but recommended)
   - In Xcode, select the project → *Info* tab → *URL Types* → click **+**.
   - Set **Identifier** to `instagram` and **URL Schemes** to `instagram` (this allows the app to query if Instagram is installed).
4. **Build & Run**
   - Connect an iPhone 15 (or use the iPhone 15 simulator).
   - Press **Run** (⌘R). The app will launch with a single **Generate & Post** button.
5. **Using the app**
   - Tap **Generate & Post**.
   - The app attempts to open the Gemini app (`gemini://`). If the scheme works, Gemini opens; otherwise you’ll see a message asking you to open it manually.
   - Inside Gemini, generate an image using any prompt you like and **save it to Photos**.
   - Return to the iOSGeminiApp – after a short delay the photo picker appears; select the image you just saved.
   - The app automatically presents the iOS share sheet limited to Instagram, with the caption `#gemini #aiart #creative #instapost #free`.
   - Tap **Share** in Instagram – the image appears in your feed with the caption and hashtags.

---
## Customisation
- **Caption / Hashtags** – Edit the `caption` constant inside `InstagramSharer.share(image:)` to suit your brand.
- **Gemini URL scheme** – If the Gemini app uses a different scheme, replace `gemini://` in `generateAndShare()` with the correct one.
- **Delay before picker** – The `DispatchQueue.main.asyncAfter(deadline: .now() + 5)` line gives the user time to generate and save the image. Adjust the seconds if you need more/less time.
- **Error handling** – For production, replace the simple `statusMessage` strings with proper alerts.

---
## License & Attribution
This starter code is provided **as‑is** under the MIT License. It uses only Apple‑provided frameworks (SwiftUI, PhotosUI) and does not embed any third‑party binaries.

---
## Next Steps (Optional Enhancements)
- **Automatic image upload** – If you later decide to host the image publicly, you could add a tiny server‑side endpoint (e.g., Firebase Functions) and switch to the Instagram Graph API for zero‑tap posting.
- **In‑app Gemini integration** – Use the Gemini Cloud API (paid) to generate images directly from your app, removing the need for the external Gemini app.
- **UI polish** – Add animations, a loading spinner while waiting for the Gemini app, and better error dialogs.

---
Enjoy building your quick‑and‑free Instagram posting app! If you run into any issues or want to expand the functionality, just let me know.
