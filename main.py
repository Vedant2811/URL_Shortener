#                           ____________*********|| URL Shortener|| *********____________
#
# importing all the required packages and modules
# from flask means flask named package import Flask module
import random

from flask import Flask, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
import re
from werkzeug.utils import redirect

from md5Hash import MD5

app = Flask(__name__)
# configuring SQLALCHEMY_DATABASE_URI and SQLALCHEMY_TRACK_MODIFICATIONS
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'False'
# database of app which is created using Flask and SQLALCHEMY
db = SQLAlchemy(app)


# creating Urls named table in the database using flask_sqlalchemy
class Urls(db.Model):
    # creating columns inside table
    id_ = db.Column("id_", db.Integer, primary_key=True)
    long = db.Column("long", db.String())
    short = db.Column("short", db.String())

    # calling the constructor for inserting the entries
    def __init__(self, long, short):
        self.long = long
        self.short = short


# final commit for creating table
@app.before_first_request
def create_tables():
    db.create_all()


# main functions which shorten the long url to a shorter string
def shorten_url(div):
    # div is basically the hash code of long url

    # characters named string
    characters = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+/=?"
    # calculating the length of characters string
    base = len(characters)

    # initializing a list
    ret = []
    # checking if argument div passed to the function is positive
    # if not making it positive
    if div < 0:
        div *= -1
    # printing div value for debugging purpose
    print(div)
    while div > 0:
        # taking modulo of div by base(length of characters string)
        val = div % base
        # printing val value for debugging purpose
        print(val)
        # appending the character present in val position in characters string to ret list
        ret.append(characters[val])
        # printing ret list value for debugging purpose
        # print(ret)
        # integer division of div by base
        # if    x = 37 // 3
        #       x = 12
        div = div // base
    # returning the ret list in reverse order for another validation
    mainStr = "".join(ret[::-1])
    shortLen = random.randint(4, 8)
    print(shortLen)
    beg = random.randint(0, len(mainStr) - shortLen)
    print(beg)
    return mainStr[beg : beg + shortLen]

# checking if long url passed is even a valid url or not
# it will return a boolean value (true or false)


def isValidURL(s):
    regex = ("((http|https)://)(www.)?" +
             "[a-zA-Z0-9@:%._\\+~#?&//=]" +
             "{2,256}\\.[a-z]" +
             "{2,6}\\b([-a-zA-Z0-9@:%" +
             "._\\+~#?&//=]*)")

    p = re.compile(regex)
    # if no url is passed then return false
    if s is None:
        return False
    # if url is passed and validated then return true otherwise return false
    if re.search(p, s):
        return True
    else:
        return False


def hashCode(ori_url):
    list = []
    looptill = 0
    if len(ori_url) <= 175:
        # if length of original url is less than 175
        # looptill variable gets value of length of url
        looptill = len(ori_url)

    else:
        # else looptill value will be 175
        looptill = 175
    # iterate value of looptill times till poiinter reaches
    # looptill - 1th postion
    for i in range(looptill):
        # x = 31 exponent i
        x = 31 ** i
        # store the data in a list
        list.append(x)

    big = 0
    # convert the string into integer using given formula
    for i in range(looptill):
        big = big + ord(ori_url[i]) * list[i]

    return big


# it is the method which is called first
@app.route('/', methods=['POST', 'GET'])
def home():
    # check if method request is post or get
    if request.method == "POST":
        # receiving the string from the html page named main_url
        url_recieved = request.form["main_url"]
        # checking for the validation of url if it is valid
        if isValidURL(url_recieved):
            # checking the database for the entry of url as long url
            found_url = Urls.query.filter_by(long=url_recieved).first()
            # if url entered is found on database return the shortened url and display it
            if found_url:
                return redirect(url_for("display_short_url", url=found_url.short))
            # if not shorten it
            else:
                # calling shorten_url function and passing hash code of that particular string/url
                plain = hashCode(str(MD5.hash(url_recieved)))
                short_url = shorten_url(plain)

                # setting a boolean variable flag to true
                flag = True
                # running the while loop till flag is true
                while flag:
                    #
                    found_short_url = Urls.query.filter_by(short=short_url).first()
                    if found_short_url:
                        plain = hashCode(str(MD5.hash(url_recieved)))
                        short_url = shorten_url(plain)
                    else:
                        flag = False

                # final step before entering the data into database
                new_url = Urls(url_recieved, short_url)
                # adding the new entry to the table
                db.session.add(new_url)
                # commiting the transaction previously done
                db.session.commit()
                # display the shortened form of long url
                return redirect(url_for("display_short_url", url=short_url))
        else:
            # if url provided is not valid display the following message
            return f"<h1>URL provided is not a valid url. Please type a valid URL</h1>"
    else:
        # if method request is get then return to the home page
        return render_template("home.html")


# creating a function for redirection when we put short url after / (slash)
@app.route('/<short_url>')
def redirection(short_url):
    # check for the entries in the table to find long url corresponding to that short url
    long_url = Urls.query.filter_by(short=short_url).first()
    # if it's present redirect to long url
    if long_url:
        return redirect(long_url.long)
    # if not present display the following message
    else:
        return f'<h1>Url doesnt exist</h1>'


#
@app.route('/display/<url>')
def display_short_url(url):
    return render_template('shorturl.html', short_url_display=url)


# created a function to display all the long and short urls present in the table
@app.route('/all_urls')
def display_all():
    return render_template('all_urls.html', vals=Urls.query.all())


# if the name of file is main then only run this application and port no. will be 5000
# and option for debugging will be available
if __name__ == '__main__':
    app.run(port=5000, debug=True)

# abcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghijabcdefghij