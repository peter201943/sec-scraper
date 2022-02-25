"""
MIT License

Copyright (c) 2022 Peter J. Mangelsdorf

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
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
from    pathlib         import Path

def timename() -> str:
  return str(__datetime.now(__timezone.utc)).replace(" ","T").replace("-00:00","").replace("+00:00","").replace(":",".") + "Z"

logging.basicConfig(
  filename  = f'logs/{timename()}.csv',
  encoding  = 'utf-8',
  level     = logging.DEBUG,
  format    = '"%(asctime)s",%(levelname)s,"%(filename)s.%(funcName)s","%(message)s"'
)

WORKBOOK_NAME           = "kai-file.xlsx"
WORKSHEET_NAME          = "export"
COLUMN_MAIN             = 'A' # NOTICE that this is only used down in "update_workbook" for ONE CASE! (this is due to the inconsistent API)
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

Path("logs/").mkdir(parents=True, exist_ok=True)

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
      if table_row.find_all("td")[3].string in ["10-K", "10K", "10k", "10-k"]:
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

def update_workbook(row_ids=None, wb=WORKBOOK_NAME, ws=WORKSHEET_NAME, idc=COLUMN_MAIN, target=COLUMN_SEC_LINK, coname=COLUMN_CONAME):
  logging.info("sec_scraper.update_workbook: started")
  workbook = load_workbook(wb)
  worksheet = workbook[ws]
  items = len(worksheet[idc])
  if not row_ids:
    row_ids = range(ROW_START,items + 1)
  if isinstance(row_ids,int):
    row_ids = [row_ids]
  logging.debug(f"sec_scraper.update_workbook: running script for {len(row_ids)} items")
  for row_id in row_ids:
    if row_id < ROW_START:
      continue
    company_name = worksheet.cell(column=coname,row=row_id).value
    logging.debug(f"sec_scraper.update_workbook: NEXT row {row_id} (\"{company_name}\")")
    try:
      d_wordcount = worksheet.cell(column = COLUMN_D_WORDCOUNT, row = row_id).value
      d_sentences = worksheet.cell(column = COLUMN_D_SENTENCES, row = row_id).value
      if isinstance(d_wordcount,int):
        if d_wordcount == 0 and isinstance(d_sentences,str) and len(d_sentences) == 0:
          logging.debug(f"sec_scraper.is_complete: row {row_id} appears to already be complete")
          logging.debug(f"sec_scraper.update_workbook: SKIPPED row {row_id}")
          continue
        elif d_wordcount > 0 and isinstance(d_sentences,str) and len(d_sentences) > 50:
          logging.debug(f"sec_scraper.is_complete: row {row_id} appears to already be complete")
          logging.debug(f"sec_scraper.update_workbook: SKIPPED row {row_id}")
          continue
        else:
          logging.debug(f"sec_scraper.is_complete: row {row_id} has errors in `COLUMN_D_SENTENCES` ({COLUMN_D_SENTENCES}), will overwrite")
      else:
        logging.debug(f"sec_scraper.is_complete: row {row_id} has errors in `COLUMN_D_SENTENCES` ({COLUMN_D_SENTENCES}), will overwrite")
    except Exception as e:
      logging.error(f"sec_scraper.is_complete: crashed on determining completion status of row {row_id}")
      logging.error(f"sec_scraper.is_complete: {e}")
      logging.error(f"sec_scraper.update_workbook: SKIPPED row {row_id}")
      continue
    dir_link = worksheet.cell(column=target,row=row_id).value
    if not isinstance(dir_link, str) or not len(dir_link) > 5:
      logging.error(f"sec_scraper.get_sheet_dir_link: row {row_id} has missing or invalid `sec_link`")
      logging.error(f"sec_scraper.update_workbook: SKIPPED row {row_id}")
      continue
    dir_page          = get_page_rate_limited(dir_link)
    try:
      clean_10k_link  = get_dir_10k_link(dir_page)
    except Exception as e:
      logging.error(f"sec_scraper.get_dir_10k_link: could not find 10-k link for row {row_id}")
      logging.error(f"sec_scraper.get_dir_10k_link: {e}")
      logging.error(f"sec_scraper.update_workbook: SKIPPED row {row_id}")
      continue
    try:
      clean_10k       = get_page_rate_limited(clean_10k_link).body.get_text().strip().replace("\n"," ") # removing any newlines as well
    except Exception as e:
      logging.error(f"sec_scraper.cleanup: could not cleanup row {row_id} body")
      logging.error(f"sec_scraper.cleanup: {e}")
      logging.error(f"sec_scraper.update_workbook: SKIPPED row {row_id}")
      continue
    try:
      sentences       = get_diversity_instances(clean_10k)
    except Exception as e:
      logging.error(f"sec_scraper.get_diversity_instances: unknown error")
      logging.error(f"sec_scraper.get_diversity_instances: {e}")
      logging.error(f"sec_scraper.update_workbook: SKIPPED row {row_id}")
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
      logging.critical(f"sec_scraper.write_sentence_stats: CRASHED on final statistics writing, attempting to save (failure on row: {row_id})")
      logging.critical(f"sec_scraper.write_sentence_stats: {e}")
      logging.critical(f"sec_scraper.write_sentence_stats: Cancelling future writes, PLEASE INSPECT FILE MANUALLY FOR ERRORS")
      workbook.save(wb)
      logging.error("sec_scraper.update_workbook: exiting early")
      exit()
    logging.debug(f"sec_scraper.write_sentence_stats: Saved sentence statistics for row: {row_id}")
    workbook.save(wb)
  logging.info("sec_scraper.update_workbook: finished")

if __name__ == "__main__":
  update_workbook()
  pass
