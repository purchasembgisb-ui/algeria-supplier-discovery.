# Algeria Supplier Discovery — MVP

A local Python application to discover and organize supplier/distributor leads in Algeria.

## Features in this first version

- Streamlit dashboard
- French/Arabic search-query builder
- Optional Brave Search API connector
- Import URLs and CSV files
- Public HTML page extraction with robots.txt check and conservative request delay
- SQLite database with source URLs, timestamps, and verification status
- Duplicate handling by source URL
- CSV and Excel export
- Optional Google Sheets export

## Important limits

- Search results are leads, not verified suppliers.
- No automated Facebook/Instagram scraping is included. Use official, authorized APIs and permissions for social platforms.
- This tool does not bypass logins, paywalls, CAPTCHAs, robots.txt, or other access controls.
- The first version does not guarantee completeness or validate company registration status.
- Before production use, review applicable Algerian privacy/data-protection requirements, each website's terms, and retention requirements.
- Set the User-Agent contact to a real monitored address before any sustained collection.
- The website collector only supports HTML pages; it does not crawl an entire site or follow links automatically.

## Windows setup

1. Install Python 3.11 or newer from https://www.python.org/downloads/
2. Extract this folder to a location such as `C:\\algeria_supplier_discovery`.
3. Open Command Prompt in that folder.
4. Create and activate a virtual environment:

   ```bat
   py -m venv .venv
   .venv\\Scripts\\activate
   ```

5. Install dependencies:

   ```bat
   pip install -r requirements.txt
   ```

6. Copy `.env.example` to `.env`, then add your search provider key if you have one.
7. Load environment variables and launch:

   ```bat
   copy .env.example .env
   streamlit run app.py
   ```

   If the API key is added to `.env`, load it by adding these two lines near the top of `app.py`:

   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```

8. Streamlit will display a local URL, usually `http://localhost:8501`.

## Search provider

The app supports Brave Search API through `BRAVE_SEARCH_API_KEY`. If no key is configured, it shows an explicit demo placeholder rather than inventing real suppliers. Check the provider's current pricing, terms, geographic coverage, and rate limits before use.

Google's Custom Search JSON API is not available to new customers according to Google's current documentation, so it is not used as the default connector.

## Google Sheets setup

1. Create a Google Cloud project and enable Google Sheets API.
2. Create a service account and download its JSON key securely.
3. Share the target spreadsheet with the service-account email as an editor.
4. Set `GOOGLE_APPLICATION_CREDENTIALS` to the JSON key file path.
5. Enter the spreadsheet ID in the Export tab.

Do not commit API keys or service-account credentials to source control.

## Suggested next improvements

- Add a source registry with each site's terms/access notes.
- Add manual company verification and duplicate review screens.
- Add official business registry lookups where permitted.
- Add domain-level crawl limits and persistent crawl logs.
- Add source-specific adapters for directories that expressly permit automated access.
- Add Google Sheets two-way synchronization only after defining conflict and deletion rules.


## Browser-only deployment (no installation on your work PC)

1. Create a GitHub account in your browser.
2. Create a **public** repository named `algeria-supplier-discovery` (do not include API keys or private company data in the repository).
3. Extract the ZIP on a personal device or use any permitted file manager. On GitHub, choose **Add file → Upload files** and upload the project files from the project folder. Keep `app.py`, `database.py`, `discovery.py`, `website_collector.py`, `exporters.py`, and `requirements.txt` at the repository root. Do not upload `.env`, any database file, or service-account credentials.
4. Visit https://share.streamlit.io/, sign in, connect GitHub, choose **Create app**, select the repository, branch `main`, and main file `app.py`.
5. In deployment settings / **Advanced settings → Secrets**, add:

   ```toml
   BRAVE_SEARCH_API_KEY = "paste-your-provider-key-here"
   ```

   Keep the key private. If you do not have a key yet, omit this setting; the app will show demo placeholders, not live search results.
6. Deploy and open the generated `*.streamlit.app` URL.

### Important cloud storage note

This first version uses SQLite. On hosted platforms, local disk contents can be ephemeral, so do not rely on this database as the only copy of important records. Export backups regularly. Before using it as a real working database, upgrade to a persistent managed database (for example, a managed PostgreSQL service) and configure access control. A public GitHub repository also makes source code public, so never commit credentials or company contact datasets.
