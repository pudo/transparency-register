import logging

import scraper_accreditations

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    scraper_accreditations.extract()
