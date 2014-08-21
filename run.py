import os
from loghub import app
from loghub.storage import db


if __name__ == '__main__':
    #app.run("192.168.33.10",
    app.run("localhost",
            debug=True)
