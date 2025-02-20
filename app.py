# dependenies
import json
from flask import Flask, render_template, jsonify,request
import scrape_mars as sc
from flask_pymongo import PyMongo




#################################################
# Flask Setup
#################################################
app = Flask(__name__)

app.config['MONGO_URI'] = "mongodb://localhost:27017/mars_data"
mongo = PyMongo(app)

# Route to render index.html template using data from Mongo
@app.route("/")
def index():

    # Find one record of data from the mongo database
    mars_data = mongo.db.mars_data.find_one()

    # Return template and data
    return render_template("index.html", mars_data=mars_data)


# Route that will trigger the scrape function
@app.route("/scrape")
def scrape():

    # Run the scrape function
    mars_data = sc.scrape()

    # Update the Mongo database using update and upsert=True
    mongo.db.mars_data.update({}, mars_data, upsert=True)
    return 'Done!'


if __name__ == "__main__":
    app.run(debug=True)
