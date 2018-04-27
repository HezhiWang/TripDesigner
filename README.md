# Trip Designer

This is the final project for **DS-GA 3001 Advanced Python**, which originates from the course project for [**DS-GA 1007 Programming for Data Science**](https://github.com/hzhao16/final_project/tree/master/hz1411-hw1567-sar516-master). This is a web application written in Python Django Framework. It can design travel plans for users with specific preferences.

## Contributors

Hezhi Wang [https://github.com/HezhiWang](https://github.com/HezhiWang) Netid: hw1567

Han Zhao [https://github.com/hzhao16](https://github.com/hzhao16) Netid: hz1411

## How to run locally

### 1. Install the dependencies

```
pip install -r requirements.txt
```

### 2. Get API keys

This web application uses 3 free APIs:

- [Amadeus API](https://sandbox.amadeus.com/api-catalog)
- [Yelp Fusion API](https://www.yelp.com/developers/faq)
- [Google Maps API](https://developers.google.com/maps/documentation/javascript/get-api-key)

Please follow the links and get the keys. Then,

```
$ cd TripDesigner
$ touch trip/api/config.py
$ touch trip/static/trip/config.js
```
In config.py, enter your API keys like so:
```
YELP_API_KEY = "YOUR YELP FUSION API KEY" 
AMADEUS_API_KEY = "YOUR AMADEUS API KEY"
GOOGLEMAP_KEY = "YOUR GOOGLE MAPS API KEY"
```
In config.js, enter you Google Maps API key like so:
```
var config = {
  Googlemapskey : "YOUR GOOGLE MAPS API KEY"
}
```

### 3. Connect to Scrapyd service
cd into the home directory, and in the command line
```
$ cd scrapy_app
$ scrapyd
```
Make sure **not** to close this window while using the app.

### 4. Start the app
Open a new command line window, into the home directory,
```
$ python manage.py runserver
```

### 5. Browser Requirements
To avoid any error, please use the newest version of Google Chrome. 
