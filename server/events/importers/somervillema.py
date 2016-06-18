'''
Cornerwise project

Data importer for Somerville's Public Minutes and Agendas. This script extracts
event information for public meetings from Somerville's website. The main page
is http://www.somervillema.gov/government/public-minutes.

Commandline usage:
=====
% python somervillema.py -h


Import usage:
=====
import events.importers.somervillema

# Extract all the current data (from datetime.now() up to the latest posting).
data1 = get_data()

# Get all data from a month ahead and behind the current date (all the entries
# for the default range of dates provided by the main page).
data2 = get_data(current_only=False)

'''

from datetime import datetime
from bs4 import BeautifulSoup
import argparse
import dateutil.parser
import logging
import requests
import json
import time


logger = logging.getLogger(__name__)


def get_date(soup, tr):
    '''
    Get the date of the event, as posted to the left of the link for
    the event.
    '''

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
    '''
    Get the link to the page containing the details for the event.
    '''

    css = ('html > body > center > table > tbody > tr:nth-of-type(2) > '
           'td > table > tbody > tr:nth-of-type(1) > td:nth-of-type(3) > '
           'table > tbody > tr:nth-of-type(2) > td:nth-of-type(1) > div > '
           'div:nth-of-type(3) > * > tbody > tr:nth-of-type({}) > '
           'td:nth-of-type(2) > a'.format(tr))
    link = soup.select(css)[0].attrs['href']
    title = soup.select(css)[0].get_text()
    
    logger.info('get_link returned {}, {}'.format(link, title))
    return link, title


def get_agenda(soup, tr):
    '''
    Get the agenda download link for the event.
    '''

    css = ('html > body > center > table > tbody > tr:nth-of-type(2) > td > '
           'table > tbody > tr:nth-of-type(1) > td:nth-of-type(3) > table > '
           'tbody > tr:nth-of-type(2) > td:nth-of-type(1) > div > '
           'div:nth-of-type(3) > * > tbody > tr:nth-of-type({}) > '
           'td:nth-of-type(3) > a'.format(tr))
    link = soup.select(css)[0].attrs['href']

    logger.info('get_agenda returned {}'.format(link))
    return link


def scrape_page():
    '''
    This is a generator that scrapes the data from each of the links on the main
    page. It returns a single event in dictionary format. Its contents are as
    follows:

        * title
        * date
        * address
        * location (building name, etc)
        * contact_name
        * contact_phone
        * contact_email
        * contact2_name (if there is one)
        * contact2_phone (if there is one)
        * contact2_email (if there is one)
        * agenda_url 
    '''
    
    # Get the contents of the main page.
    base_url = 'http://somervillema.gov/'
    urlpart2 = 'pubmtgs.cfm?'
    urlpart3 = ('js=1&view_name=public_minutes'
                '&view_display_id=page_1&view_path=government%2Fpublic-minutes'
                '&view_base_path=government%2Fpublic-minutes&view_dom_id=1'
                '&pager_element=0&view_args=')
    page = requests.get(base_url + urlpart2 + urlpart3)
    soup = BeautifulSoup(page.content, 'html.parser')

    # 'p' is a counter for main pages, 'a' is a counter for the items on each page.
    p = 0
    a = 1

    # Loop through all the links on the main page (base_url), enter each one,
    # and extract all the data from them. This loop will be broken either when
    # the caller breaks from the generator loop, or when it breaks itself
    # because it reached the end of the last page.
    while True:
        logger.info('DEBUG: Beginning run {}'.format(a))
        
        try:
            # Get the agenda download URL for entry 'a' on the main page.
            agenda_link = get_agenda(soup, a)
            
            # Get the link and title of entry 'a' on the main page.
            link, title = get_link(soup, a)

            # Get the date of entry 'a' on the main page.
            cur_event_date = get_date(soup, a)

        # We've reached the end of a page.
        except IndexError:
            logger.info('DEBUG: Hit the last link on the page, trying next page.')

            p += 1
            page = requests.get(base_url + urlpart2 + 'page={}&'.format(p) +
                                urlpart3)
            soup = BeautifulSoup(page.content, 'html.parser')

            # Restart the iterator, because we're on a new page.
            a = 1

            # Get the agenda link for the first entry of the next page.
            agenda_link = get_agenda(soup, a)
            
            # Get the link and title of the first entry of the next page.
            link, title = get_link(soup, a)

            # Get the date of the first entry on the next page.
            cur_event_date = get_date(soup, a)

            
        # Build the URL for the above link.
        url = base_url + link

        out_dict = {}
        new_page = requests.get(url)
        new_soup = BeautifulSoup(new_page.content, 'html.parser')
            
        out_dict['title'] = title
        
        try:
            event_date = new_soup.select('#page_main > * > b')[0].get_text()
            out_dict['date'] = event_date

        except IndexError:
            event_time = new_soup.select(
                '#page_main > p:nth-of-type(3)')[0].get_text().strip().split()[8:10]
            out_dict['date'] = cur_event_date.strftime( \
                                "%A, %B %d, %Y, {} {}".format(event_time[0],
                                                              event_time[1]))

        # Some pages don't have address info on them.
        try:
            event_addr = new_soup.select('#event_map > a')[0].attrs['href']
            event_loc = new_soup.select('#event_address')[0].get_text('|').split('|')

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

        except:
            out_dict['location'] = ''
            out_dict['address'] = ''
        
        # Pack up the contact information. If there's a second contact entry,
        # pack that too.
        try:
            event_cnt = new_soup.select(
                '#event_contact_wrapper')[0].get_text('|').split('|')        
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

        out_dict['agenda_url'] = agenda_link
        
        yield out_dict

        logger.info('DEBUG: Completed run {}\n'.format(a))

        a += 1
    
        if not args.nosleep:
            time.sleep(1)
        
    return


def get_data(current_only=True):
    '''
    This function builds a dictionary out of the events returned from the
    scrape_page generator. Returns a dictionary with one key ('events') whose
    value is a list of dictionaries (appended from the scrape_page() generator.
    '''

    data = {'events': []}

    # Get the first event in the iteration. If we see this event again, then we
    # need to break out of the loop -- this means we've read all the available
    # pages.
    first = next(x for x in scrape_page())
    found_first = 0
    
    # Run the generator and build the dictionary.
    for event in scrape_page():
        if current_only:
            date = dateutil.parser.parse(event['date'])
            if date < datetime.now():
                logger.info('DEBUG: Found most current entries.')
                logger.info('DEBUG: Exiting.')
                break
        if event == first:
            found_first += 1
            if found_first == 2:
                logger.info('DEBUG: Reached last page, exiting.')
                break

        data['events'].append(event)
        
    return data


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', help='Display debugging information.',
                        action='store_true')
    parser.add_argument('-a', '--all', help='Run through all entries on the '
                        'page. The default action is to scrape only the most '
                        'current events.', action='store_false')
    parser.add_argument('-p', '--prettyprint', help='PrettyPrint the JSON '
                        'dictioanry after the script has run its course.',
                        action='store_true')
    parser.add_argument('-n', '--nosleep', help='Don\'t sleep(1) between each scrape.',
                        action='store_true')
    
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.INFO)

    if args.prettyprint:
        print(json.dumps(get_data(args.all), sort_keys=True, indent=3))
