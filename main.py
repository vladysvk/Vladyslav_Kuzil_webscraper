from bs4 import BeautifulSoup
import requests
import csv
import json

def main():
    display_menu()

class Scraper:
    def __init__(self):
        self.product_code = input("Enter product code: ")
        self.base_url = f"https://www.ceneo.pl/{self.product_code}/opinie-"
        self.headers = {"User-Agent": "Mozilla/5.0"}

    def fetch_html(self, page_number=1):
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

    def page_count(self):
        html_text = self.fetch_html()
        if not html_text:
            return 1  

        soup = BeautifulSoup(html_text, "lxml")
        pagination_links = soup.find_all("a", class_="pagination__item")
        if pagination_links:
            return len(pagination_links)
        return 1

    def get_reviews(self):
        all_reviews = []
        total_pages = self.page_count()
        print(f"Total pages found: {total_pages}")

        for page_number in range(1, total_pages + 1):
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
    
    def save_to_json(self, data):
        filename = f"{self.product_code}_reviews.json"
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        print(f"Data saved to {filename}")

    def save_to_csv(self, data):
        filename = f"{self.product_code}_reviews.csv"
        with open(filename, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        print(f"Data saved to {filename}")


def display_menu():
    while True:
        print("\nCeneo.pl Scraper - Menu")
        print("1. Enter product code and scrape reviews")
        print("2. Exit")
        choice = input("Select an option: ")

        if choice == "1":
            scraper = Scraper()
            opinions = scraper.get_reviews()

            if opinions:
                print("\nExtracted Reviews:")
                for i, opinion in enumerate(opinions, 1):
                    print(f"\nReview {i}:")
                    for key, value in opinion.items():
                        print(f"{key}: {value}")
                    print("-" * 50)

                while True:
                    print("\nSave options:")
                    print("1. Save to JSON")
                    print("2. Save to CSV")
                    print("3. Save to both")
                    print("4. Do not save")
                    save_choice = input("Select an option: ")

                    if save_choice == "1":
                        scraper.save_to_json(opinions)
                        break
                    elif save_choice == "2":
                        scraper.save_to_csv(opinions)
                        break
                    elif save_choice == "3":
                        scraper.save_to_json(opinions)
                        scraper.save_to_csv(opinions)
                        break
                    elif save_choice == "4":
                        break
                    else:
                        print("Invalid choice. Please try again.")

            else:
                print("No reviews extracted.")
        elif choice == "2":
            print("Exiting program. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()


