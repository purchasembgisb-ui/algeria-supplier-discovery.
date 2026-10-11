from io import BytesIO
import os
import pandas as pd

def save_csv(df):
    return df.to_csv(index=False).encode("utf-8-sig")

def save_excel(df):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Suppliers")
    return buffer.getvalue()

def push_google_sheets(df, spreadsheet_id, worksheet_name):
    if not spreadsheet_id.strip():
        raise ValueError("Enter a Google spreadsheet ID.")
    credentials_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "").strip()
    if not credentials_file:
        raise ValueError("Set GOOGLE_APPLICATION_CREDENTIALS to your service-account JSON file path.")
    import gspread
    from google.oauth2.service_account import Credentials
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials = Credentials.from_service_account_file(credentials_file, scopes=scopes)
    client = gspread.authorize(credentials)
    spreadsheet = client.open_by_key(spreadsheet_id)
    try:
        worksheet = spreadsheet.worksheet(worksheet_name)
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=worksheet_name, rows=1000, cols=max(20, len(df.columns)))
    worksheet.clear()
    values = [df.columns.astype(str).tolist()] + df.fillna("").astype(str).values.tolist()
    worksheet.update(values, value_input_option="RAW")
