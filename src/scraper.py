import requests
from bs4 import BeautifulSoup


class Scraper:
    def __init__(self, url: str) -> None:
        """
        Initialize the Scraper with a given URL.

        Parameters:
        - url (str): The URL of the webpage to scrape.
        """
        self.url = url

    def clean_table_rows(self, row):
        """
        Clean up HTML tags and attributes in a table row.

        Parameters:
        - row: BeautifulSoup Tag representing a table row.

        Returns:
        - row: Cleaned BeautifulSoup Tag.
        """
        for unwanted_tag in ["span", "a", "div", "link", "style", "i", "b", "sup"]:
            for unwanted in row.find_all(unwanted_tag):
                unwanted.unwrap()  # removing the unwanted tags
        row.attrs = {}  # cleaning out the attributes
        return row

    def get_table(self):
        """
        Scrape and clean the table rows from the specified URL.

        Returns:
        - list: List of cleaned BeautifulSoup Tags representing table rows.
        """
        response = requests.get(self.url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "lxml")
            tables = soup.find("table")
            if tables:
                cleaned_rows = []
                rows = tables.find_all("tr")
                for row in rows:
                    cleaned = self.clean_table_rows(row)
                    cleaned_rows.append(cleaned)

                return cleaned_rows
        return []
