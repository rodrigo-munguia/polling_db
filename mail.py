import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header



def remainder_email(email_data):    
    order_items = email_data["order_items"]    
    it_str = ""
    
    for item in order_items:
        it_str = it_str + item + "\n"      
    
    html = """\
    <html>
    <head></head>
    <body>
    <br>

        <h2>Dear """ +  email_data["name"] + """</h2>
        <h3>This is a remainder for your Order ID: """+ str(email_data["order"])+ """</h3>
        
        <h3>It is important to recall that you only have 24 hours for picking up your order in sucursal</h3>
        <h3>Sucursal address:</h3>
        <h3>Otherwise your order will be automatically cancel:</h3>               

        <h3>
            Contact Details:
        </h3>
        Email: multiservicios@gmail.com <br/>        

        <h2>Order Details:</h2>
         
        <h4> """ + it_str  +"""             </h4> 
        
        <h3> Total: """ + str(email_data["amount"]) + """ </h3>        
        
    </body>
    </html>
    """
    return html

#------------------------------------------------------------------------------

def cancel_email(email_data):    
    order_items = email_data["order_items"]    
    it_str = ""
    
    for item in order_items:
        it_str = it_str + item + "\n"      
    
    html = """\
    <html>
    <head></head>
    <body>
    <br>

        <h2>Dear """ +  email_data["name"] + """</h2>
        <h3> Unfortunately your Order ID: """+ str(email_data["order"])+ """ has been canceled </h3>
        
        <h4>The period of 24 hours for picking up your order has expired.</h4>
        <h4>If you are still interested in our products, you can place a new order.</h4>               

        <h3>
            Contact Details:
        </h3>
        Email: multiservicios@gmail.com <br/>        

        <h2>Order Details:</h2>
         
        <h4> """ + it_str  +"""             </h4> 
        
        <h3> Total: """ + str(email_data["amount"]) + """ </h3>        
        
    </body>
    </html>
    """
    return html



def Send_remainder_mail_to_client(email_conf,email_data):  

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Remainder for order " + email_data["order"]
    #msg['From'] = email_conf["EMAIL_HOST_USER"]
    msg['From'] = str(Header('Multiservicios <Multiservicios@gmail.com>'))
    msg['To'] = email_data["email"]
    # Create the body of the message (a plain-text and an HTML version).
    #text = "Hi!\nHow are you?\nHere is the link you wanted:\nhttp://www.python.org"
    html = remainder_email(email_data)    
    # Record the MIME types of both parts - text/plain and text/html.
    #part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')
    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
   # msg.attach(part1)
    msg.attach(part2)    
    # creates SMTP session
    s = smtplib.SMTP(email_conf["EMAIL_HOST"], email_conf["EMAIL_PORT"])
    # start TLS for security
    s.starttls()
    # Authentication
    s.login(email_conf["EMAIL_HOST_USER"], email_conf["EMAIL_HOST_PASSWORD"])
    # message to be sent
    message = "Message_you_need_to_send"
    # sending the mail    
    s.sendmail(email_conf["EMAIL_HOST_USER"], email_data["email"], msg.as_string())
    # terminating the session
    s.quit()    
    pass


#------------------------------------------------------------------------------------------

def Send_cancel_mail_to_client(email_conf,email_data):  

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Cancelation for order " + email_data["order"]
    #msg['From'] = email_conf["EMAIL_HOST_USER"]
    msg['From'] = str(Header('Multiservicios <Multiservicios@gmail.com>'))
    msg['To'] = email_data["email"]
    # Create the body of the message (a plain-text and an HTML version).
    #text = "Hi!\nHow are you?\nHere is the link you wanted:\nhttp://www.python.org"
    html = cancel_email(email_data)    
    # Record the MIME types of both parts - text/plain and text/html.
    #part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')
    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
   # msg.attach(part1)
    msg.attach(part2)    
    # creates SMTP session
    s = smtplib.SMTP(email_conf["EMAIL_HOST"], email_conf["EMAIL_PORT"])
    # start TLS for security
    s.starttls()
    # Authentication
    s.login(email_conf["EMAIL_HOST_USER"], email_conf["EMAIL_HOST_PASSWORD"])
    # message to be sent
    message = "Message_you_need_to_send"
    # sending the mail    
    s.sendmail(email_conf["EMAIL_HOST_USER"], email_data["email"], msg.as_string())
    # terminating the session
    s.quit()    
    pass