
[![MIT License](https://img.shields.io/github/license/peter201943/sec-scraper.svg?style=flat)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3670A0?style=flat&logo=python&logoColor=white&label=python%203.10)](https://www.python.org/)
[![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=flat&logo=github&logoColor=white&label=peter201943%2Fsec-scraper)](https://github.com/peter201943/sec-scraper)

# [SEC Scraper](https://github.com/peter201943/sec-scraper)

A simple project to scrape 10-K forms from the US SEC (Securities and Exchange Commission) using spreadsheets and Python.

## Contents
- [Contents](#contents)
- [About](#about)
- [Getting Started](#getting-started)
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
TODO

## Getting Started
1. [Download Python](https://www.python.org/)
2. [Download the project](https://github.com/peter201943/sec-scraper/archive/refs/heads/main.zip)
3. Open a Command Prompt ([Windows](https://www.pcworld.com/article/395081/open-command-prompt-in-windows.html)) ([Mac](https://www.howtogeek.com/682770/how-to-open-the-terminal-on-a-mac/)) in the Folder
4. Install the Requirements
    ```bash
    pip install -r requirements.txt
    ```
5. [Create a `csv` of your Spreadsheet](https://en.wikipedia.org/wiki/Comma-separated_values) (try File > Export on most programs)
6. Edit [`config.py`](config.py) with:
    - the names of spreadsheet columns
    - the names of files
    - the text-search regexes
    - any additional parameters
7. Run `python sec_scrape.py`
8. Find your results in the output file

## Usage
TODO

## Roadmap
See the **[Notes](notes)** folder for current status.
This is not intended to be a long-running project.

## Contributing

### Prerequisites
- [Git for your Operating System](https://git-scm.com/)
- A decent text editor, such as [VS Code](https://code.visualstudio.com/)
- [General Python Knowledge](https://www.youtube.com/watch?v=rfscVS0vtbw)
- [Python Web Scraping](https://www.youtube.com/watch?v=ALizgnSFTwQ)
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
- **[`config.py`](config.py)** handles file system and project variables
- **[`sec_scraper.py`](sec_scraper.py)** handles command-line invocation
- **[`scraper.py`](scraper.py)** handles the actual task of scraping and writing

### Accepting Changes
This is a low-priority project for peter201943 and as such pull requests are not likely to be accepted.
You will be better served by forking it and continuing development of it on your own.

## License
Distributed under the MIT License. See [`LICENSE`](LICENSE) for more information.

## Contact
Peter James Mangelsdorf  
[![Outlook](https://img.shields.io/badge/Microsoft_Outlook-0078D4?style=flat&logo=microsoft-outlook&logoColor=white&label=peter.j.mangelsdorf)](mailto:peter.j.mangelsdorf@outlook.com)  
[![Discord](https://img.shields.io/badge/%3CServer%3E-%237289DA.svg?style=flat&logo=discord&logoColor=white&label=peter201943%238017)](https://discord.com/)  
[![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=flat&logo=github&logoColor=white&label=peter201943)](https://github.com/peter201943/)  

## Acknowledgements
See **[Notes](notes/)** for links to articles, repositories, and programs.
