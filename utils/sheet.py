import gspread
import os
from dotenv import load_dotenv

load_dotenv()

class Sheet:
    def __init__(self) -> None:
        self.credentials = {
            "type": "service_account",
            "project_id": os.environ['PROJECT_ID'],
            "private_key_id": os.environ['PRIVATE_KEY_ID'],
            "private_key": os.environ['PRIVATE_KEY'].replace('\\n', '\n'),
            "client_email": os.environ['CLIENT_EMAIL'],
            "client_id": os.environ['CLIENT_ID'],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": os.environ['CLIENT_X509_CERT_URL']
        }
        self.scopes = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        self.gc = gspread.service_account_from_dict(self.credentials, scopes=self.scopes)
        self.SPREADSHEET_KEY = os.environ['SPREADSHEET_KEY']
        self.workbook = self.gc.open_by_key(self.SPREADSHEET_KEY)

    def getSheet(self, author_id: str):
        worksheet_list = self.workbook.worksheets()
        exist = False
        for current in worksheet_list:
            if current.title == author_id:
                exist = True
        if exist == False:
            self.workbook.add_worksheet(title=author_id,rows=100,cols=4)
            self.initSheet(author_id)
        return self.workbook.worksheet(author_id)

    def checkCell(self, worksheet: gspread.Worksheet, cell: str) -> bool:
        if worksheet.acell(cell).value == '0':
            return True
        else:
            return False

    def initSheet(self, author_id: str):
        worksheet = self.getSheet(author_id)
        worksheet.update_acell('A1', '0')
        worksheet.update_acell('B1', '0')
        worksheet.update_acell('C1', '0')
        if self.checkCell(worksheet, 'A4') == True:
            worksheet.update_acell('A4','0')
        if self.checkCell(worksheet, 'B4') == True:
            worksheet.update_acell('B4','0')

    def checkStats(self, author_id: str):
        worksheet_list = self.workbook.worksheets()
        for current in worksheet_list:
            if current.title == author_id:
                if self.checkCell(current, 'A1') == True or self.checkCell(current, 'B1') == True or self.checkCell(current, 'C1') == True:
                    return False, False, False
                id = current.acell('A1').value
                tag = current.acell('B1').value
                puuid = current.acell('C1').value
                return id, tag, puuid
        return False, False, False #then send not registered message in main method

    def removeSheet(self, author_id: str):
        worksheet = self.getSheet(author_id)
        worksheet.update_acell('A2','')
        worksheet.update_acell('B2','')
        worksheet.update_acell('A3','0')
        worksheet.update_acell('B3','0')
        worksheet.update_acell('A4','0')
        worksheet.update_acell('B4','0')

    def enableTrack(self, author_id: str, toggle: str, channel_id):
        sheet = self.getSheet(author_id)
        if toggle == "on":
            sheet.update_acell('A2',"on")
            sheet.update_acell('A3',str(channel_id))
            return True
        elif toggle == "off":
            sheet.update_acell('A2',"off")
            return False
        return