# Online deployment quick start (no local installation on your work PC)

## Before you start
- You need permission to access GitHub and Streamlit Community Cloud.
- Use a personal email/account if allowed by your employer.
- Do not upload secrets, `.env`, database files, or private company data to a public repository.

## 1. Create GitHub account and repository
1. Open https://github.com/signup and create your account.
2. Verify your email.
3. Click **+** → **New repository**.
4. Name: `algeria-supplier-discovery`
5. Choose **Public** only if you are comfortable making the code public. Do not include any data or secrets.
6. Create repository.

## 2. Upload the code in your browser
1. Extract the downloaded ZIP using a permitted file manager.
2. Open the new GitHub repository.
3. Click **Add file** → **Upload files**.
4. Upload these files at the repository root:
   - `app.py`
   - `database.py`
   - `discovery.py`
   - `website_collector.py`
   - `exporters.py`
   - `requirements.txt`
   - `.gitignore`
   - `README.md`
5. Do not upload `.env`, `data/suppliers.db`, or service-account JSON credentials.
6. Commit the files.

If your work browser blocks file uploads or GitHub, stop here and ask IT which approved hosting workflow is available.

## 3. Deploy on Streamlit
1. Open https://share.streamlit.io/
2. Sign in and connect your GitHub account.
3. Choose **Create app**.
4. Select repository `algeria-supplier-discovery`, branch `main`, file path `app.py`.
5. Open **Advanced settings** → **Secrets**.
6. If you have a Brave Search API key, add:
   `BRAVE_SEARCH_API_KEY = "YOUR_KEY"`
   If not, deploy without it to test the interface in demo mode.
7. Click **Deploy** and wait for the app URL.

## 4. Test
- Open the app URL.
- Search for a sample activity such as `fournisseur emballage`.
- Without an API key, only demo placeholders appear; this is expected.
- With a configured key, confirm that result URLs open and check the evidence before marking suppliers verified.
- Export a CSV/Excel backup after any test data entry.

## Storage warning
This prototype uses SQLite on the hosted app. Hosted local storage may reset when the app restarts or redeploys. Treat this as a demo until persistent managed storage is configured. Do not enter confidential company data yet.
