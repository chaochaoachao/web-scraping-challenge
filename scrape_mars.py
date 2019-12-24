import pandas as pd
from splinter import Browser
from splinter.exceptions import ElementDoesNotExist
from bs4 import BeautifulSoup
import requests
import pymongo
import time
import json


def init_browser():
    executable_path = {"executable_path": "chromedriver.exe"}
    return Browser("chrome", **executable_path, headless=False)

def init_visit_web(url):
    executable_path = {"executable_path":"chromedriver.exe"}
    browser=Browser("chrome", **executable_path, headless=False)
    browser.visit(url)
    # wait for page to be load
    time.sleep(1)
    soup = BeautifulSoup(browser.html, 'lxml')
    return soup

def scrape(db):
    
    # mars news
    url = 'https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest'
    soup=init_visit_web(url)
    result=soup.find('div', class_='list_text')
    news_title=result.find('div', class_='content_title',recursive=True).text
    news_p=result.find('div', class_='article_teaser_body',recursive=True).text

    print(news_title)
    print(news_p)


    # Mars Space Images - Featured Image
    browser=init_browser()
    img_url='https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(img_url)

    browser.click_link_by_id('full_image')
    time.sleep(1)

    # click the button opening details page for the featured image
    browser.click_link_by_partial_text('more info')
    soup = BeautifulSoup(browser.html, 'lxml')

    # Parse HTML with Beautiful Soup
    img_url = soup.find('figure', class_='lede').a['href']
    print(img_url)
    featured_image_url='https://www.jpl.nasa.gov'+ img_url
    print(featured_image_url)


    # Mars Weather
    url = 'https://twitter.com/marswxreport?lang=en'
    soup = init_visit_web(url)
    mars_weather = soup.find('p', class_='TweetTextSize').text
    print(mars_weather)

    # Mars Facts
    url = 'https://space-facts.com/mars/s'
    tables = pd.read_html(url)
    df = tables[0]
    df.columns = ['Parameter', 'Value']
    df.set_index('Parameter',inplace=True)
    mars_facts = df.to_html().replace('\n', '')
    print(mars_facts)

    # Mars Hemispheres
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    soup = init_visit_web(url)    
    #extract links to Mars Hemispehere images
    results=soup.find_all("div", class_="item")

    hemisphere_image_urls = []
    for result in results:
        title = result.find("h3").text
        title = title.replace("Enhanced", "")
        end_url = result.find("a")["href"]
        img_url = "https://astrogeology.usgs.gov" + end_url  
        soup = init_visit_web(img_url)
        image_div = soup.find("div", class_="downloads")
        image_url = image_div.find("a")["href"]
        hemisphere_image_urls.append({"title": title, "img_url": image_url})
    print(hemisphere_image_urls)

    # create a dictionary for img urls
    mars_hemispheres_imgs=json.dumps(hemisphere_image_urls)

    # create a dictionary with all the data collected
    mars_record= {
            'news_title': news_title,
            'news_p': news_p,
            'featured_image_url': featured_image_url,
            'mars_weather': mars_weather,
            'mars_facts': mars_facts,
            'hemisphere_image_urls': mars_hemispheres_imgs
        }

    # Delete previous data and insert new into Mongo DB
    db.items.delete_many({})
    db.items.insert_one(mars_record)
