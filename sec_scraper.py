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
from    datetime        import datetime as __datetime
from    datetime        import timezone as __timezone

def timename() -> str:
  return str(__datetime.now(__timezone.utc)).replace(" ","T").replace("-00:00","").replace("+00:00","").replace(":",".") + "Z"

logging.basicConfig(
  filename  = f'logs/{timename()}.log', 
  encoding  = 'utf-8',
  level     = logging.DEBUG,
  format    = '[%(asctime)s] %(levelname)s\t%(message)s'
)

WORKBOOK_NAME           = "kai-file.xlsx"
WORKSHEET_NAME          = "export"
COLUMN_MAIN             = 'A' # NOTICE that this is only used down in "update_all_stats" for ONE CASE! (this is due to the inconsistent API)
COLUMN_SEC_LINK         = 9
COLUMN_D_WORDCOUNT      = 11
COLUMN_D_SENTENCES      = 12
COLUMN_CONAME           = 5
ROW_START               = 2
TEN_SECONDS             = 10
MAX_CALLS_PER_SECOND    = 10
CHARACTER_SEARCH_RANGE  = 100
REGEX                   = re.compile(r'\bdiversity\b | \bdiverse\b',flags=re.I | re.X)
HEADERS                 = json.load(open("secrets.json"))["sec_request_headers"]

class SecLink():
  """
  Bad:  `https://www.sec.gov/ix?doc=/Archives/edgar/data/1555280/000155528021000098/zts-20201231.htm`
  Bad:  `Archives/edgar/data/1555280/000155528021000098/zts-20201231.htm`
  Fix:  `https://www.sec.gov/Archives/edgar/data/1555280/000155528021000098/zts-20201231.htm`
  """
  def __init__(self,address:str = None):
    self.fixed = False
    if address is not None:
      self.address = address
      self.fix()
    else:
      self.address = ""
  def fix(self):
    old_address = self.address
    if "ix?doc=/" in self.address:
      self.address = "https://www.sec.gov/" + self.address.split("ix?doc=/")[1]
    if self.address[0:14] == "Archives/edgar":
      self.address = "https://www.sec.gov/" + self.address
    if self.address[0:15] == "/Archives/edgar":
      self.address = "https://www.sec.gov" + self.address
    self.fixed = True
    logging.info(f"`SecLink.fix` fixed link from: {old_address} to: {self.address}")
  def __str__(self):
    return self.address
  def __repr__(self):
    return f"<SecLink ({'fixed' if self.fixed else 'broken'}) \"{self.address}\">"

@sleep_and_retry
@limits(calls=MAX_CALLS_PER_SECOND, period=TEN_SECONDS)
def get_page_rate_limited(link:str, headers=HEADERS) -> BeautifulSoup:
  logging.info(f"`get_page_rate_limited` downloading: {link}")
  resp = requests.get(link, headers=headers)
  html = resp.text
  return BeautifulSoup(html, "html.parser")

def get_sheet_dir_link(row_id:int, wb=WORKBOOK_NAME, ws=WORKSHEET_NAME, target=COLUMN_SEC_LINK) -> str:
  workbook = load_workbook(wb)
  worksheet = workbook[ws]
  next_link = worksheet.cell(column=target,row=row_id).value
  if isinstance(next_link, str) and len(next_link) > 5:
    logging.info(f"`get_sheet_dir_link` found: {next_link}")
    return next_link
  else:
    logging.error(f"`get_sheet_dir_link` encountered an entry with missing or invalid `sec_link` at row: {row_id}")
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
    raise Exception("`get_dir_10k_link` encountered an entry with no `10k_link`")
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

def update_all_stats(wb=WORKBOOK_NAME, ws=WORKSHEET_NAME, idc=COLUMN_MAIN, target=COLUMN_SEC_LINK, coname=COLUMN_CONAME):
  logging.info("`update_all_stats` started")
  workbook = load_workbook(wb)
  worksheet = workbook[ws]
  items = len(worksheet[idc])
  logging.info(f"running script for {items} items")
  for row_id in range(ROW_START,items):
    company_name = worksheet.cell(column=coname,row=row_id).value
    logging.info(f"`update_all_stats` NEXT row {row_id} (\"{company_name}\")")
    try:
      d_wordcount = worksheet.cell(column = COLUMN_D_WORDCOUNT, row = row_id).value
      d_sentences = worksheet.cell(column = COLUMN_D_SENTENCES, row = row_id).value
      if d_wordcount != "" and d_wordcount.isdigit():
        if int(d_wordcount) > 0 and len(d_sentences) > 50:
          logging.info(f"`is_complete` SKIPPED row {row_id}, appears to already be complete")
          continue
      else:
        logging.info(f"`is_complete` row {row_id} has errors in `COLUMN_D_WORDCOUNT` ({COLUMN_D_WORDCOUNT}), will overwrite")
    except Exception as e:
      logging.error(f"`is_complete` SKIPPED row {row_id}, could not determine completion status of entry")
      continue
    dir_link = worksheet.cell(column=target,row=row_id).value
    if not isinstance(dir_link, str) or not len(dir_link) > 5:
      logging.error(f"`get_sheet_dir_link` SKIPPED row: {row_id} (Encountered an entry with missing or invalid `sec_link`)")
      continue
    dir_page        = get_page_rate_limited(dir_link)
    try:
      clean_10k_link  = get_dir_10k_link(dir_page)
    except Exception as e:
      logging.error(f"`get_dir_10k_link` SKIPPED row {row_id}, could not find 10-k link")
      continue
    try:
      clean_10k       = get_page_rate_limited(clean_10k_link).body.get_text().strip().replace("\n"," ") # removing any newlines as well
    except Exception as e:
      logging.error(f"`update_all_stats.cleanup` SKIPPED row {row_id} due to unknown error")
      continue
    try:
      sentences       = get_diversity_instances(clean_10k)
    except:
      logging.error(f"`get_diversity_instances` SKIPPED row {row_id} due to unknown error")
      continue
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
      logging.critical(f"`write_sentence_stats` CRASHED on final statistics writing, attempting to save (failure on row: {row_id})\nCancelling future writes, PLEASE INSPECT FILE MANUALLY FOR ERRORS")
      workbook.save(wb)
      raise e
    logging.info(f"`write_sentence_stats` Saved sentence statistics for row: {row_id}")
    workbook.save(wb)
  logging.info("`update_all_stats` finished")

if __name__ == "__main__":
  update_all_stats()
  pass
