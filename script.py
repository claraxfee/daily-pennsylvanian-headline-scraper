"""
Scrapes a headline from The Daily Pennsylvanian website and saves it to a 
JSON file that tracks headlines over time.
"""

import os
import sys

import daily_event_monitor

import bs4
import requests
import loguru


def scrape_news():
    """
    Scrapes the news headlines from The Daily Pennsylvanian home page.

    Returns:
        all_news: A list of news headline texts if found, otherwise an empty list.
    """
    req = requests.get("https://www.thedp.com/section/news")
    loguru.logger.info(f"Request URL: {req.url}")
    loguru.logger.info(f"Request status code: {req.status_code}")

    all_news = [] #init empty list

    if req.ok:
        soup = bs4.BeautifulSoup(req.text, "html.parser")
        target_elements = soup.find_all("h3", class_="standard-link") #get all 
        for target_element in target_elements:
            headlineLink = target_element.find("a")
            headline = "" if headlineLink is None else headlineLink.text
            all_news.append(headline)
            loguru.logger.info(f"Data point: {headline}")
    return all_news


def scrap_most_read():
    """
    Scrapes the most read headlines from The Daily Pennsylvanian home page.

    Returns:
        all_most_read: A list of most read headline texts if found, otherwise an empty list.
    """

    req = requests.get("https://www.thedp.com")
    loguru.logger.info(f"Request URL: {req.url}")
    loguru.logger.info(f"Request status code: {req.status_code}")

    all_most_read = [] #init empty list

    if req.ok:
        soup = bs4.BeautifulSoup(req.text, "html.parser")
        target_mostreads = soup.find_all("div", class_="col-sm-5 most-read-item") #get all 
        for target_mostread in target_mostreads:
            headlineLink = target_mostread.find("a", class_= "frontpage-link standard-link")
            headline = "" if headlineLink is None else headlineLink.text
            all_news.append(headline)
            loguru.logger.info(f"Data point: {headline}")
    return all_news


if __name__ == "__main__":

    # Setup logger to track runtime
    loguru.logger.add("scrape.log", rotation="1 day")

    # Create data dir if needed
    loguru.logger.info("Creating data directory if it does not exist")
    try:
        os.makedirs("data", exist_ok=True)
    except Exception as e:
        loguru.logger.error(f"Failed to create data directory: {e}")
        sys.exit(1)

    # Load daily event monitor
    loguru.logger.info("Loading daily event monitor")
    dem = daily_event_monitor.DailyEventMonitor(
        "data/daily_pennsylvanian_headlines.json"
    )

    # Run scrape
    loguru.logger.info("Starting scrape")
    try:
        all_news = scrape_news()
    except Exception as e:
        loguru.logger.error(f"Failed to scrape news headline: {e}")
        all_news = []
    try:
        all_most_read = scrape_most_read()
    except Exception as e:
        loguru.logger.error(f"Failed to scrape most read headline: {e}")
        all_most_read = []

    # Save data
    
    combined = all_most_read + all_news
    for headline in combined:
        if headline in all_most_read and headline in all_news:
            dem.add_today(headline)
        dem.save()
    loguru.logger.info("Saved daily event monitor")

    def print_tree(directory, ignore_dirs=[".git", "__pycache__"]):
        loguru.logger.info(f"Printing tree of files/dirs at {directory}")
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            level = root.replace(directory, "").count(os.sep)
            indent = " " * 4 * (level)
            loguru.logger.info(f"{indent}+--{os.path.basename(root)}/")
            sub_indent = " " * 4 * (level + 1)
            for file in files:
                loguru.logger.info(f"{sub_indent}+--{file}")

    print_tree(os.getcwd())

    loguru.logger.info("Printing contents of data file {}".format(dem.file_path))
    with open(dem.file_path, "r") as f:
        loguru.logger.info(f.read())

    # Finish
    loguru.logger.info("Scrape complete")
    loguru.logger.info("Exiting")
