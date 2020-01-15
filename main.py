import requests
import bs4
import csv


def SHL_title_searchable(title, user):
    urls = []
    has_link = False
    shl_link = ''
    shortTitle = title.split()[0:3]
    parseTitle = "+".join(shortTitle)
    url_title = 'https://catalogue.libraries.london.ac.uk/search/?searchtype=t&searcharg={}&searchscope=24'.format(parseTitle)
    urls.append(url_title)
    parseUser = user.replace(',', '%2C').split()
    parseAuthor = "+".join(parseUser)
    url_author = 'https://catalogue.libraries.london.ac.uk/search~S24/?searchtype=a&searcharg={}&searchscope=24&sortdropdown=-&SORT=D&extended=0&SUBMIT=Search'.format(parseAuthor) # Uche%2C+Chibuike+Ugochukwu
    urls.append(url_author)
    for url in urls:

        htmlfile = requests.get(url)
        objSoup = bs4.BeautifulSoup(htmlfile.text, 'lxml')

        if htmlfile.status_code == requests.codes.ok:
            theisSet = {}
            print('Response ok')
            isSearchable = objSoup.select('.browseScreen > .msg > td') # if no match, the class of msg will show No matches found; nearby TITLES are:
            
            has_link = len(isSearchable)==0
            if has_link:
                print('found SHL link')
                opacstub = "http://catalogue.libraries.london.ac.uk/record="
                recordid = objSoup.select('#recordnum')
                for r in recordid:
                    rid = r.get('href')
                    rid = rid[8:]
                    print(rid)
                    shl_link = opacstub + rid
                    print('Persistent link for this record: {}'.format(shl_link))
                return has_link, shl_link
            else:
                shl_link = ''
        else:
            print('Response failed')
    if not has_link:
        print('not found SHL link')

    return has_link, shl_link

def thesis_search(year_from, year_to):
    years = range(year_from,year_to+1)
    dataset = []
    for y in years:
        try:
            url = 'http://etheses.lse.ac.uk/view/year/{}.html'.format(y)

            htmlfile = requests.get(url)
            objSoup = bs4.BeautifulSoup(htmlfile.text, 'lxml')

            if htmlfile.status_code == requests.codes.ok:
                print('Response ok')
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
                    hasLink, shl_link = SHL_title_searchable(theisSet['title'],theisSet['author'])
                    print(hasLink, shl_link)
                    print('')
                    theisSet['shl_has_link'] = hasLink
                    theisSet['shl_link'] = shl_link
                    dataset.append(theisSet)

            else:
                print('Response failed')
        except Exception as e:
            print(e)
    
    return dataset

def main():
    
    year_from = 1999
    year_to = 2000

    lse_dataset = thesis_search(year_from,year_to)
    print(lse_dataset)

    keys = lse_dataset[0].keys()
    print(keys)

    with open('theise from {} to {}.csv'.format(year_from, year_to), "w",  encoding='utf-8') as csv_file:
        dict_writer = csv.DictWriter(csv_file, keys, delimiter=',', lineterminator='\n')
        dict_writer.writeheader()
        for line in lse_dataset:
            try:
                print(line)
                dict_writer.writerow(line)
            except Exception as e:
                print(e)

if __name__ == '__main__':
    main()