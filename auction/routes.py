from datetime import datetime
from fileinput import filename
import flask
from auction import app
from flask import render_template, redirect, url_for, flash, request
from auction.models import Item, User
from auction.forms import RegisterForm, LoginForm, NewItemForm, PlaceBidForm
from auction import db
from auction.sendmail import email_content
from flask_login import login_user, logout_user, login_required, current_user
import os

#Home page that shows all active auctions
@app.route('/')
@app.route('/auction', methods=['GET'])
def auction_page():    
    items = Item.query.filter_by(item_sold=False)                           #import and show all items that have not been sold yet
    return render_template('auction.html', items=items)

#Display the item information page
@app.route("/item/<int:item_id>", methods=["GET", "POST"])
@login_required
def item_page(item_id):
    item = Item.query.filter_by(id=item_id).first()                         #import de item information
    user = User.query.filter_by(username=item.seller).first()               #import de user information that corresponds to the item seller
    return render_template('item.html', item=item, user=user)

#Display the bid page of the item
@app.route("/bid/<int:item_id>", methods=["GET", "POST"])
@login_required
def bid_page(item_id):
    form = PlaceBidForm()
    item = Item.query.filter_by(id=item_id).first()                         #import de item information
    if form.validate_on_submit():
        if form.new_bid.data > item.curr_bid:                               #if there is a bid on the auction 
            item.curr_bid=form.new_bid.data+10                              #the next bid will be 10p higher
            item.last_bidder = item.highest_bidder_id                       #change the last bidder if bid increases
            item.highest_bidder_id = current_user.id                        #change the current highest bidder for the current user
            try:
                db.session.commit()
                flash("Bid placed Successfully!", category='success')
                return redirect('/auction')
            except:
                flash("Error! Looks like there was a problem... Try again!", category='danger')
                return render_template('bid.html', form=form, item=item)
        else:
            flash("Error! Your bid has to be higher than the current bid... Try again!",category='danger')
            return render_template('bid.html', form=form, item=item)
    else:
        return render_template('bid.html', form=form, item=item)



#Saving The image in the folder
def save_image(image_file):
    image_name=image_file.filename
    image_path=os.path.join(app.root_path, 'static/images', image_name)     #save images to static/image folder
    image_file.save(image_path)
    return image_name

#add new item to the DB    
@app.route('/sellitem', methods=['GET','POST'])
@login_required
def sellitem_page():
    form = NewItemForm()
    date_time=datetime.now()
    date = date_time.strftime("%d  %B  %Y")                                 #show a better looking data format
    if form.validate_on_submit():
        img_file=save_image(form.image.data)                                #save image from the newitem form
        sell_new_item = Item(name=form.item_name.data,
                             start_price=form.item_price.data,
                             curr_bid=form.item_price.data,
                             description=form.item_description.data,
                             owner=None,
                             seller=current_user.username,
                             image=img_file,
                             date_created=date_time,
                             show_date=date
                            )
        db.session.add(sell_new_item)                                       #add every new data to the db
        db.session.commit()
        return redirect(url_for('auction_page'))
    return render_template('sellitem.html', form=form)


#Display Items that current user is selling
@app.route('/myitems', methods=['GET', 'POST'])
@login_required
def myitems_page():
    items = Item.query.filter_by(seller=current_user.username) 
    return render_template('myitems.html', items=items)


#Sells the Item, removes it from home page and send email to the winner
@app.route('/sold/<int:item_id>')
def sold(item_id):
    item = Item.query.filter_by(id=item_id).first()
    try:
        if item.curr_bid != item.start_price:                               #it there is a new bid
            item.owner = item.highest_bidder_id                             #the owner of the item is the highest bidder
            item.item_sold = True                                           #item is sold
            user = User.query.filter_by(id=item.owner).first()              #get the user with higher bin in the item
            db.session.commit()                                             #commit to db
            email_content(item, user)                                       #Send email to the winner
            return redirect('/myitems')
        else:                                                               #if ther is no bids for this item
            item.owner = item.highest_bidder_id                             #the item owner = Null
            item.item_sold = True                                           #item status is sold but no one wins
            db.session.commit()                                             #commit to db
            return redirect('/myitems')
    except:
        return "There was a problem"
        

#Shows all the items that user has won in auctions
@app.route('/inventory', methods=['GET'])
@login_required
def inventory_page():
    items = Item.query.filter_by(owner=current_user.id)
    return render_template('inventory.html', items=items)

#Display message if user gets outbid in one auction
@app.route('/messages', methods=['GET'])
@login_required
def messages_page():
    items = Item.query.filter_by(last_bidder=current_user.id)
    return render_template('messages.html', items=items)

#Payment page that user receives on the email
@app.route('/payment')
@login_required
def payment_page():
    return render_template('paymentpage.html')

#Register new user
@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                              email_address=form.email_address.data,
                              phone_number=form.phone_number.data,
                              password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f"Account created successfully! You are now logged in as {user_to_create.username}", category='success')
        return redirect(url_for('auction_page'))
    if form.errors != {}:                                                   #If there are not errors from the validations
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')

    return render_template('register.html', form=form)

#Checks if user is registered and do the login
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data
        ):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('auction_page'))
        else:
            flash('Username and password are not match! Please try again', category='danger')

    return render_template('login.html', form=form)

#Logout current user
@app.route('/logout')
def logout_page():
    logout_user()
    flash("You have been logged out!", category='info')
    return redirect(url_for("auction_page"))

