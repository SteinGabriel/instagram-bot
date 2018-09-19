import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException


class InstagramBot:

    def __init__(self, username, password, target_profile, num_to_follow):
        self.username = username
        self.password = password
        self.target_profile = target_profile
        self.num_to_follow = num_to_follow
        self.driver = webdriver.Chrome()
        self.min_posts_to_follow = 60
        self.min_profile_followers_to_follow = 350
        self.profiles_followed = 0
        self.profiles_accessed = 0

    def run(self):
        self.setup()
        self.login()
        time.sleep(1)
        self.access_page(self.target_profile)
        time.sleep(1)
        self.find_followers(self.num_to_follow)
        self.follow()
        self.report()
        # self.closeBrowser()

    def setup(self):
        driver = self.driver
        driver.get('https://www.instagram.com/')

    def closeBrowser(self):
        self.driver.close()

    def login(self):
        driver = self.driver
        # click the login button in order to navigate to login page
        login_button = driver.find_element_by_xpath(
            "//a[@href='/accounts/login/?source=auth_switcher']")
        login_button.click()
        time.sleep(2)

        # username login input
        user_input = driver.find_element_by_name('username')
        user_input.clear()
        user_input.send_keys(self.username)

        # password login input
        password_input = driver.find_element_by_name('password')
        password_input.clear()
        password_input.send_keys(self.password)

        # perform login
        password_input.send_keys(Keys.RETURN)

    def access_page(self, target_profile):
        driver = self.driver
        driver.get('https://www.instagram.com/' + target_profile)
        time.sleep(1)

    def find_followers(self, numOfFollowers):
        print("Finding followers...")
        driver = self.driver
        target_profile = self.target_profile
        # finds and click at followers button
        followers_button = driver.find_element_by_xpath(
            "//a[@href='/" + target_profile + "/followers/']")
        followers_button.click()
        time.sleep(1)

        # creates array with each follower item
        followers_items = []
        while (len(followers_items) < numOfFollowers):
            frame = driver.find_element_by_class_name('j6cq2')
            driver.execute_script(
                'arguments[0].scrollTop = arguments[0].scrollHeight', frame)
            followers_items = driver.find_elements_by_xpath(
                "//li[contains(.,'Follow')]")

        # Finds all link elements and creates an array with the profile name
        # exctracted from the title attribute of the link elements
        linkElements = driver.find_elements_by_tag_name('a')
        followers_urls = []
        for elem in linkElements:
            if elem.get_attribute("title") != '':
                followers_urls.append(elem.get_attribute("title"))

        self.followers_urls = followers_urls

    def follow(self):
        followers = self.followers_urls
        num_to_follow = self.num_to_follow
        driver = self.driver

        # access the follower profile page
        # finds the follow button and click it
        for i in range(0, num_to_follow):
            self.profiles_accessed += 1
            self.access_page(followers[i])

            print('profile ' + str(self.profiles_accessed) +
                  "/" + str(self.num_to_follow))

            try:
                button = driver.find_element_by_xpath(
                    "//button[contains(.,'Follow')]")
                if self.should_follow():
                    self.profiles_followed += 1
                    button.click()
                time.sleep(1)
            except NoSuchElementException as identifier:
                print('NoSuchElementException!')
                pass

    def should_follow(self):
        should = True
        if self.is_private():
            should = False

        if self.is_active() == False:
            should = False

        if self.is_followed():
            should = False

        return should

    def is_private(self):
        driver = self.driver
        h2_elements = driver.find_elements_by_tag_name('h2')

        return len(h2_elements) == 1

    def is_active(self):
        active = True
        min_posts = self.min_posts_to_follow
        # min_followers = self.min_profile_followers_to_follow
        driver = self.driver

        spans = driver.find_elements_by_tag_name("span")

        self.num_posts = 0
        self.num_followers = 0
        for span in spans:
            if len(span.text.split(" ")) >= 2:

                if span.text.split(" ")[1] == "posts":
                    self.num_posts = int(span.text.split(" ")[
                                         0].replace(',', ''))

        if self.num_posts < min_posts:
            active = False

        return active

    def is_followed(self):
        driver = self.driver

        buttons = driver.find_elements_by_xpath(
            "//button[contains(.,'Following')]")

        return len(buttons) == 1

    def report(self):
        print(" ")
        print("=== FINISHED ===")
        print(" ")
        print(str(self.profiles_accessed) + " profiles accessed.")
        print(str(self.profiles_followed) + " profiles followed.")
