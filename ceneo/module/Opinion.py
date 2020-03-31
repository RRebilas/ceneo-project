class Opinion:

    def __init__(self, opinion):
        self.opinion_id = int(opinion["data-entry-id"])
        self.author = opinion.find("div", "reviewer-name-line").string.strip()
        self.stars = int(opinion.find("span", "review-score-count").string[0])
        self.useful = int(opinion.find("button", "vote-yes").find("span").string)
        self.useless = int(opinion.find("button", "vote-no").find("span").string)
        self.content = opinion.find("p", "product-review-body").getText()
        self.date_of_issue = opinion.find("span", "review-time").find_all("time")[0]["datetime"]
        try:
            self.recommendation = opinion.find("div", "product-review-summary").find("em").string
            self.purchased = opinion.find("div", "product-review-pz").find("em").string
            self.date_of_purchase = opinion.find("span", "review-time").find_all("time")[1]["datetime"]
            self.cons = opinion.find("div", "cons-cell").find("ul").get_text()
            self.pros = opinion.find("div", "pros-cell").find("ul").get_text()
        except (AttributeError, IndexError):
            self.recommendation = None
            self.purchased = None
            self.date_of_purchase = None
            self.cons = None
            self.pros = None
