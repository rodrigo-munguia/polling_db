from time import sleep
from datetime import datetime, timezone
from apscheduler.schedulers.background import BackgroundScheduler
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from mail import Send_remainder_mail_to_client, Send_cancel_mail_to_client
import os

 
# Creates a default Background Scheduler
sched = BackgroundScheduler()

#-----------------------------------------------
# function for deleting orders (and put their items to stock back) if orders have been
# in kart for more than X minutes
def polling_kart_orders(db_conf):
    print("Executing polling kart orders...")
    now = datetime.now(timezone.utc)
    #current_time = now.strftime("%H:%M:%S")
    #print("Current Time =", current_time)
    
    try:
        conn = psycopg2.connect(
                host=db_conf["db_HOST"],
                database=db_conf["db_NAME"],
                user=db_conf["db_USER"],
                password=db_conf["db_PASSWORD"],
                port = db_conf["db_PORT"],
                cursor_factory=RealDictCursor)
        
        """
        # create a cursor
        cur = conn.cursor()        
	    # execute a statement
        print('PostgreSQL database version:')
        cur.execute('SELECT version()')
        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        print(db_version)
        """
        cursor = conn.cursor() 
        query = "SELECT * FROM core_order WHERE ordered = false "
        cursor.execute(query)        
        orders_in_kart = cursor.fetchall()   
        
        
        for order_k in orders_in_kart: 
            print(order_k["start_date"])         
            delta_t = now - order_k["start_date"]           
            elapsed_minutes = delta_t.days*24*60 + delta_t.seconds/60
            
            if elapsed_minutes > 60: # if the order in kart has been active more than X minutes
                print(elapsed_minutes) 
                print("kart time expired for order")
                print(order_k["order_number"])                
                # select orderitem
                query = "SELECT * FROM core_orderitem WHERE order_id = " + str(order_k["id"])
                cursor.execute(query)        
                order_items = cursor.fetchall()
                
                # update stock
                for order_it in order_items:
                    item_id = order_it["item_id"]
                    quantity = order_it["quantity"]
                    orderitem_id = order_it["id"]
                    # select item
                    query = "SELECT * FROM core_item WHERE id = " + str(item_id)
                    cursor.execute(query) 
                    item = cursor.fetchall()
                    stock = item[0]["stock"]
                    new_stock = stock + quantity
                    query = "UPDATE core_item SET stock = %s  WHERE id = %s"
                    cursor.execute(query,(new_stock,item_id))
                    conn.commit()
                
                # delete orderitem
                query = "DELETE FROM core_orderitem WHERE order_id = " + str(order_k["id"])
                cursor.execute(query) 
                conn.commit()
                # delete order
                query = "DELETE FROM core_order WHERE id = " + str(order_k["id"])
                cursor.execute(query)
                conn.commit()
        
        conn.close()        
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


#-----------------------------------------------
# function for deleting pick_up orders (and put their items to stock back) if the order has been not
# complete (payed) in more than X hours.
# After deleting/canceling the order, send a remainder emil to the customer in Y hours 

def polling_pick_up_orders(db_conf,email_conf):
    print("polling pick up orders..")
    now = datetime.now(timezone.utc)
    try:
        conn = psycopg2.connect(
                host=db_conf["db_HOST"],
                database=db_conf["db_NAME"],
                user=db_conf["db_USER"],
                password=db_conf["db_PASSWORD"],
                port = db_conf["db_PORT"],
                cursor_factory=RealDictCursor)
        
        cursor = conn.cursor() 
        query = "SELECT * FROM core_order WHERE delivery_option = 'P' AND complete = False "
        cursor.execute(query)        
        pu_orders = cursor.fetchall()   
        #print(pu_orders)
        
        for order in pu_orders:
            ordered_date = order["ordered_date"]
            delta_t = now - ordered_date            
            elapsed_hours = delta_t.days*24 + delta_t.seconds/3600
            
            # if elapsed hours is more than X hours
            if elapsed_hours > 6 and order["reminder"] == False:
                print(delta_t) 
                print("Reminder for order")
                order_number = order["order_number"]
                print(order_number)
                query = "SELECT * FROM auth_user WHERE id = " + str(order["user_id"])
                cursor.execute(query)
                user =  cursor.fetchone()
                user_name = user["username"]                
                print(user_name)
                query = "SELECT * FROM core_shippingaddress WHERE id = " + str(order["ShippingAddress_id"])
                cursor.execute(query)
                shipping_address =  cursor.fetchone()
                user_mail = shipping_address["email"]
                print(user_mail)
                query = "SELECT * FROM core_payment WHERE id = " + str(order["payment_id"])
                cursor.execute(query)
                order_payment = cursor.fetchone()
                total_amount = order_payment["amount"]
                print("total = " + str(total_amount))                
                query = "SELECT * FROM core_orderitem WHERE order_id = " + str(order["id"])
                cursor.execute(query)        
                order_items = cursor.fetchall()
                # update stock
                order_items_list = []
                for order_it in order_items:
                    item_id = order_it["item_id"]
                    quantity = order_it["quantity"]
                    orderitem_id = order_it["id"]
                    # select item
                    query = "SELECT * FROM core_item WHERE id = " + str(item_id)
                    cursor.execute(query) 
                    item = cursor.fetchall()[0]
                    o_i = str(quantity) + " of " + str(item["title"])
                    print(o_i)
                    order_items_list.append(o_i)
            
                email_data ={
                    "name":user_name,
                    "order":order_number,
                    "email":user_mail,
                    "order_items": order_items_list,
                    "amount":total_amount
                }
                                
                # send remainder mail to client
                Send_remainder_mail_to_client(email_conf,email_data)
                    
                # set the ramainder status to true
                query = "UPDATE core_order SET reminder = True"
                cursor.execute(query)
                conn.commit()
            
            # if elapsed hours is more than X hours
            if elapsed_hours > 24 and order["reminder"] == True:
                print(delta_t) 
                print("Cancel for order")
                order_number = order["order_number"]
                print(order_number)
                query = "SELECT * FROM auth_user WHERE id = " + str(order["user_id"])
                cursor.execute(query)
                user =  cursor.fetchone()
                user_name = user["username"]                
                print(user_name)
                query = "SELECT * FROM core_shippingaddress WHERE id = " + str(order["ShippingAddress_id"])
                cursor.execute(query)
                shipping_address =  cursor.fetchone()
                user_mail = shipping_address["email"]
                print(user_mail)
                query = "SELECT * FROM core_payment WHERE id = " + str(order["payment_id"])
                cursor.execute(query)
                order_payment = cursor.fetchone()
                total_amount = order_payment["amount"]
                print("total = " + str(total_amount))                
                query = "SELECT * FROM core_orderitem WHERE order_id = " + str(order["id"])
                cursor.execute(query)        
                order_items = cursor.fetchall()
                # update stock
                order_items_list = []
                for order_it in order_items:
                    item_id = order_it["item_id"]
                    quantity = order_it["quantity"]
                    orderitem_id = order_it["id"]
                    # select item
                    query = "SELECT * FROM core_item WHERE id = " + str(item_id)
                    cursor.execute(query) 
                    item = cursor.fetchall()
                    stock = item[0]["stock"]
                    new_stock = stock + quantity
                    o_i = str(quantity) + " of " + str(item[0]["title"])
                    order_items_list.append(o_i)
                    query = "UPDATE core_item SET stock = %s  WHERE id = %s"
                    cursor.execute(query,(new_stock,item_id))
                    conn.commit()                                   
                
            
                email_data ={
                    "name":user_name,
                    "order":order_number,
                    "email":user_mail,
                    "order_items": order_items_list,
                    "amount":total_amount
                }
                                
                # send cancelation mail to client
                Send_cancel_mail_to_client(email_conf,email_data)
                    
                # delete orderitem
                query = "DELETE FROM core_orderitem WHERE order_id = " + str(order["id"])
                cursor.execute(query) 
                conn.commit()
                # delete order
                query = "DELETE FROM core_order WHERE id = " + str(order["id"])
                cursor.execute(query)
                conn.commit()                      
              
        
        
        conn.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        

                 
    
