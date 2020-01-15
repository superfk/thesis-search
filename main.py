import requests
import bs4
import csv


def SHL_title_searchable(title):
    has_link = False
    shortTitle = title.split()[0:4]
    parseTitle = "+".join(shortTitle)
    url = 'https://catalogue.libraries.london.ac.uk/search/?searchtype=t&searcharg={}&searchscope=24'.format(parseTitle)
    htmlfile = requests.get(url)
    objSoup = bs4.BeautifulSoup(htmlfile.text, 'lxml')

    if htmlfile.status_code == requests.codes.ok:
        theisSet = {}
        print('Response ok')
        print('')
        isSearchable = objSoup.select('.browseScreen > .msg > td') # if no match, the class of msg will show No matches found; nearby TITLES are:
        has_link = len(isSearchable)==0
        if has_link:
            print('found SHL link')
        else:
            print('not found SHL link')
        return has_link

    else:
        print('Response failed')
        return has_link

def thesis_search(year_from, year_to):
    years = range(year_from,year_to+1)
    dataset = []
    for y in years:
        url = 'http://etheses.lse.ac.uk/view/year/{}.html'.format(y)

        htmlfile = requests.get(url)
        objSoup = bs4.BeautifulSoup(htmlfile.text, 'lxml')

        if htmlfile.status_code == requests.codes.ok:
            print('Response ok')
            print('')
            print('Start Search {} year'.format(y))
            personNames = objSoup.select('.ep_view_page_view_year > p > .person_name')
            theiesLinks = objSoup.select(".ep_view_page_view_year > p > a[href]")
            theiesNames = objSoup.select(".ep_view_page_view_year > p > a > em")
            for name,link, tName in zip(personNames,theiesLinks,theiesNames):
                theisSet = {}
                print(name.getText(), ' ', link.get('href'), " ", tName.getText())
                theisSet['year'] = y
                theisSet['author'] = name.getText()
                theisSet['title'] = tName.getText()
                theisSet['link'] = link.get('href')
                theisSet['shl_has_link'] = SHL_title_searchable(theisSet['title'])
                dataset.append(theisSet)

        else:
            print('Response failed')
    
    return dataset

def main():
    
    year_from = 1980
    year_to = 1990

    lse_dataset = thesis_search(year_from,year_to)

    keys = lse_dataset[0].keys()
    with open('theise from {} to {}.csv'.format(year_from, year_to), 'w') as output_file:
        dict_writer = csv.DictWriter(output_file, keys, lineterminator='\n')
        dict_writer.writeheader()
        dict_writer.writerows(lse_dataset)

if __name__ == '__main__':
    main()