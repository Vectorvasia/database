import os
from lxml import etree
import lxml.etree as ET


def task1():
    os.system('scrapy crawl uahotels')
    root = None
    with open('results/uahotels.xml', 'r', encoding='utf-8') as file:
        root = etree.parse(file)

    pagesCount = root.xpath('count(//page)')
    textFragmentsCount = root.xpath('count(//fragment[@type="text"])')
    print('Average count of text fragments per page %f' % (textFragmentsCount / pagesCount))


def task2():
    crawl()
    xslt_parse()


def crawl():
    try:
        os.remove('results/zvetsad.xml')
    except OSError:
        print('results/zvetsad.xml not found')
    os.system('scrapy crawl zvetsad -o results/zvetsad.xml -t xml')


def xslt_parse():
    dom = ET.parse('results/zvetsad.xml')
    xslt = ET.parse('zvetsad.xslt')
    transform = ET.XSLT(xslt)
    newdom = transform(dom)
    with open('results/zvetsad.html', 'wb') as f:
        f.write(ET.tostring(newdom, pretty_print=True))
    print('results/zvetsad.html was created')


task1()
#task2()
