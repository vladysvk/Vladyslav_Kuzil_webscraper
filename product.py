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