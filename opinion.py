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