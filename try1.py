
import  requests
import  json
from    openpyxl        import load_workbook
from    openpyxl.styles import Alignment
from    bs4             import BeautifulSoup
from    ratelimit       import limits, RateLimitException, sleep_and_retry

WORKBOOK_NAME         = "final.xlsx"
WORKSHEET_NAME        = "export"
COLUMN_MAIN           = 1
COLUMN_SEC_LINK       = 9
COLUMN_10K_LINK       = 11
COLUMN_D_WORDCOUNT    = 12
COLUMN_D_SENTENCES    = 13
ROW_START             = 2
ONE_MINUTE            = 60
MAX_CALLS_PER_MINUTE  = 10

HEADERS = json.load(open("secrets.json"))["sec_request_headers"]

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
  def fix(self):
    if "https://www.sec.gov/ix?" in self.address:
      self.address = "https://www.sec.gov/" + self.address.split("ix?doc=/")[1]
    self.fixed = True
  def __str__(self):
    return self.address
  def __repr__(self):
    return f"<SecLink ({'fixed' if self.fixed else 'broken'}) \"{self.address}\">"

def test_read(wb=WORKBOOK_NAME, ws=WORKSHEET_NAME, idc=COLUMN_MAIN, target=COLUMN_SEC_LINK):
  workbook = load_workbook(wb)
  worksheet = workbook[ws]
  links = []
  for row_id in range(0,len(worksheet[idc])):
    next_row = row_id + ROW_START
    next_link = worksheet.cell(column=target,row=next_row).value
    if isinstance(next_link, str) and len(next_link) > 5:
      links.append(next_link)
  return(links)

def test_write(wb=WORKBOOK_NAME, ws=WORKSHEET_NAME):
  workbook = load_workbook(wb)
  worksheet = workbook[ws]
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
  workbook.save(wb)

def test_requests(headers=HEADERS, link="https://www.sec.gov/Archives/edgar/data/1555280/000155528021000098/zts-20201231.htm"):
  resp = requests.get(link, headers=headers)
  html = resp.text
  soup = BeautifulSoup(html, "html.parser")
  print(soup.body.get_text().strip())

def test_link():
  test_link = SecLink("https://www.sec.gov/ix?doc=/Archives/edgar/data/1555280/000155528021000098/zts-20201231.htm")
  print(f"test_link: {repr(test_link)}")

@sleep_and_retry
@limits(calls=MAX_CALLS_PER_MINUTE, period=ONE_MINUTE)
def access_rate_limited_api(link="https://www.sec.gov/Archives/edgar/data/1555280/000155528021000098/zts-20201231.htm", headers=HEADERS):
  resp = requests.get(link, headers=headers)
  html = resp.text
  soup = BeautifulSoup(html, "html.parser")
  print(soup.body.get_text().strip())

def test_rate_limit():
  count = 0
  for i in range(1000):
    count = access_rate_limited_api("no link", count)
    print(count)

def get_dir_10k_link(page:str) -> str:
  # use beautifulsoup, scan page for link
  pass

if __name__ == "__main__":
  # test_write()
  # test_read()
  # test_requests()
  # test_link()
  # test_requests()
  # test_rate_limit()
  pass
