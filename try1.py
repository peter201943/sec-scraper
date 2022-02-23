
import csv
from pathlib          import Path
from openpyxl         import load_workbook
from openpyxl.styles  import Alignment

original_path = "input.csv"
dirlinks_path = "temp/dirlinks.csv"
doclinks_path = "temp/doclinks.csv"
stats_path    = "temp/stats.csv"
final_path    = "temp/final.xlsx"

Path("temp").mkdir(parents=True, exist_ok=True)
Path("temp/pages_full").mkdir(parents=True, exist_ok=True)
Path("temp/pages_bare").mkdir(parents=True, exist_ok=True)

workbook_page_name  = "export"
column_sec_link     = 9
column_10k_link     = 11
column_d_wordcount  = 12
column_d_sentences  = 13

def safe_read(original_path):
  with open(original_path, 'r') as original_csv:
    reader = csv.DictReader(original_csv)
    for row in reader:
      yield(row)

def dirlinks_write(dirlinks_path):
  with open(dirlinks_path, 'w', newline='', encoding='utf-8') as dirlinks_csv:
    csvwriter = csv.writer(dirlinks_csv)
    csvwriter.writerow(["row_id","dir_link"])
    for idx, row in enumerate(safe_read(original_path)):
      print(f"row_id: {idx+2}, dir_link: {repr(row['sec_link'])}")
      csvwriter.writerow([idx+2,row['sec_link']])

def test_final_read(final_path, runs_for_m_cells=9000, stops_after_n_blanks=5):
  global column_sec_link
  workbook = load_workbook(final_path)
  worksheet = workbook[workbook_page_name]
  links = []
  empties = 0
  input(f"length of `cnt`: {len(worksheet['A'])}")
  for row_id in range(0,runs_for_m_cells):
    next_row = row_id + 2
    next_link = worksheet.cell(column=column_sec_link,row=next_row).value
    if isinstance(next_link, str) and len(next_link) > 5:
      links.append(next_link)
      empties = 0
    else:
      empties += 1
      if empties > stops_after_n_blanks:
        return(links)
  return(links)

def test_final_write(final_path):
  global workbook_page_name
  workbook = load_workbook(final_path)
  worksheet = workbook[workbook_page_name]
  for row in safe_read(stats_path):
    try:
      worksheet.cell(
        column  = 11, 
        row     = int(row['row_id']), 
        value   = "i can haz cheezburgr\ncat_salad_outrage.jpeg"
      ).alignment = Alignment(wrapText=True)
    except Exception as e:
      workbook.save(final_path)
      raise e
  workbook.save(final_path)

def doclinks_find():
  pass

if __name__ == "__main__":
  # dirlinks_write(dirlinks_path)
  # test_final_write(final_path)
  test_final_read(final_path)
  pass