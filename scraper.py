import logging

import scraper_register
import scraper_accreditations

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    scraper_register.extract()
    scraper_accreditations.extract()
