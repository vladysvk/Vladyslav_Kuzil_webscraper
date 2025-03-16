from flask import Flask, render_template, request, redirect, url_for
from product import Product
from opinion import Opinion
import os
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import requests
import csv
import json
from bs4 import BeautifulSoup

app = Flask(__name__)
"""
class Product:
    def __init__(self, product_code = None, name = None, price = None, opinions = None):
        self.product_code = product_code
        self.name = name
        self.price = price
        self.opinions = opinions if opinions else []

    def add_opinion(self, opinion):
        self.opinions.append(opinion)

    def average_rating(self):
        total_stars = 0
        for opinion in self.opinions:
            total_stars += opinion.stars
        return total_stars / len(self.opinions) if self.opinions else 0


class Opinion:
    def __init__(self, opinion_id, author, recommendation, stars, content, pros=None, cons=None, helpful_count=None, unhelpful_count=None, publish_date=None, purchase_date=None):
        self.opinion_id = opinion_id
        self.author = author
        self.recommendation = recommendation
        self.stars = stars
        self.content = content
        self.pros = pros or []
        self.cons = cons or []
        self.helpful_count = helpful_count or 0
        self.unhelpful_count = unhelpful_count or 0
        self.publish_date = publish_date
        self.purchase_date = purchase_date

"""
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/product', methods=['GET', 'POST'])
def product():
    if request.method == 'POST':
        product_code = request.form['product_code']
        scraper = Scraper(product_code)
        opinions = scraper.get_reviews()
        html = scraper.fetch_html()
        product_name, product_price = scraper.parse_product_details(html)
        
        
        
        product = Product(product_code, product_name, product_price)

        for opinion in opinions:
            product.add_opinion(Opinion(
            opinion_id=opinion['Opinion ID'],  
            author=opinion['Author'],
            recommendation=opinion['Recommendation'],
            stars=float(opinion['Stars'].split('/')[0].strip().replace(',', '.')),  # Fix for comma in rating            content=opinion['Content'],
            content=opinion['Content'],  
            pros=opinion['Advantages'],
            cons=opinion['Disadvantages'],
            helpful_count=int(opinion['Helpful']),  
            unhelpful_count=int(opinion['Unhelpful']),  
            publish_date=opinion['Publishing date'],
            purchase_date=opinion['Purchase date']
        ))
        return render_template('product.html', product=product, price = product_price)

    return render_template('product_form.html')

@app.route('/statistics/<product_code>')
def statistics(product_code):
    scraper = Scraper(product_code)
    opinions = scraper.get_reviews()
    ratings = [int(opinion['Stars'].split('/')[0].strip()) for opinion in opinions]
    rating_counter = Counter(ratings)
    plt.figure(figsize=(6, 4))
    sns.barplot(x=list(rating_counter.keys()), y=list(rating_counter.values()))
    plt.title(f"Rating distribution for product {product_code}")
    plt.xlabel('Stars')
    plt.ylabel('Number of Opinions')

    graph_path = f"static/{product_code}_ratings.png"
    plt.savefig(graph_path)
    plt.close()

    return render_template('statistics.html', product_code=product_code, graph_path=graph_path)

