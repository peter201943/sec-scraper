
import csv
from pathlib import Path
from openpyxl import load_workbook

original_path = "input.csv"
dirlinks_path = "temp/dirlinks.csv"
doclinks_path = "temp/doclinks.csv"
stats_path    = "temp/stats.csv"

Path("temp").mkdir(parents=True, exist_ok=True)
Path("temp/pages_full").mkdir(parents=True, exist_ok=True)
Path("temp/pages_bare").mkdir(parents=True, exist_ok=True)

def original_read(original_path):
  with open(original_path, 'r') as original_csv:
    reader = csv.DictReader(original_csv)
    for row in reader:
      yield(row)

def dirlinks_write(dirlinks_path):
  with open(dirlinks_path, 'w', newline='', encoding='utf-8') as dirlinks_csv:
    csvwriter = csv.writer(dirlinks_csv)
    csvwriter.writerow(["row_id","dir_link"])
    for idx, row in enumerate(original_read(original_path)):
      print(f"row_id: {idx+2}, dir_link: {repr(row['sec_link'])}")
      csvwriter.writerow([idx+2,row['sec_link']])

def doclinks_find():
  pass

if __name__ == "__main__":
  dirlinks_write(dirlinks_path)
