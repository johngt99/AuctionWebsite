import smtplib
from email.message import EmailMessage

def email_content(item, user):     
    msg = EmailMessage()
    msg['Subject'] = 'Coventry Auctions'
    msg['From'] = 'announcementsandarticles@gmail.com'#sender
    msg['To'] = user.email_address
    msg.set_content('Congratulations!!! You won the auction: ' + item.name + '. Go to ' +    #body of the message with link to payment
                    '<a href="http://127.0.0.1:5000/payment">Payment</a>' + ' to finish your payment.', subtype='html')

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login('announcementsandarticles@gmail.com', 'yhbaejcjupglhpxz')#email and password of the sender
        smtp.send_message(msg)

    breakpoint

