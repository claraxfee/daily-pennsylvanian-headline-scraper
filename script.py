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


def scrape_sports():
    """
    Scrapes the sports headlines from The Daily Pennsylvanian home page.

    Returns:
        all_news: A list of sports headline texts if found, otherwise an empty list.
    """
    req = requests.get("https://www.thedp.com/section/news")
    loguru.logger.info(f"Request URL: {req.url}")
    loguru.logger.info(f"Request status code: {req.status_code}")

    all_news = [] #init empty list

    if req.ok:
        soup = bs4.BeautifulSoup(req.text, "html.parser")
        target_elements = soup.find_all("h3", class_="standard-link") #get all divs
        for target_element in target_elements:
            headlineLink = target_element.find("a")
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
        all_news = scrape_sports()
    except Exception as e:
        loguru.logger.error(f"Failed to scrape news headline: {e}")
        all_news = []

    # Save data
    if all_news: 
        for headline in all_news:
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
