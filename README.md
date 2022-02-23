
[![MIT License](https://img.shields.io/github/license/peter201943/sec-scraper.svg?style=flat)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3670A0?style=flat&logo=python&logoColor=white&label=python%203.10)](https://www.python.org/)
[![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=flat&logo=github&logoColor=white&label=peter201943%2Fsec-scraper)](https://github.com/peter201943/sec-scraper)

# [SEC Scraper](https://github.com/peter201943/sec-scraper)

A simple project to scrape 10-K forms from the US SEC (Securities and Exchange Commission) using spreadsheets and Python.

## Contents
- [Contents](#contents)
- [About](#about)
- [Usage](#usage)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Major Files](#major-files)
  - [Accepting Changes](#accepting-changes)
- [License](#license)
- [Contact](#contact)
  - [Primary Maintainer](#primary-maintainer)
  - [Project](#project)
- [Acknowledgements](#acknowledgements)

## About
A simple scraper for some simple statistics gathering on US SEC 10-K forms.
Coded very poorly, and in need of script cleanup.

## Usage
1. Download a decent text editor, such as [VS Code](https://code.visualstudio.com/)
2. [Download Python](https://www.python.org/)
3. [Download the project](https://github.com/peter201943/sec-scraper/archive/refs/heads/main.zip)
4. Open a Command Prompt ([Windows](https://www.pcworld.com/article/395081/open-command-prompt-in-windows.html)) ([Mac](https://www.howtogeek.com/682770/how-to-open-the-terminal-on-a-mac/)) in the Folder
5. Install the Requirements
    ```bash
    pip install -r requirements.txt
    ```
6. Copy your input file (Excel Workbook) into the same directory as the script
7. Edit [`sec_scraper.py`](sec_scraper.py) with:
    - the numbers of spreadsheet columns
    - the names of files
    - the text-search regexes
    - any additional parameters
8. Create a `secrets.json` with the following contents:
    ```json
    {
        "sec_request_headers":
        {
            "User-Agent":       "YOUR INSTITUTION, YOUR EMAIL",
            "Accept-Encoding":  "gzip, deflate",
            "Host":             "www.sec.gov"
        }
    }
    ```
9. Run the script
    ```bash
    python sec_scrape.py
    ```
10. Find your results in the original file

## Roadmap
- See the **[Notes](notes)** folder for current status.  
  This is not intended to be a long-running project.  
- Significantly better documentation of the code needed
- Significantly better breakdown of code into smaller functions needed
- Still very buggy/many edge cases not addressed

## Contributing

### Prerequisites
- [Download Git for your Operating System](https://git-scm.com/)
- [General Python Knowledge](https://www.youtube.com/watch?v=rfscVS0vtbw)
- [How to Web Scrape the SEC | Part 1](https://www.youtube.com/watch?v=-7I7OAC6ih8)
- [Python Regexes](https://www.youtube.com/watch?v=K8L6KVGG-7o)

### Installation
1. Clone the Repository
    ```bash
    git clone git@github.com:peter201943/sec-scraper.git
    ```
2. Open the Folder
    ```bash
    cd sec-scraper
    ```
3. Create a [Virtual Environment](https://dev.to/bowmanjd/python-tools-for-managing-virtual-environments-3bko)
4. Install the Requirements
    ```bash
    pip install -r requirements.txt
    ```
5. Open the Project (with VS Code, as example)
    ```bash
    code .
    ```

### Major Files
- **[`sec_scraper.py`](sec_scraper.py)** Configuration, definition, etcetera. The meat of the project.
- **[`tests.py`](tests.py)** Small incremental steps to learn how each part works.

### Accepting Changes
This is a low-priority project for peter201943 and as such pull requests are not likely to be accepted.
You will be better served by forking it and continuing development of it on your own.

## License
Code distributed under the [MIT License](https://opensource.org/licenses/MIT). See [`LICENSE`](LICENSE) for more information.

Documentation distributed under the [Creative Commons Attribution 4.0 License](https://creativecommons.org/licenses/by/4.0/).

This document released under [Creative Commons Attribution 4.0 License](https://creativecommons.org/licenses/by/4.0/) by Peter J. Mangelsdorf.

## Contact
Peter James Mangelsdorf  
[![Outlook](https://img.shields.io/badge/Microsoft_Outlook-0078D4?style=flat&logo=microsoft-outlook&logoColor=white&label=peter.j.mangelsdorf)](mailto:peter.j.mangelsdorf@outlook.com)  
[![Discord](https://img.shields.io/badge/%3CServer%3E-%237289DA.svg?style=flat&logo=discord&logoColor=white&label=peter201943%238017)](https://discord.com/)  
[![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=flat&logo=github&logoColor=white&label=peter201943)](https://github.com/peter201943/)  

## Acknowledgements
See **[Notes](notes/)** for links to articles, repositories, and programs.
