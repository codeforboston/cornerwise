'''
Cornerwise project

Data importer for Somerville's Public Minutes and Agendas. This script extracts
event information for public meetings from Somerville's website.

Usage:

import events.importers.somervillema
print(json.dumps(somervillema.get_data(), sort_keys=True, indent=4))
'''

from datetime import datetime
from bs4 import BeautifulSoup
import logging
import requests
import json
import time

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def get_date(soup, tr):
    '''Get the date that the event was posted on the page.'''

    css = ('html > body > center > table > tbody > tr:nth-of-type(2) > '
           'td > table > tbody > tr:nth-of-type(1) > td:nth-of-type(3) > '
           'table > tbody > tr:nth-of-type(2) > td:nth-of-type(1) > div > '
           'div:nth-of-type(3) > * > tbody > tr:nth-of-type({}) > '
           'td:nth-of-type(1) > span'.format(tr))
    date = soup.select(css)[0].get_text()
    date_ret = datetime.strptime(str(date), "%b %d, %Y")

    logger.info('get_date returned {}'.format(date))
    return date_ret


def get_link(soup, tr):
    '''Get the link to the page containing the details for the event.'''
    
    css = ('html > body > center > table > tbody > tr:nth-of-type(2) > '
           'td > table > tbody > tr:nth-of-type(1) > td:nth-of-type(3) > '
           'table > tbody > tr:nth-of-type(2) > td:nth-of-type(1) > div > '
           'div:nth-of-type(3) > * > tbody > tr:nth-of-type({}) > '
           'td:nth-of-type(2) > a'.format(tr))
    link = soup.select(css)[0].attrs['href']
    title = soup.select(css)[0].get_text()
    
    logger.info('get_link returned {}, {}'.format(link, title))
    return link, title


def scrape_page(url, title, parent_event_date):
    '''Scrape the data from the event detail page.'''

    out_dict = {}
    new_page = requests.get(url)
    new_soup = BeautifulSoup(new_page.content, 'html.parser')
    event_addr = new_soup.select('#event_map > a')[0].attrs['href']
    event_loc = new_soup.select('#event_address')[0].get_text('|').split('|')

    out_dict['title'] = title
    
    try:
        event_date = new_soup.select('#page_main > * > b')[0].get_text()
        out_dict['date'] = event_date

    except IndexError:
        event_time = new_soup.select('#page_main > p:nth-of-type(3)')[0].get_text().strip().split()[8:10]
        out_dict['date'] = parent_event_date.strftime( \
                            "%A, %B %d, %Y, {} {}".format(event_time[0],
                                                          event_time[1]))

    # This pulls the first text item under 'location' and strips it
    # of whitespace characters.
    tmploc = [event_loc[i].strip() for i in range(len(event_loc)) \
              if event_loc[i].strip() != '']
    out_dict['location'] = tmploc[1]
    
    # This gets the address from the google maps url in the href that's
    # attached to the map icon on the page.
    out_dict['address'] = event_addr[event_addr.find('&q=')+3:]

    # Some pages have limited information, and will result in these two
    # keys having the same value. This clears out one of them.
    if out_dict['location'] == out_dict['address']: out_dict['address'] = ''
    
    try:
        event_cnt = new_soup.select('#event_contact_wrapper')[0].get_text('|').split('|')        
        tmpcnt = [event_cnt[i].strip() for i in range(len(event_cnt)) \
                   if event_cnt[i].strip() != '']

        out_dict['contact_name'] = tmpcnt[1]
        out_dict['contact_phone'] = tmpcnt[2]
        out_dict['contact_email'] = tmpcnt[3]

        try:
            if len(tmpcnt) > 3:
                out_dict['contact2_name'] = tmpcnt[4]
                out_dict['contact2_phone'] = tmpcnt[5]
                out_dict['contact2_email'] = tmpcnt[6]

        except IndexError:
            pass

    except IndexError:
        out_dict['contact_name'] = ''
        out_dict['contact_phone'] = ''
        out_dict['contact_email'] = ''
    
    return out_dict


def get_data(current_only=False):
    '''Run through all the upcoming events, and scrape each page.
    Return the raw data.'''

    base_url = 'http://somervillema.gov'
    page = requests.get(base_url + '/government/public-minutes')
    soup = BeautifulSoup(page.content, 'html.parser')

    data = {'events': []}
    a = 1
    event_date = get_date(soup, a)
    
    while event_date > datetime.now():
        link, title = get_link(soup, a)
        new_url = base_url + link

        logger.info('new_url={}'.format(new_url))
        data['events'].append(scrape_page(new_url, title, event_date))
        logger.info('Run #{} complete.'.format(a))

        a += 1
        event_date = get_date(soup, a)
        
        time.sleep(1)

    return data


if __name__ == '__main__':
    print json.dumps(get_data(), sort_keys=True, indent=3)

    
