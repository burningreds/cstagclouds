import sys

import scrapy
from scrapy.crawler import CrawlerProcess

#from extractpapers.spiders.papers_dynamic_spider import PapersDynamicSpider
#from extractpapers.spiders.papers_spider import PapersSpider
#from getlinks import get_links
from extractpapers.spiders.papers_dynamic_spider import PapersDynamicSpider
from extractpapers.spiders.papers_spider import PapersSpider
from getlinks import get_links


def main(argv):
    name = str(argv).split('/')[-1]
    print (name)
    results = get_links.get_papers_links(name)

    user_agent = 'Prios (prios@dcc.uchile.cl)'

    process = CrawlerProcess({
        'USER_AGENT': user_agent
    })

    for result in results:
        try:
            process.crawl(PapersSpider(url=result,name=name),
                          url=result,
                          name=name)
            print(result)
        except scrapy.exceptions.NotSupported:
            process.crawl(PapersDynamicSpider(url=result, name=name),
                          url=result,
                          name=name)
            print(result)
    process.start()


if __name__ == "__main__":
    main(sys.argv[1])