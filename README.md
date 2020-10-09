# FixFake-Tech-Challenage

## Environment
To run this project you need:
 - Python 3.7.6
 - ChromeDriver installed(to run get_image_urls())


## Functions
1. **get_image_urls(number_of_images)**: webscrape google images using the query "fake" and get the urls
2. **link2db(image_urls)**: save the urls into database
3. **read_links_from_db(db_paht="db/images_link.db")**: to reduce the time of obtaining the data from web-scraping, this function is used to directly read the saved links from database
4. **image2db(image_urls, file_save_dir="images/")**: to download the image from url and to save the image info to database

## Performance
The time for running this program without webscraping is around 20 seconds. It will take longer if web-scraping function is included.
