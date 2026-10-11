import streamlit as st
import pandas as pd
from dotenv import load_dotenv
load_dotenv()
from pathlib import Path
from database import init_db, list_companies, upsert_companies, export_all
from discovery import build_queries, run_search
from website_collector import enrich_url
from exporters import save_csv, save_excel, push_google_sheets

st.set_page_config(page_title="Algeria Supplier Discovery", page_icon="🔎", layout="wide")
DB_PATH = Path("data/suppliers.db")
init_db(DB_PATH)

st.title("Algeria Supplier Discovery")
st.caption("Find and organize publicly available supplier and distributor information in Algeria.")

with st.sidebar:
    st.header("Search settings")
    keyword = st.text_input("Product / activity", value="industrial equipment")
    wilaya = st.selectbox("Wilaya", ["All Algeria", "Alger", "Oran", "Constantine", "Sétif", "Blida", "Mostaganem", "Annaba", "Tlemcen", "Béjaïa"])
    language = st.selectbox("Search language", ["French", "Arabic", "French + Arabic"])
    max_results = st.slider("Maximum search results", 5, 50, 15, 5)
    st.caption("Search uses the configured provider in .env. Without an API key, demo mode is available.")

tab_search, tab_database, tab_import, tab_export = st.tabs(["Discover", "Database", "Import URLs / CSV", "Export"])

with tab_search:
    st.subheader("Discover supplier leads")
    st.write("Search public web results, then review the leads before adding them to your database.")
    if st.button("Search for suppliers", type="primary"):
        queries = build_queries(keyword, wilaya, language)
        results = []
        with st.spinner("Searching configured provider…"):
            for query in queries[:4]:
                results.extend(run_search(query, max_results=max_results, demo_if_unconfigured=True))
        if results:
            df = pd.DataFrame(results).drop_duplicates(subset=["source_url"])
            st.session_state["search_results"] = df
        else:
            st.session_state["search_results"] = pd.DataFrame()
            st.warning("No results returned. Configure a search API key in .env or try another keyword.")
    if "search_results" in st.session_state:
        found = st.session_state["search_results"]
        if not found.empty:
            st.dataframe(found, use_container_width=True, hide_index=True)
            if st.button("Save displayed leads to database"):
                rows = found.to_dict("records")
                upsert_companies(DB_PATH, rows)
                st.success(f"Saved {len(rows)} lead records (duplicates are updated).")
        else:
            st.info("No leads found yet.")

with tab_database:
    st.subheader("Supplier database")
    db = pd.DataFrame(list_companies(DB_PATH))
    if db.empty:
        st.info("Your database is empty. Run a search or import a CSV/URLs.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            filter_text = st.text_input("Filter by company, activity, or keyword")
        with c2:
            status = st.selectbox("Verification status", ["All", "Unverified", "Verified", "Rejected"])
        if filter_text:
            mask = db.astype(str).apply(lambda col: col.str.contains(filter_text, case=False, na=False)).any(axis=1)
            db = db[mask]
        if status != "All":
            db = db[db["verification_status"] == status]
        st.dataframe(db, use_container_width=True, hide_index=True)
        st.caption("Treat all search results as unverified until checked against reliable evidence.")

with tab_import:
    st.subheader("Import URLs or a CSV")
    uploaded = st.file_uploader("Upload CSV with at least a company_name or source_url column", type=["csv"])
    if uploaded is not None:
        try:
            imported = pd.read_csv(uploaded).fillna("")
            st.dataframe(imported.head(20), use_container_width=True)
            if st.button("Import CSV rows"):
                upsert_companies(DB_PATH, imported.to_dict("records"))
                st.success(f"Imported {len(imported)} rows.")
        except Exception as exc:
            st.error(f"Could not read CSV: {exc}")
    urls_text = st.text_area("Or paste public company / directory URLs (one per line)")
    if st.button("Collect permitted public pages"):
        urls = [u.strip() for u in urls_text.splitlines() if u.strip()]
        rows = []
        progress = st.progress(0)
        for i, url in enumerate(urls):
            try:
                rows.append(enrich_url(url))
            except Exception as exc:
                rows.append({"source_url": url, "notes": f"Collection failed: {exc}", "verification_status": "Unverified"})
            progress.progress((i + 1) / max(1, len(urls)))
        if rows:
            upsert_companies(DB_PATH, rows)
            st.success(f"Processed {len(rows)} URL(s). Review the database and verify each lead.")

with tab_export:
    st.subheader("Export records")
    all_rows = export_all(DB_PATH)
    df = pd.DataFrame(all_rows)
    if df.empty:
        st.info("Nothing to export yet.")
    else:
        st.download_button("Download CSV", data=save_csv(df), file_name="algeria_suppliers.csv", mime="text/csv")
        st.download_button("Download Excel", data=save_excel(df), file_name="algeria_suppliers.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        st.markdown("### Optional: Google Sheets")
        st.write("Configure a Google service account and share the destination spreadsheet with its service-account email.")
        spreadsheet_id = st.text_input("Google spreadsheet ID", value="")
        worksheet = st.text_input("Worksheet name", value="Suppliers")
        if st.button("Export to Google Sheets"):
            try:
                push_google_sheets(df, spreadsheet_id, worksheet)
                st.success("Export sent to Google Sheets.")
            except Exception as exc:
                st.error(f"Google Sheets export failed: {exc}")

st.divider()
st.caption("Use only sources and data you are authorized to access. Follow applicable law, site terms, robots.txt, and reasonable rate limits.")
