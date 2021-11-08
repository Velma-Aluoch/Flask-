
from flask import *

app= Flask(__name__) #_name_means main
# This secret key encrypts your user session for security reasons
app.secret_key ='AG_66745_hhYuo!@' #16 characters
@app.route('/')
def home():
    return render_template('home.html')


import pymysql
# establish db connection
connection = pymysql.connect(host='localhost',user='root', password='', database='Shoes_db')

@app.route('/shoes')
def shoes():

    #create your query
    sql='SELECT* FROM Product'
    #execute/run your query
    #create a cursor used to execute sql
    cursor= connection.cursor()

    #now use the cursor to execute your sql
    cursor.execute(sql)

    #check how many rows were returned
    if cursor.rowcount==0:
        return render_template('shoes.html', msg='Out of stock')
    else:
        rows = cursor.fetchall()
        return render_template('shoes.html', rows=rows)


####################################################
#this route will display a single shoe
#this route will need a product id
@app.route('/single/<Product_id>')
def single(Product_id):

    #create your query, provide a %s placeholder
    sql='SELECT* FROM Product WHERE Product_id=%s'
    #execute/run your query
    #create a cursor used to execute sql
    cursor= connection.cursor()

    #now use the cursor to execute your sql
    #below you provide id to replace the %s
    cursor.execute(sql, (Product_id))

    #check how many rows were returned
    if cursor.rowcount==0:
        return render_template('single.html', msg='product doesnt exist')
    else:
        row = cursor.fetchone()
        return render_template('single.html', row=row)

    #This row will display single shoes




            # creating a login route
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        #         we now move to the database and confirm if above details exist

        sql = 'SELECT * FROM Customer where customer_email=%s and customer_password=%s'
        # create a cursor and execute above sql
        cursor = connection.cursor()
        # execute the sql, provide email and password to fit %s
        cursor.execute(sql, (email, password))

        # check if a match was found
        if cursor.rowcount == 0:
            return render_template('login.html', error='Wrong credentials')
        elif cursor.rowcount == 1:
            # create a user to track who is logged in
            # Attach user email to the session
            session['user'] = email
            return redirect('/shoes')
        else:
            return render_template('login.html', error='Error occured,Try later')
    else:
        return render_template('login.html')


# craete a sign up templates create fields as per customer table
@app.route('/register', methods=['POST', 'GET'])
def register():

    if request.method == 'POST':
        customer_firstname = request.form['customer_firstname']
        customer_lastname = request.form['customer_lastname']
        customer_surname = request.form['customer_surname']
        customer_phone = request.form['customer_phone']
        customer_email = request.form['customer_email']
        customer_password = request.form['customer_password']
        confirm_password = request.form['confirm_password']
        customer_gender = request.form['customer_gender']
        customer_address = request.form['customer_address']
        dob = request.form['dob']

        import re
        if customer_password != confirm_password:
            return render_template('register.html', password='password do not match')
        elif len(customer_password) < 6:
            return render_template('register.html', password='password must be 6 characters')
        elif not re.search('[a-z]', customer_password):
            return render_template('register.html', password='Must have a small letter' )
        elif not re.search('[A-Z]', customer_password):
            return render_template('register.html', password='Must have a caps letter' )
        elif not re.search('[0-9]', customer_password):
            return render_template ('register.html', password='Must have a number')
        elif not re.search('[_@$]', customer_password):
            return render_template('register.html', password='Must have special characters' )
        elif len(customer_phone) < 10:
            return render_template('register.html', phone='Must be above 10 numbers')
        else:
            sql = 'insert into Customer(customer_firstname, customer_lastname, customer_surname, customer_phone, customer_email, customer_password, customer_gender, customer_address, dob) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)'
            cursor = connection.cursor()
            try:
                cursor.execute(sql, (customer_firstname, customer_lastname, customer_surname, customer_email,customer_phone, customer_password, customer_gender, customer_address,dob))
                connection.commit()
                return render_template('register.html', success='Saved Successfully')
            except:
                return render_template('register.html', error='Failed')

    else:
        return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user') #clear session
    return redirect('/login')

@app.route('/reviews', methods=['POST', 'GET'])
def reviews():
    if request.method=='POST':
        user = request.form['user']
        product_id = request.form['product_id']
        message = request.form['message']

        sql = 'insert into reviews(user, product_id, message) values (%s, %s, %s)'
        cursor = connection.cursor()
        try:
            cursor.execute(sql, (user, product_id, message))
            connection.commit()
            # when going back to/single carying the product id

            flash('Review posted successfully')
            flash('Thank you for your review')
            return redirect(url_for ('single', Product_id=product_id))
        # the flashed message goes single.html
        except:
            flash('Review not posted')
            return redirect(url_for ('single', Product_id=product_id))
        else:
            return''


import requests
import datetime
import base64
from requests.auth import HTTPBasicAuth
@app.route('/mpesa_payment', methods = ['POST','GET'])
def mpesa_payment():
        if request.method == 'POST':
            phone = str(request.form['phone'])
            amount = str(request.form['amount'])
            #capture the session of paying client
            email = session['user']

            qtty=str(request.form['qtty'])
            product_id=str(request.form['Product_id'])
            # multiply quantity * amount
            total_pay= float(qtty) * float(amount)

            # SQL to insert to sql
            # create a table named payment_info
            # pay_id Int, PK AI
            # PHONE varchar 50,
            # email varchar 100
            # qtty int 50
            # product_id int 50
            # total_pay
            # pay_date timestamp default current timestamp
            sql = 'insert into Payment_info (phone, email, qtty,total_pay, product_id) values(%s, %s, %s, %s, %s)'
            cursor = connection.cursor()
            cursor.execute(sql,(phone, email, qtty, total_pay, product_id))
            connection.commit()



            # GENERATING THE ACCESS TOKEN
            consumer_key = "BeUa0XvSlJIsGMPICIQOVCGwAYWIlQgK"
            consumer_secret = "49iS4NsBHJ4m9bik"

            api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials" #AUTH URL
            r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))

            data = r.json()
            access_token = "Bearer" + ' ' + data['access_token']

            #  GETTING THE PASSWORD
            timestamp = datetime.datetime.today().strftime('%Y%m%d%H%M%S')
            passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
            business_short_code = "174379"
            data = business_short_code + passkey + timestamp
            encoded = base64.b64encode(data.encode())
            password = encoded.decode('utf-8')


            # BODY OR PAYLOAD
            payload = {
                "BusinessShortCode": "174379",
                "Password": "{}".format(password),
                "Timestamp": "{}".format(timestamp),
                "TransactionType": "CustomerPayBillOnline",
                "Amount": amount,  # use 1 when testing
                "PartyA": phone,  # change to your number
                "PartyB": "174379",
                "PhoneNumber": phone,
                "CallBackURL": "https://modcom.co.ke/job/confirmation.php",
                "AccountReference": email,
                "TransactionDesc": 'qtty' +qtty +'ID:' +product_id
            }


            # POPULATING THE HTTP HEADER
            headers = {
                "Authorization": access_token,
                "Content-Type": "application/json"
            }

            url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest" #C2B URL

            response = requests.post(url, json=payload, headers=headers)
            print (response.text)
            return render_template('payment.html', msg = 'Please Complete Payment in Your Phone')
        else:
            return render_template('payment.html')


@app.route('/contact', methods=['POST','GET'])
def contact():
    if request.method == 'POST':
        name=request.form['name']
        Email=request.form['Email']
        message=request.form['message']

        sql='insert into contact (name, Email, message) Values (%s, %s, %s)'
        cursor=connection.cursor()

        try:
            cursor.execute(sql, (name, Email, message))
            connection.commit()

            return redirect(url_for('contact', msg='Succesfull'))
        except:
            return redirect(url_for('contact', msg='Unsuccesful'))

    else:
        return render_template('contact.html')


# admin side dashboard===============
@app.route('/admin', methods = ['POST','GET'])
def admin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        # we now move to the database and confirm if above details exist
        sql = "SELECT * FROM admin where email = %s and password=%s"
        # create a cursor and execute above sql
        cursor = connection.cursor()
        # execute the sql, provide email and password to fit %s placeholders
        cursor.execute(sql, (email, password))
        # check if a match was found
        if cursor.rowcount ==0:
            return render_template('admin.html', error = 'Wrong Credentials')
        elif cursor.rowcount ==1:
            session['admin'] = email
            return  redirect('/dashboard')
        else:
            return render_template('admin.html', error='Error Occured, Try Later')
    else:
        return render_template('admin.html')


# admin side dashboard===============
@app.route('/admin', methods = ['POST','GET'])
def admin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        # we now move to the database and confirm if above details exist
        sql = "SELECT * FROM admin where email = %s and password=%s"
        # create a cursor and execute above sql
        cursor = connection.cursor()
        # execute the sql, provide email and password to fit %s placeholders
        cursor.execute(sql, (email, password))
        # check if a match was found
        if cursor.rowcount ==0:
            return render_template('admin.html', error = 'Wrong Credentials')
        elif cursor.rowcount ==1:
            session['admin'] = email
            return  redirect('/dashboard')
        else:
            return render_template('admin.html', error='Error Occured, Try Later')
    else:
        return render_template('admin.html')


# dashboard
@app.route('/dashboard')
def dashboard():
    if 'admin' in session:
        sql = "select * from customers ORDER by reg_date DESC"
        cursor = connection.cursor()
        cursor.execute(sql)
        if cursor.rowcount == 0:
            return render_template('dashboard.html', msg = "No Customers")
        else:
            rows = cursor.fetchall()
            return  render_template('dashboard.html', rows = rows) # create this template
    else:
        return redirect('/admin')





#git link: https://github.com/modcomlearning/Flaskproject
#create a github account from github.com

if __name__ =='__main__':
     app.run(debug=True)
#right click and run
#http://127.0.0.1:5000/
