# import libraries
import selenium
from selenium import webdriver
import time
import datetime
import sqlite3
from skimage import io
import requests

def get_image_urls(number_of_images):
    """
    This function extracts 100 images from google image search of 'fake'
    To run this function, you need to download suitable version of ChromeDriver from https://chromedriver.chromium.org/downloads
    and to modify the executable_path
    The function is refered from https://medium.com/@wwwanandsuresh/web-scraping-images-from-google-9084545808a2
    """    
    wd = webdriver.Chrome(executable_path="/Users/Tutu/Desktop/Chromedriver")
    search_url = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img"
    wd.get(search_url.format(q="fake"))

    image_urls = set()
    image_count = 0
    results_start = 0
    def scroll_to_end(wd):
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)  
        
    while image_count < number_of_images:

        image_results = wd.find_elements_by_css_selector("img.Q4LuWd")
        number_results = len(image_results)
        
        for img in image_results[results_start:number_results]:
            
            try:
                img.click()
                time.sleep(1)
            except Exception:
                continue

            # extract image urls    
            actual_images = wd.find_elements_by_css_selector('img.n3VNCb')
            for actual_image in actual_images:
                if actual_image.get_attribute('src') and 'http' in actual_image.get_attribute('src'):
                    image_urls.add(actual_image.get_attribute('src'))

            image_count = len(image_urls)

        if len(image_urls) >= number_of_images:
            print(f"Found: {len(image_urls)} image links, done!")
            break
        else:
            print("Found:", len(image_urls), "image links, looking for more ...")
            time.sleep(30)

            load_more_button = wd.find_element_by_css_selector(".mye4qd")
            if load_more_button:
                wd.execute_script("document.querySelector('.mye4qd').click();")

        # move the result startpoint further down
        results_start = len(image_results)
    
    wd.quit()
    return list(image_urls)
    
def link2db(image_urls):
    """ 
    This function save image links into a database with a table named images_link
    """
    conn = None
    try:
        conn = sqlite3.connect("db/images_link.db")
        
        # create the table
        try:
            conn.execute('''CREATE TABLE IMAGES_LINK (image_url TEXT PRIMARY KEY NOT NULL);''')
            print("-----successfully created the table-----")
        except:
            print("-----the table already exists-----")
            pass
        
        # insert the data into database one by one
        cursor = conn.cursor()
        insert_query = """INSERT INTO IMAGES_LINK (image_url) VALUES(?);"""
        cursor.executemany(insert_query, list(zip(image_links)))
        print("-----successfully inserted the data-----")

            
        conn.commit()
        
    except sqlite3.Error as e:
        print(e)
    
    if conn:
        conn.close()


def read_links_from_db(db_path="db/images_link.db"):
    """
    This function read the image links from the database
    """
    
    conn = sqlite3.connect(db_path)
    image_links = conn.cursor().execute("SELECT * FROM IMAGES_LINK").fetchall()
    
    conn.close()
    
    return [i[0] for i in image_links]
    
def image2db(image_urls, file_save_dir="images/"):
    """
    This function download the images from urls and save the info to database
    """

    
    def delete_url(url):
        """
        This function delete some url that is not able to download a complete image
        """
        conn = sqlite3.connect("db/images_link.db")
        c = conn.cursor()
        c.execute("""DELETE FROM IMAGES_LINK WHERE image_url=? """, (url, ))
        conn.commit()
        conn.close()
        

    conn = sqlite3.connect("db/images_info.db")
    
    try:
        conn.execute('''CREATE TABLE IMAGES_INFO
                 (image_name TEXT PRIMARY KEY NOT NULL,
                 image_url NONE,
                 image_shape_width INT,
                 image_shape_height INT,
                 image_shape_channel INT,
                 download_datetime TEXT,
                 image_location TEXT);''')
        
        print("-----successfully created the table-----")
        
    except:
        print("-----the table already exists-----")
        pass
    
    cursor = conn.cursor()
    insert_query = """INSERT INTO IMAGES_INFO (image_name, image_url, 
                    image_shape_width, image_shape_height, image_shape_channel, 
                    download_datetime, image_location) VALUES(?, ?, ?, ?, ?, ?, ?);"""
    
    for i in range(len(image_urls)):
        image_url = image_urls[i]
        image_name = 'image_' + str(i) + '.jpg'
        image_location = file_save_dir + image_name
        download_datetime = datetime.datetime.now().strftime("%Y-%m-%d")
        # download image 
        with open(image_location, 'wb') as handler:
            image_data = requests.get(image_url).content
            handler.write(image_data)
        try:
            image = io.imread(image_location)
        except:
            print(image_url, ' download failed')
            delete_url(image_url)
            pass
        
        if len(image.shape) ==3:
            image_shape_w, image_shape_h, image_shape_c = image.shape
        else:
            image_shape_w, image_shape_h = image.shape
            image_shape_c = 1
        
        
        
        info = (image_name, image_url, image_shape_w, image_shape_h, image_shape_c, 
                                          download_datetime, image_location)
        

        
        # write the image info into database
        try:
            cursor.execute(insert_query, info)
        except sqlite3.Error as e:
            print("-----" + image_name + " fails to be saved-----")
            print(e)
    
    conn.commit()
    
    conn.close()
    
if __name__ == "__main__":
    start = time.time()
    # web scrape 100 images from google
#     image_links = get_image_urls(100)
    # obtain the links from database
    image_links = read_links_from_db()
    # save the links to database
    link2db(image_links)
    image2db(image_links, "images/")
    print("the program takes overall ", time.time() - start, ' seconds')