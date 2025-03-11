from bs4 import BeautifulSoup
import requests

class Scraper:
    def __init__(self):
        self.product_code = input("Enter product code: ")
        self.base_url = f"https://www.ceneo.pl/{self.product_code}/opinie-"
        self.headers = {"User-Agent": "Mozilla/5.0"}

    def fetch_html(self, page_number):
        url = f"{self.base_url}{page_number}"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.text
        else:
            print("Oops! Something went wrong.")
            return None

    def parse_reviews(self, html):
        soup = BeautifulSoup(html, "lxml")
        reviews = []

        for review in soup.find_all("div", class_="user-post user-post__card js_product-review"):
            opinion_id = review["data-entry-id"]
            author = review.find("span", class_="user-post__author-name").text.strip()
            
            recommendation = review.find("span", class_="user-post__author-recommendation")
            recommendation = recommendation.text.strip() if recommendation else "No recommendation"

            stars = review.find("span", class_="user-post__score-count").text.strip()

            content = review.find("div", class_="user-post__text").text.strip()

            pros_section = review.find("div", class_="review-feature__title", string="Zalety")
            pros = [pro.text.strip() for pro in pros_section.find_next_siblings("div")] if pros_section else []

            cons_section = review.find("div", class_="review-feature__title", string="Wady")
            cons = [con.text.strip() for con in cons_section.find_next_siblings("div")] if cons_section else []

            helpful = review.find("button", class_="vote-yes")["data-total-vote"] if review.find("button", class_="vote-yes") else "0"
            unhelpful = review.find("button", class_="vote-no")["data-total-vote"] if review.find("button", class_="vote-no") else "0"

            publish_date = review.find("span", class_="user-post__published").text.strip()
            purchase_date = review.find("span", class_="user-post__published", string="Opinia dodana po zakupie")  
            purchase_date = purchase_date.find_next_sibling("time").text.strip() if purchase_date else "No date"

            reviews.append({
                "Opinion ID": opinion_id,
                "Author": author,
                "Recommendation": recommendation,
                "Stars": stars,
                "Content": content,
                "Advantages": pros,
                "Disadvantages": cons,
                "Helpful": helpful,
                "Unhelpful": unhelpful,
                "Publishing date": publish_date,
                "Purchase date": purchase_date
            })

        return reviews  

    def get_reviews(self, max_pages=5):
        all_reviews = []
        for page_number in range(1, max_pages + 1):
            print(f"Fetching reviews from page {page_number}...")
            html = self.fetch_html(page_number)
            if html:
                reviews = self.parse_reviews(html)
                if reviews:
                    all_reviews.extend(reviews)
                else:
                    print("No reviews found on this page.")
                    break
            else:
                break
        return all_reviews

scraper = Scraper()
opinions = scraper.get_reviews(max_pages=10)  

if opinions:
    for i, opinion in enumerate(opinions, 1):
        print(f"Review {i}:")
        for key, value in opinion.items():
            print(f"{key}: {value}")
        print("-" * 50)
else:
    print("No reviews extracted.")