class Scraper:
    def __init__(self, product_code):
        self.product_code = product_code
        self.base_url = f"https://www.ceneo.pl/{self.product_code}/opinie-" if product_code else ""
        self.headers = {"User-Agent": "Mozilla/5.0"}

    def fetch_html(self, page_number=1):
        url = f"{self.base_url}{page_number}"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.text
        else:
            print("Oops! Something went wrong.")
            return None
   
    def parse_product_details(self, html):
        soup = BeautifulSoup(html, "lxml")
            
    
        name = soup.find("h1", class_="product-top__product-info__name js_product-h1-link js_product-force-scroll js_searchInGoogleTooltip default-cursor")
        product_name = name.text.strip() if name else "No name found"

            
        price = soup.find("span", class_="price")
        product_price = price.text.strip() if price else "No price found"

        return product_name, product_price

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
        os.makedirs("data", exist_ok=True)  
        filename = os.path.join("data", f"{self.product_code}_reviews.json")
        
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        
        print(f"Data saved to {filename}")

    def save_to_csv(self, data):
        os.makedirs("data", exist_ok=True)  
        filename = os.path.join("data", f"{self.product_code}_reviews.csv")

        with open(filename, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        
        print(f"Data saved to {filename}")


    def average_rating(self, reviews):
        total_stars = 0
        valid_reviews = 0

        for review in reviews:
            stars = review['Stars'].strip()
        
           
            if '/' in stars:
                try:
                    numerator = int(stars.split('/')[0].strip())
                    total_stars += numerator
                    valid_reviews += 1
                except ValueError:
                    continue
            else:
                try:
                    total_stars += float(stars.replace(',', '.'))
                    valid_reviews += 1
                except ValueError:
                    continue

        return total_stars / valid_reviews if valid_reviews else 0


    def recommendation_stats(self, reviews):
        positive = sum([1 for review in reviews if "Polecam" in review["Recommendation"]])
        negative = len(reviews) - positive
        return positive, negative

    def vote_stats(self, reviews):
        helpful_votes = [int(review["Helpful"]) for review in reviews]
        unhelpful_votes = [int(review["Unhelpful"]) for review in reviews]
        avg_helpful = sum(helpful_votes) / len(helpful_votes) if helpful_votes else 0
        avg_unhelpful = sum(unhelpful_votes) / len(unhelpful_votes) if unhelpful_votes else 0
        return avg_helpful, avg_unhelpful

    def most_common_pros_and_cons(self, reviews):
        all_pros = [pro for review in reviews for pro in review["Advantages"]]
        all_cons = [con for review in reviews for con in review["Disadvantages"]]
        
        common_pros = Counter(all_pros).most_common(5)  
        common_cons = Counter(all_cons).most_common(5)  
        return common_pros, common_cons

    def display_statistics(self, reviews):
        avg_rating = self.average_rating(reviews)
        print(f"Average Rating: {avg_rating:.2f} stars")

        positive, negative = self.recommendation_stats(reviews)
        print(f"Positive Recommendations: {positive}")
        print(f"Negative Recommendations: {negative}")

        avg_helpful, avg_unhelpful = self.vote_stats(reviews)
        print(f"Average Helpful Votes: {avg_helpful:.2f}")
        print(f"Average Unhelpful Votes: {avg_unhelpful:.2f}")

        common_pros, common_cons = self.most_common_pros_and_cons(reviews)
        print("Most Common Advantages:")
        for pro, count in common_pros:
            print(f"- {pro}: {count} mentions")
        
        print("Most Common Disadvantages:")
        for con, count in common_cons:
            print(f"- {con}: {count} mentions")

        self.plot_statistics(positive, negative, avg_helpful, avg_unhelpful, common_pros, common_cons)

    def plot_statistics(self, positive, negative, avg_helpful, avg_unhelpful, common_pros, common_cons):
        plt.figure(figsize=(8, 6))
        plt.pie([positive, negative], labels=["Positive", "Negative"], autopct='%1.1f%%', colors=["#4CAF50", "#FF5722"])
        plt.title("Recommendation Statistics")
        plt.show()

        labels = ["Helpful", "Unhelpful"]
        values = [avg_helpful, avg_unhelpful]
        
        plt.figure(figsize=(8, 6))
        sns.barplot(x=labels, y=values, palette="Blues_d")
        plt.title("Average Helpful and Unhelpful Votes")
        plt.show()


        pros, pros_count = zip(*common_pros) if common_pros else ([], [])
        cons, cons_count = zip(*common_cons) if common_cons else ([], [])

        plt.figure(figsize=(12, 6))
        plt.subplot(1, 2, 1)
        sns.barplot(x=pros, y=pros_count, palette="Greens_d")
        plt.title("Most Common Advantages")
        plt.xticks(rotation=45, ha="right")

        plt.subplot(1, 2, 2)
        sns.barplot(x=cons, y=cons_count, palette="Reds_d")
        plt.title("Most Common Disadvantages")
        plt.xticks(rotation=45, ha="right")

        plt.tight_layout()
        plt.show()


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        product_code = request.form["product_code"]
        scraper = Scraper(product_code=product_code)
        reviews = scraper.get_reviews()

        if reviews:
            return render_template("reviews.html", reviews=reviews, product_code=product_code)
        else:
            return "No reviews found or there was an error scraping the reviews."

    return render_template("index.html")


@app.route("/save", methods=["POST"])
def save_data():
    product_code = request.form["product_code"]
    save_format = request.form["save_format"]
    scraper = Scraper(product_code=product_code)
    reviews = scraper.get_reviews()

    if reviews:
        if save_format == "json":
            scraper.save_to_json(reviews)
        elif save_format == "csv":
            scraper.save_to_csv(reviews)
        else:
            scraper.save_to_json(reviews)
            scraper.save_to_csv(reviews)
        return redirect(url_for("index"))
    return "Error saving data"


if __name__ == "__main__":
    app.run(debug=True)

