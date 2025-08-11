from app.config import config
import gspread
from gspread import Spreadsheet
from google.oauth2.service_account import Credentials


from app.utils.os_utils import save_to_disc


class ImportController:
    def from_google_sheets(self, url: str, target_path: str) -> None:
        scopes = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credentials_path = config.config_path / "credentials" / "cybernetics-460111-1cbe44a0762b.json"
        creds = Credentials.from_service_account_file(credentials_path, scopes=scopes)
        client = gspread.authorize(creds)

        # Открываем документ
        spreadsheet = client.open_by_url(url)

        # Сохраняем каждый лист как JSON
        all_data = self._get_all_sheets_data_as_dict(spreadsheet)
        save_to_disc(all_data, target_path)
        # print(f"Imported data to {target_path}")

    def _get_all_sheets_data_as_dict(self, spreadsheet: Spreadsheet) -> dict:
        result = {}

        for worksheet in spreadsheet.worksheets():
            rows = worksheet.get_all_values()

            if not rows:
                result[worksheet.title] = []
                continue

            num_cols = max(len(row) for row in rows)
            headers = [f'col_{i + 1}' for i in range(num_cols)]
            normalized_rows = [row + [''] * (num_cols - len(row)) for row in rows]

            result[worksheet.title] = [
                dict(zip(headers, row)) for row in normalized_rows
            ]

        return result


