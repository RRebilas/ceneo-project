def set_value(opinion, tag, tag_class, child):
    try:
        return opinion.find(tag, tag_class).find(child).get_text().strip()
    except AttributeError:
        return None


class Opinion:

    def __init__(self, opinion):
        self.opinion_id = int(opinion["data-entry-id"])
        self.author = opinion.find("div", "reviewer-name-line").string.strip()
        self.stars = int(opinion.find("span", "review-score-count").string[0])
        self.useful = int(opinion.find("button", "vote-yes").find("span").string)
        self.useless = int(opinion.find("button", "vote-no").find("span").string)
        self.content = opinion.find("p", "product-review-body").getText()
        self.date_of_issue = opinion.find("span", "review-time").find_all("time")[0]["datetime"]
        risk_values = [['div', 'product-review-summary', 'em'], ['div', 'product-review-pz', 'em'],
                       ['div', 'cons-cell', 'ul'], ['div', 'pros-cell', 'ul']]
        self.recommendation, self.purchased, self.cons, self.pros = [set_value(opinion, *tags) for tags in risk_values]
        self.purchased = 'Tak' if (self.purchased == "Opinia potwierdzona zakupem") else 'Nie'
        try:
            self.date_of_purchase = opinion.find("span", "review-time").find_all("time")[1]["datetime"]
        except IndexError:
            self.date_of_purchase = None
