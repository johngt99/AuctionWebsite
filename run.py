from auction import app
#Checks if the run.py file has executed directly and not imported
if __name__ == '__main__':
    app.run(debug=True)

#creates the DB if it doesn't exist already
from auction import db
db.create_all()     