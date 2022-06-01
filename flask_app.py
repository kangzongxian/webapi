from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random
from flask import json

from bs4 import BeautifulSoup
import requests
import time
# from bs4 import BeautifulSoup
# import time
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager

# def getShopeePrices(item, mode):
#
#     item_word = '%20'.join(item.split(' '))
#     search_link = ""
#
#     # Relevancy
#     if mode == 0:
#         search_link = f"https://shopee.sg/search?keyword={item_word}&page=0&sortBy=relevancy"
#
#     # Price low to high
#     elif mode == 1:
#         search_link = f"https://shopee.sg/search?keyword={item_word}&order=asc&page=0&sortBy=price"
#
#     # Price high to low
#     elif mode == 2:
#         search_link = f"https://shopee.sg/search?keyword={item_word}&order=desc&page=0&sortBy=price"
#
#     # Initialise driver and go to website
#     chrome_options = Options()
#     chrome_options.add_argument('disable-notifications')
#     chrome_options.add_argument('--disable-infobars')
#     chrome_options.add_argument('start-maximized')
#     chrome_options.add_argument('headless')
#     driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
#     driver.get(search_link)
#
#     #TODO: Not sure why need to sleep here, but if don't sleep got no results
#     time.sleep(2)
#
#     # Using Selenium
#     html = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
#
#     # Using Bs4
#     soup = BeautifulSoup(html, "html.parser")
#     items = soup.find_all(name="div", class_="KMyn8J")
#
#     for item in items:
#         name = item.find("div", class_="ie3A+n").get_text()
#         print(name)
#         price = item.find("span", class_="ZEgDH9").get_text()
#         print(price)

def getAmazonPrices(item):

    # Follow the template, words separated by spaces joined by +
    item_word = '+'.join(item.split(' '))

    search_link = ""

    mode = 0
    # TODO: Currently cannot work if user sorts by low to high etc...
    # TODO: I think is cause is a JS Script so a bit hard
    # TODO: I think if really cannot, we can sort it based on the results based on relevance, then sort asc / desc
    # Update search link depending on the type that the user wants
    if mode == 0:
        search_link = f"https://www.amazon.sg/s?k={item_word}&crid=2J3NF4V3FF6EZ&" \
                      f"sprefix=water+bott%2Caps%2C310&ref=nb_sb_noss_2"
    elif mode == 1:
        search_link = f"https://www.amazon.sg/s?k={item_word}&s=price-asc-rank&crid=2J3NF4V3FF6EZ&" \
                      f"qid=1653582277&sprefix=water+bott%2Caps%2C310&ref=sr_st_price-asc-rank"
    elif mode == 2:
        search_link = f"https://www.amazon.sg/s?k={item_word}&s=price-desc-rank&crid=2J3NF4V3FF6EZ&qid" \
                      f"=1653582324&sprefix=water+bott%2Caps%2C310&ref=sr_st_price-desc-rank"

    # Send request to get the data
    item_data = requests.get(search_link)
    item_website = item_data.text

    soup = BeautifulSoup(item_website, "html.parser")

    # Some elements found with a-section may not be those with the items
    # So we need to do filtering when looping through (checking if == None)
    items = soup.find_all(name="div", class_="a-section")

    # For some reason there are duplicates (2 of each)
    # So I filter and put them into the final_objects
    item_objects = []
    final_objects = []

    for item in items:
        name = item.find("span", class_="a-text-normal")
        if name == None:
            continue
        name = name.get_text()
        price = item.find("span", class_="a-offscreen")
        if price == None:
            continue
        price = price.get_text()
        link = item.find("a", class_="a-link-normal", href=True)
        url = f"https://amazon.sg/{link['href']}"

        # Create an object with the necessary data that we need
        new_item = {
            'name': name,
            'price': price,
            'url': url
        }
        item_objects.append(new_item)

    for i in range(len(item_objects)):
        if i % 2 == 0:
            final_objects.append(item_objects[i])

    # The objects that we need
    for i in range(len(final_objects)):
        # print(final_objects[i])
        pass

    return final_objects



app = Flask(__name__)

##CREATE DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##CREATE TABLE
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/random/<cafe_id>")
def get_random_cafe(cafe_id):
    item_to_search = cafe_id
    cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(cafes)
    items = getAmazonPrices(cafe_id)

    # time.sleep(5)
    # stuff = getShopeePrices("water bottle", 0)
    return json.dumps(items)




    # return item
    # print(f"hello, {jsonify(cafe=random_cafe.to_dict())}")
    # return jsonify(cafe=random_cafe.to_dict())
    return render_template("index.html")


@app.route("/all")
def get_all_cafes():
    cafes = db.session.query(Cafe).all()
    return jsonify(cafes=[cafe.to_dict() for cafe in cafes])


@app.route("/search")
def get_cafe_at_location():
    query_location = request.args.get("loc")
    cafe = db.session.query(Cafe).filter_by(location=query_location).first()
    if cafe:
        return jsonify(cafe=cafe.to_dict())
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."}), 404


@app.route("/add", methods=["POST"])
def post_new_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})


@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def patch_new_price(cafe_id):
    new_price = request.args.get("new_price")
    cafe = db.session.query(Cafe).get(cafe_id)
    if cafe:
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the price."}), 200
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404


@app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    api_key = request.args.get("api-key")
    if api_key == "TopSecretAPIKey":
        cafe = db.session.query(Cafe).get(cafe_id)
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={"success": "Successfully deleted the cafe from the database."}), 200
        else:
            return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404
    else:
        return jsonify(error={"Forbidden": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


if __name__ == '__main__':
    app.run(debug=True)
