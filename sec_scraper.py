"""
2022 MIT License Drexel University
"""

import  requests
import  json
import  re
import  logging
from    openpyxl        import load_workbook
from    openpyxl.styles import Alignment
from    bs4             import BeautifulSoup
from    ratelimit       import limits, RateLimitException, sleep_and_retry

WORKBOOK_NAME           = "kai-file.xlsx"
WORKSHEET_NAME          = "export"
COLUMN_MAIN             = 1
COLUMN_SEC_LINK         = 9
COLUMN_10K_LINK         = 11
COLUMN_D_WORDCOUNT      = 12
COLUMN_D_SENTENCES      = 13
ROW_START               = 2
TEN_SECONDS             = 10 # Out of decency, using 10 seconds as opposed to 1 second long wait
MAX_CALLS_PER_SECOND    = 10
CHARACTER_SEARCH_RANGE  = 100
REGEX                   = 'divers' # for now, just using a simple search string
HEADERS                 = json.load(open("secrets.json"))["sec_request_headers"]

class SecLink():
  """
  Bad: `https://www.sec.gov/ix?doc=/Archives/edgar/data/1555280/000155528021000098/zts-20201231.htm`
  Fix: `https://www.sec.gov/Archives/edgar/data/1555280/000155528021000098/zts-20201231.htm`
  """
  def __init__(self,address:str = None):
    self.fixed = False
    if address is not None:
      self.address = address
      self.fix()
    else:
      self.address = ""
  def fix(self):
    if "ix?doc=/" in self.address:
      self.address = "https://www.sec.gov/" + self.address.split("ix?doc=/")[1]
    self.fixed = True
  def __str__(self):
    return self.address
  def __repr__(self):
    return f"<SecLink ({'fixed' if self.fixed else 'broken'}) \"{self.address}\">"

@sleep_and_retry
@limits(calls=MAX_CALLS_PER_SECOND, period=TEN_SECONDS)
def get_page_rate_limited(link:str, headers=HEADERS) -> BeautifulSoup:
  resp = requests.get(link, headers=headers)
  html = resp.text
  return BeautifulSoup(html, "html.parser")

def get_sheet_dir_link(row_id:int, wb=WORKBOOK_NAME, ws=WORKSHEET_NAME, idc=COLUMN_MAIN, target=COLUMN_SEC_LINK) -> str:
  workbook = load_workbook(wb)
  worksheet = workbook[ws]
  next_link = worksheet.cell(column=target,row=row_id).value
  if isinstance(next_link, str) and len(next_link) > 5:
    logging.info(f"Found: {next_link}")
    return next_link
  else:
    logging.error(f"Encountered an entry with missing or invalid `sec_link` at row: {row_id}")
    return next_link

def get_dir_10k_link(page_dir:BeautifulSoup) -> str:
  link_10k = ""
  for table_row in page_dir.find_all("tr"):
    try:
      if table_row.find_all("td")[1].string in ["10-K", "10K", "10k", "10-k"]:
        link_10k = SecLink(table_row.find_all('td')[2].a.get('href'))
    except:
      continue
  if link_10k == "":
    logging.error(f"Encountered an entry with no `10k_link`, returning empty link")
  return link_10k

def get_diversity_instances(plaintext:str) -> list:
  min_distance = 0
  max_distance = len(plaintext)
  places = (match.start() for match in re.finditer(REGEX, plaintext))
  sentences = []
  for place in places:
    start = max(place - CHARACTER_SEARCH_RANGE, min_distance)
    stop  = min(place + CHARACTER_SEARCH_RANGE, max_distance)
    new_sentence = plaintext[start:stop]
    sentences.append(new_sentence)
  return sentences

def write_sentence_stats(row_id:int, sentences:list, wb=WORKBOOK_NAME, ws=WORKSHEET_NAME):
  workbook = load_workbook(wb)
  worksheet = workbook[ws]
  try:
    worksheet.cell(
      column  = COLUMN_D_WORDCOUNT,
      row     = row_id,
      value   = len(sentences)
    )
    worksheet.cell(
      column  = COLUMN_D_SENTENCES,
      row     = row_id,
      value   = "\n".join(sentences)
    ).alignment = Alignment(wrapText=True)
  except Exception as e:
    logging.critical(f"Final Statistics Writing Interrupted (`write_sentence_stats`), attempting to save (failure on row: {row_id})")
    workbook.save(wb)
    raise e
  logging.info(f"Saved sentence statistics for row: {row_id}")
  workbook.save(wb)

def overwrite_all_stats(wb=WORKBOOK_NAME, ws=WORKSHEET_NAME, idc=COLUMN_MAIN, target=COLUMN_SEC_LINK):
  workbook = load_workbook(wb)
  worksheet = workbook[ws]
  links = []
  # for all items in the excel file
  for row_id in range(ROW_START,len(worksheet[idc])):
    dir_link = worksheet.cell(column=target,row=row_id).value
    if not isinstance(dir_link, str) or not len(dir_link) > 5:
      logging.error(f"Encountered an entry with missing or invalid `sec_link` at row: {row_id} was SKIPPED")
      continue
    dir_page        = get_page_rate_limited(dir_link)
    clean_10k_link  = get_dir_10k_link(dir_page)
    clean_10k       = get_page_rate_limited(clean_10k_link).body.get_text().strip()
    sentences       = get_diversity_instances(clean_10k)
    try:
      worksheet.cell(
        column  = COLUMN_D_WORDCOUNT,
        row     = row_id,
        value   = len(sentences)
      )
      worksheet.cell(
        column  = COLUMN_D_SENTENCES,
        row     = row_id,
        value   = "\n".join(sentences)
      ).alignment = Alignment(wrapText=True)
    except Exception as e:
      logging.critical(f"Final Statistics Writing Interrupted (`write_sentence_stats`), attempting to save (failure on row: {row_id})")
      workbook.save(wb)
      raise e
    logging.info(f"Saved sentence statistics for row: {row_id}")
    workbook.save(wb)

if __name__ == "__main__":
  overwrite_all_stats()
  pass
