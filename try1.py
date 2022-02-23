
import  requests
from    openpyxl        import load_workbook
from    openpyxl.styles import Alignment
from    bs4             import BeautifulSoup

WORKBOOK_NAME       = "final.xlsx"
WORKSHEET_NAME      = "export"
COLUMN_MAIN         = 1
COLUMN_SEC_LINK     = 9
COLUMN_10K_LINK     = 11
COLUMN_D_WORDCOUNT  = 12
COLUMN_D_SENTENCES  = 13
ROW_START           = 2

def test_final_read():
  workbook = load_workbook(WORKBOOK_NAME)
  worksheet = workbook[WORKSHEET_NAME]
  links = []
  for row_id in range(0,len(worksheet[COLUMN_MAIN])):
    next_row = row_id + ROW_START
    next_link = worksheet.cell(column=COLUMN_SEC_LINK,row=next_row).value
    if isinstance(next_link, str) and len(next_link) > 5:
      links.append(next_link)
  return(links)

def test_final_write():
  workbook = load_workbook(WORKBOOK_NAME)
  worksheet = workbook[WORKSHEET_NAME]
  # for row in safe_read(stats_path): # FIXME replace
  #   try:
  #     worksheet.cell(
  #       column  = 11, 
  #       row     = int(row['row_id']), 
  #       value   = "i can haz cheezburgr\ncat_salad_outrage.jpeg"
  #     ).alignment = Alignment(wrapText=True)
  #   except Exception as e:
  #     workbook.save(final_path)
  #     raise e
  workbook.save(WORKBOOK_NAME)

def test_requests():
  # resp = requests.get("https://www.sec.gov/Archives/edgar/data/1555280/000155528021000098/zts-20201231.htm")
  # resp = requests.get("https://www.sec.gov/Archives/edgar/data/edgar/data/1555280/0001555280-21-000098-index.htm")
  resp = requests.get("https://www.google.com/")
  html = resp.text
  soup = BeautifulSoup(html, "html.parser")
  print(soup.body.get_text().strip())

if __name__ == "__main__":
  # dirlinks_write(dirlinks_path)
  # test_final_write(WORKBOOK_NAME)
  # test_final_read(WORKBOOK_NAME)
  # test_requests()
  pass