#-------------------------------------------------------------    
    
if __name__ == '__main__':    

    
    if os.environ.get('DEBUG') is not None:
        DEBUG = os.environ.get('DEBUG')
    else:
        DEBUG = True 
    
    
    if DEBUG == True:
        # for development environment 
        f = open('personal_config.json')
        config = json.load(f)
        db = config['railway_db'][0]
            
        
        db_conf = {"db_NAME" : db['NAME'],
                    "db_USER" : db['USER'],
                    "db_PASSWORD":db['PASSWORD'],
                    "db_HOST":db['HOST'],
                    "db_PORT" :db['PORT']  }
        
        email = config['email'][0]
        
        email_conf = {                    
                    "EMAIL_HOST": email['EMAIL_HOST'] ,
                    "EMAIL_HOST_USER":email['EMAIL_HOST_USER']  ,
                    "EMAIL_HOST_PASSWORD":email['EMAIL_HOST_PASSWORD']  ,
                    "EMAIL_PORT":email['EMAIL_PORT']  ,
                    "EMAIL_USE_TLS": email['EMAIL_USE_TLS'] ,
                    "EMAIL_USE_SSL": email['EMAIL_USE_SSL'] }
    
    else:
        
        
        # for production environment
        DB_NAME = os.environ.get('DB_NAME', default='')
        DB_USER = os.environ.get('DB_USER', default='')
        DB_PASSWORD = os.environ.get('DB_PASSWORD', default='')
        DB_HOST = os.environ.get('DB_HOST', default='') 
        DB_PORT = os.environ.get('DB_PORT', default='')        
         
        EMAIL_HOST = os.environ.get('EMAIL_HOST', default='')
        EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', default='')
        EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', default='')
        EMAIL_PORT = os.environ.get('EMAIL_PORT', default='')
        EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', default='') 
        EMAIL_USE_SSL = os.environ.get('EMAIL_USE_SSL', default='') 

        db_conf = {"db_NAME" : DB_NAME,
                    "db_USER" : DB_USER,
                    "db_PASSWORD":DB_PASSWORD,
                    "db_HOST":DB_HOST,
                    "db_PORT" :DB_PORT }
        
        email_conf = {                    
                    "EMAIL_HOST": EMAIL_HOST ,
                    "EMAIL_HOST_USER":EMAIL_HOST_USER ,
                    "EMAIL_HOST_PASSWORD":EMAIL_HOST_PASSWORD ,
                    "EMAIL_PORT":EMAIL_PORT ,
                    "EMAIL_USE_TLS": EMAIL_USE_TLS,
                    "EMAIL_USE_SSL": EMAIL_USE_SSL }
        
    #------------------------------------------------------------------------
    
     
    sched.add_job(lambda:polling_kart_orders(db_conf),'interval', minutes=10)
    sched.add_job(lambda:polling_pick_up_orders(db_conf,email_conf),'interval', hours=1)
    
    
    # Starts the Scheduled jobs
    sched.start()
    
    # Runs an infinite loop
    while True:
        sleep(1)
        
    