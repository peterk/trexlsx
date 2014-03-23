import os
import requests
from flask import Flask
from flask import render_template, send_file, send_from_directory
from flask import request
from trello import TrelloApi
from openpyxl import Workbook
from openpyxl.cell import get_column_letter
from openpyxl.style import Color, Fill

app = Flask(__name__)
app.config.from_pyfile('settings.py')
TRELLO_APP_KEY = app.config["TRELLO_APP_KEY"]

@app.route('/test')
def test():
    return app.root_path


@app.route('/')
def index():
    return render_template('index.html', TRELLO_APP_KEY=TRELLO_APP_KEY)


@app.route('/export/', methods=['POST','GET'])
def export():

    token = request.form["token"]
    board_id = request.form["board_id"]

    # Get board lists
    LIST_URL = "https://api.trello.com/1/boards/%s/lists/?key=%s&token=%s" % (board_id, TRELLO_APP_KEY, token)
    r = requests.get(LIST_URL)
    lists_json = r.json()

    #call trello and get cards for the selected board
    # /1/boards/[board_id]/cards/visible
    CARD_URL = "https://api.trello.com/1/boards/%s/cards/visible?members=true&fields=idShort,idList,name,desc,labels,dateLastActivity,shortUrl&member_fields=fullName,username&key=%s&token=%s" % (board_id, TRELLO_APP_KEY, token)
    r = requests.get(CARD_URL)
    cards_json = r.json()

    #start xlsx file
    wb = Workbook(optimized_write = False)
    ws = wb.active
    ws.page_setup.orientation = ws.ORIENTATION_LANDSCAPE
    ws.add_print_title(1)

    #write header row dateLastActivity, shortUrl
    ws.append(["Id", "Status", "Name", "Description", "Labels", "Members", "Updated", "Link"])

    # format headers
    for cell in ws.range("A1:H1")[0]:
        cell.style.font.bold = True

        ws.column_dimensions["A"].width = 6.0
        ws.column_dimensions["B"].width = 15.0
        ws.column_dimensions["C"].width = 30.0
        ws.column_dimensions["D"].width = 30.0
        ws.column_dimensions["E"].width = 10.0
        ws.column_dimensions["F"].width = 30.0
        ws.column_dimensions["G"].width = 14.0
        ws.column_dimensions["H"].width = 27.0


    for card in cards_json:

        ws.append([
            card["idShort"],
            namefromid(card["idList"], lists_json),
            card["name"],
            card["desc"],
            labels(card),
            members(card),
            humandate(card["dateLastActivity"]),
            card["shortUrl"]])

    # store file and send it
    wb.save("%s/temp/trello_board_%s.xlsx" % (app.root_path, board_id))
    return send_from_directory(app.root_path + "/temp","trello_board_%s.xlsx" % board_id, as_attachment=True)



def namefromid(id, list):
    item = [el for el in list if el["id"] == id][0]
    return item["name"]


def members(card):
    return ", ".join([member["fullName"] for member in card["members"]])


def labels(card):
    return ", ".join([label["name"] for label in card["labels"]])


def humandate(iso_date):
    return "%s %s" % (iso_date.split("T")[0], iso_date.split("T")[1][0:5])


if __name__ == '__main__':
    app.run(debug=False)

