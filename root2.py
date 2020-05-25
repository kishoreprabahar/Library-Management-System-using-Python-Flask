import datetime
from flask import Flask, render_template, request,session, redirect, url_for, escape, request,flash,get_flashed_messages
from flask import Flask, render_template, flash
from flask import Flask, redirect, url_for, request
import werkzeug
from werkzeug.datastructures import ImmutableMultiDict
import pprint
import pymysql
import requests
import pprint
import re
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning
app = Flask(__name__)
app.secret_key = "secret_key"
global database
global cursor 
database = pymysql.connect("localhost", "root", "Eroshikp", "library")
cursor = database.cursor()

@app.route("/", methods = ['POST', 'GET'])
def root():
    return render_template("Mainpage.html")

@app.route("/login.html", methods = ['POST', 'GET'])
def login_display():
    return render_template("login.html")

@app.route("/home", methods = ['POST', 'GET'])
def home_display():
    return render_template("Mainpage.html")

@app.route("/about", methods = ['POST', 'GET'])
def render_about():
    return render_template("about.html")

@app.route("/contact", methods = ['POST', 'GET'])
def render_contact():
    return render_template("contact.html")

@app.route("/logout", methods = ['POST', 'GET'])
def render_logout():
    session.pop('reader', None)
    return redirect(url_for("index"))

@app.route('/login',methods = ['POST', 'GET'])
def index():
    global database
    loginSuccess = False
    reader_id = "SELECT READERID FROM READER;"
    cursor.execute(reader_id)
    if request.method == 'POST':
        reader_id = request.form['reader_id']
        if reader_id is None or reader_id == "":
            flash("Kindly enter inputs ...")
            return render_template("login.html")
        for credential in cursor.fetchall():
            if credential[0] == int(reader_id):
                loginSuccess = True
    
                
    if loginSuccess == True:
        session["reader"] = reader_id
        flash("Login Success !")
        return (render_template("readerview.html"))
        # reader view page with all the functions needs to be returned. 
    else:
        flash("Wrong Credentials !")
        return (render_template("login.html"))
        # same reader login page needs to be returned. 

@app.route('/admin.html', methods = ['POST', 'GET'])
def admin_login_display():
    return render_template("admin.html")
    
@app.route('/admin',methods = ['POST', 'GET'])
def admin():
    loginSuccess = False
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username is None or username == "" or password is None or password == "":
            flash("Kindly enter inputs ...")
            return render_template("admin.html")
        if username == "admin" and password == "admin_pass":
            loginSuccess = True
                    
    if loginSuccess == True:
        flash ("Admin Login Success")
        return render_template("adminview.html")
        # Admin view page with all the functions needs to be returned. 
    else:
        flash("Wrong Credentials !")
        return (render_template("admin.html"))
    
@app.route('/docsearch.html', methods = ['POST', 'GET'])
def render_docsearch():
    return (render_template("docsearch.html"))

@app.route('/docsearch', methods = ['POST', 'GET'])
def doc_search():
    global database
    global cursor 
    cursor = database.cursor()
    if request.method == 'POST':
        search_type = request.form['search_type']
        search_key = request.form['search_key']
        if search_type is None or search_key is None or search_key == "":
            flash ("Kindly enter the values for search !")
            return render_template("docsearch.html")
        
        output = [["Document ID", "Document Title", "Document Publish Date", "Document Publisher ID"]]
        if search_type == "docid":
            sql = "select * from document where docid = " + str(search_key)
            if cursor.execute(sql) != 0:
                for value in cursor.fetchall():
                    output.append(list(value))
            else:
                cursor.close()
                flash("No such DocID exists ... Enter the right one")
                return render_template("docsearch.html")
        elif search_type == "title":
            sql = "select * from document where title like " + "'%" + search_key + "%';"
            if cursor.execute(sql) != 0:
                for value in cursor.fetchall():
                    output.append(list(value))
            else:
                cursor.close()
                flash("No such Document Title exists ... Enter the right one")
                return render_template("docsearch.html")
        elif search_type == "pubname":
            sql = "select * from document where publisherid in (select publisherid from publisher where pubname like " + "'%" + search_key + "%');"
            if cursor.execute(sql) != 0:
                for value in cursor.fetchall():
                    output.append(list(value))
            else:
                cursor.close()
                flash("No such Document Publisher exists ... Enter the right one")
                return render_template("docsearch.html")
        
        cursor.close()   
        database.commit()    
        return render_template("result.html", result = output)
        
@app.route('/doccheckout.html', methods = ['POST', 'GET'])
def render_doccheckout():
    return (render_template("doccheckout.html"))

@app.route('/doccheckout', methods = ['POST', 'GET'])
def doc_checkout():
    global database
    global cursor
    cursor = database.cursor()
    # checking whether the reader is a registered reader...
    if request.method == 'POST':
        reader_id = session['reader']
        res_id = request.form['resid']
        if reader_id is None or reader_id == "" or res_id is None or res_id == "":
            flash("Kindly enter inputs ...")
            return render_template("doccheckout.html")
        sql = "select READERID, DOCID, COPYNO, LIBID from reserves where resnumber = " + str(res_id) + " and readerid = " +  str(reader_id) + ";"
        if cursor.execute(sql) == 0:
            flash ("No such Reservation exixts ... Try again !")
            return render_template("doccheckout.html")
        else:
            output = cursor.fetchall()
            print ("output = ", output)
            reader_id = output[0][0]
            doc_id = output[0][1]
            copy_no = output[0][2]
            lib_id = output[0][3]
            time = datetime.datetime.now()
            borrow_date_time = time.strftime("%Y-%m-%d %H:%M")
            sql_1 = "insert into borrows (READERID, DOCID, COPYNO, LIBID, BDTIME) values (" + str(reader_id) + "," + str(doc_id) + "," + str(copy_no) + "," + str(lib_id) + "," + "'" + str(borrow_date_time) + "'" + ");"
            sql_2 = "delete from reserves where resnumber = " + str(res_id) + ";"
            if cursor.execute(sql_1) != 0 and cursor.execute(sql_2) != 0:
                cursor.close()
                database.commit()
                flash ("Document Check out successful. Kindly make note of your borrow date and time.")
                return render_template("readerview.html")
                
            else:
                flash("The Document  check out is incomplete. Kindly try again");
                return render_template("doccheckout.html")
            
                    
        
        
@app.route('/docreturn.html', methods = ['POST', 'GET'])
def render_docreturn():
    return (render_template("docreturn.html"))

@app.route('/docreturn', methods = ['POST', 'GET'])
def doc_return():
    global database
    global cursor
    cursor = database.cursor()
    if request.method == 'POST':
        reader_id = session['reader']
        borrow_id = request.form['borrid']
        if reader_id is None or reader_id == "" or borrow_id is None or borrow_id == "":
            flash("Kinldy enter inputs ... ")
            return render_template("docreturn.html")
        
        sql = "select * from borrows where bornumber = " + str(borrow_id)
        if cursor.execute(sql) != 0:
            output = cursor.fetchall()
            doc_id = output[0][2]
            copy_no = output[0][3]
            lib_id = output[0][4]
            borrow_date_time = output[0][5]
            return_time = datetime.datetime.now()
            return_time_formatted = return_time.strftime("%Y-%m-%d %H:%M")
            days_difference = (return_time - borrow_date_time).days
            print (doc_id, copy_no, lib_id, borrow_date_time, return_time_formatted, days_difference)
            if days_difference > 20:
                fine = (days_difference - 20 ) * 0.20
            else:
                fine = 0
            sql = "update borrows set RDTIME = '" + str(return_time_formatted) + "', FINE = " + str(fine) + " where BORNUMBER = " + str(borrow_id) + ";"
            print (sql)
            
            sql_copy_status = "update copy set copy_status = \"available\" where docid = " + str(doc_id) + " and copyno = " + str(copy_no) + " and libid = " + str(lib_id) + ";"
            print (sql_copy_status)
            
            if cursor.execute(sql) != 0 and cursor.execute(sql_copy_status) != 0:
                cursor.close()
                database.commit()
                flash ("Document Return was successful !")
                return render_template("readerview.html")
            else:
                flash ("Something went wrong in Document Return ... Kindly try again !")
                return (render_template("docreturn.html"))
            
        else:
            flash("Entered Borrow ID is wrong. Kindly enter the right one. ")
            return render_template("docreturn.html")
        
        
@app.route('/docreserve.html', methods = ['POST', 'GET'])
def render_docreserve():
    return (render_template("docreserve.html"))



@app.route('/docreserve', methods = ['POST', 'GET'])
def doc_reserve(): 
    global database
    global cursor
    cursor = database.cursor()
    if request.method == 'POST':
        reader_id = session['reader']
        doc_id = request.form['docid']
        copy_id = request.form['copyid']
        lib_id = request.form['libid']
        if reader_id is None or reader_id == "" or doc_id is None or doc_id == "" or copy_id is None or copy_id == "" or lib_id is None or lib_id == "":
            flash("Kindly enter the inputs ...")
            return render_template("docreserve.html")
        
        sql_copy_check = "select COPY_STATUS from COPY where DOCID = " + str(doc_id) + " and COPYNO = " + str(copy_id) + " and LIBID = " + str(lib_id) + ";"
        if cursor.execute(sql_copy_check) != 0:
            output = cursor.fetchall()
            if output[0][0] is None or 'available':
                reserve_time = datetime.datetime.now()
                reserve_time_formatted = reserve_time.strftime("%Y-%m-%d %H:%M")
                sql_copy_status_update = "update COPY set COPY_STATUS = 'reserved' where DOCID = " + str(doc_id) + " and COPYNO = " + str(copy_id) + " and LIBID = " + str(lib_id) + ";"
                status_1 = cursor.execute(sql_copy_status_update)
                sql_reserve = "insert into RESERVES (READERID, DOCID, COPYNO, LIBID, DTIME) values (" + str(reader_id) + ", " + str(doc_id) + ", " + str(copy_id) + ", " + str(lib_id) + ", '" + str(reserve_time_formatted) + "');"
                status_2 = cursor.execute(sql_reserve)
                if status_1 != 0 and status_2 != 0:
                    cursor.close()
                    database.commit()
                    flash ("Reservation successful. Kindly borrow the book")
                    return render_template("readerview.html")
                else:
                    cursor.close()
                    flash("Reservation not complete. Kindly try again !")
                    return render_template("docreserve.html")
            else:
                flash("The Requested document is already borrowed or reserved. Kindly look for someother copy of the document. ")
                return render_template("docreserve.html")
            
        else:
            flash("Something went wrong in the system. Kindly try again.")
            return render_template("docreserve.html")
            


@app.route('/fine', methods = ['POST', 'GET'])
def compute_fine():
    global database
    global cursor
    cursor = database.cursor()
    if request.method == 'GET':
        reader_id = session['reader']
        if reader_id is None or reader_id == "":
            flash("Kindly enter the inputs ...")
            return render_template("fine.html")
        print (reader_id)
        sql_borrows = "select BORNUMBER, READERID, DOCID, COPYNO, LIBID, BDTIME from BORROWS where READERID = " + str(reader_id) + ";"
        cursor.execute(sql_borrows)
        output = cursor.fetchall()
        final_output = []
        headings = ["BORROW NUMBER", "READER ID", "DOCUMENT ID", "COPY NUMBER", "LIBRARY ID", "BORROW DATE and TIME", "FINE COMPUTED TILL NOW"]
        final_output.append(headings)
        if(len(output)!=0):
            for values in output:
                borrow_date = values[5] 
                current_date = datetime.datetime.now()
                days = (current_date-borrow_date).days
                if days > 20:
                    fine = (days - 20 ) * 0.2
                else:
                    fine = 0
                values = list(values)
                values.append(fine)
                final_output.append(values)
            flash("Fine Computed as per the current date. ")
            return render_template("result.html", result = final_output)
        
        else:
            flash("No borrows for this reader !")
            return render_template("readerview.html")
            

@app.route('/bookreservelist', methods = ['POST', 'GET'])
def book_reserve_list():
    global database
    global cursor
    cursor = database.cursor()
    if request.method == 'GET':
        reader_id = session['reader']
        print (reader_id)
        
        sql_reserves = "select DOCID, COPYNO, LIBID from reserves where READERID = " + str(reader_id) + ";"
        sql_borrows = "select DOCID, COPYNO, LIBID from borrows where READERID = " + str(reader_id)
        status_1 = cursor.execute(sql_reserves)
        status_2 = cursor.execute(sql_borrows)
        if status_1 !=0 or status_2 != 0:
            output_1 = cursor.fetchall()
            output_2 = cursor.fetchall()
            final_output = []
            headings = ["DOCUMENT ID", "COPY NUMBER", "LIBRARY ID", "STATUS"]
            final_output.append(headings)
            for values in output_1:
                values = list(values)
                values.append("RESERVED")
                final_output.append(values)
            for values in output_2:
                values = list(values)
                values.append("BORROWED")
                final_output.append(values)
            
            return render_template("result.html", result = final_output)
        else:
            flash("You have no outstanding borrows/reserves at this time. ")
            return render_template("readerview.html")
            
@app.route('/publisherdocs.html', methods = ['POST', 'GET'])
def render_publisherdocs():
    return (render_template("publisherdocs.html"))


@app.route('/publisherdocs', methods = ['POST', 'GET'])
def publisher_docs():
    global database
    global cursor
    cursor = database.cursor()
    if request.method == "POST":
        reader_id = session['reader']
        print (reader_id)
        pub_name = request.form['pubname']
        sql = "select * from document where publisherid in (select publisherid from publisher where pubname like " + "'%" + pub_name + "%');"
        output = []
        heading = ["DOCUMENT ID", "DOCUMENT TITLE", "DOCUMENT PUBLISH DATE", "DOCUMENT PUBLISHER ID"]
        output.append(heading)
        if cursor.execute(sql) != 0:
            for value in cursor.fetchall():
                output.append(list(value))
            return render_template("result.html", result = output)
        
        else:
            flash("No such publisher exists ... try again !")
            return render_template("publisherdocs.html")
            

@app.route('/adddoccopy.html', methods = ['POST', 'GET'])
def render_adddoccopy():
    return (render_template("adddoccopy.html"))


@app.route('/adddoccopy', methods = ['POST', 'GET'])
def add_doc_copy():
    global database
    global cursor
    cursor = database.cursor()
    if request.method == 'POST':
        doc_id = request.form['docid']
        copy_no = request.form['copyno']
        lib_id = request.form['libid']
        position = request.form['position']
        if doc_id is None or doc_id == "" or copy_no is None or copy_no == "" or lib_id is None or lib_id == "" or position is None or position == "":
            flash("Kindly enter valid inputs ...")
            return render_template("adddoccopy.html")
        sql_check = "select * from COPY where DOCID = " + str(doc_id) + " and COPYNO = " + str(copy_no) + " and LIBID = " + str(lib_id) + ";"
        if cursor.execute(sql_check) == 0:
            sql_insert = "insert into COPY values (" + str(doc_id) + ", " + str(copy_no) + ", " + str(lib_id) + ", '" + str(position) + "', 'available');"
            if cursor.execute(sql_insert) != 0:
                cursor.close()
                database.commit()
                flash("Document Copy added successfully !")
                return render_template("adminview.html")
            else:
                flash("Insertion failed ! Try again ")
                return render_template("adddoccopy.html")
        else:
            flash("The document copy already exixts ... try inserting new copy")
            return render_template("adddoccopy.html")
            
        
@app.route('/searchdoccopy.html', methods = ['POST', 'GET'])
def render_searchdoccopy():
    return (render_template("searchdoccopy.html"))


@app.route('/searchdoccopy', methods = ['POST', 'GET'])
def search_doc_copy():
    global database
    global cursor
    cursor = database.cursor()
    if request.method == 'POST':
        doc_id = request.form['docid']
        copy_no = request.form['copyno']
        lib_id = request.form['libid']
        if doc_id is None or doc_id == "" or copy_no is None or copy_no == "" or lib_id is None or lib_id == "":
            flash("Kindly enter values in the text boxes ... ")
            return render_template("searchdoccopy.html")
        sql_check = "select * from COPY where DOCID = " + str(doc_id) + " and COPYNO = " + str(copy_no) + " and LIBID = " + str(lib_id) + ";"
        heading = ["Document ID", "Copy Number", "Library ID", "Position", "Copy Status"]
        final_output = []
        final_output.append(heading)
        if cursor.execute(sql_check) != 0:
            output = cursor.fetchall()
            final_output.append(list(output[0])) 
            print  (final_output)
            return render_template("result.html", result = final_output)
        else:
            flash("No such copy exixts ... try again")
            return render_template("searchdoccopy.html")
        

@app.route('/addnewreader.html', methods = ['POST', 'GET'])
def render_addnewreader():
    return (render_template("addnewreader.html"))      
            

@app.route('/addnewreader', methods = ['POST', 'GET'])
def add_new_reader():
    global database
    global cursor
    cursor = database.cursor()
    if request.method == 'POST':
        reader_id = request.form['readerid']
        reader_type = request.form['rtype']
        reader_name = request.form['rname']  
        reader_address = request.form['raddress']
        if reader_id is None or reader_id == "" or reader_type is None or reader_type == "" or reader_name is None or reader_name == "" or reader_address is None or reader_address == "":
            flash("Kindly enter right values .... ")
            return render_template("addnewreader.html")
        sql = "SELECT READERID FROM READER where READERID = " + str(reader_id) + ";"
        if cursor.execute(sql) == 0:
            sql_insert = "insert into READER values (" + str(reader_id) + ",'" + str(reader_type) + "','" + str(reader_name) + "','" + str(reader_address) + "');"
            if cursor.execute(sql_insert) != 0:
                cursor.close()
                database.commit()
                flash("New Reader Registered Successfully !")
                return render_template("addnewreader.html")
            else:
                flash("Something went wrong during registration, Kindly try again !")
                return render_template("addnewreader.html")
        else:
            flash("This Reader ID already exists ... Try with new reader ID")
            return render_template("addnewreader.html")
        

@app.route('/branchinfo.html', methods = ['POST', 'GET'])
def render_branchinfo():
    return (render_template("branchinfo.html"))   

@app.route('/branchinfo', methods = ['POST', 'GET'])
def branch_info():
    global database
    global cursor
    cursor = database.cursor()
    if request.method == 'POST':
        lib_id = request.form['libraryid']
        if lib_id is None or lib_id == "":
            flash("Kindly enter valid inputs ... ")
            return render_template("branchinfo.html")
        sql = "select * from BRANCH where LIBID = " + str(lib_id) + ";"
        heading = ["Library ID", "Library Name", "Library Location"]
        final_output = []
        final_output.append(heading)
        if cursor.execute(sql) != 0:
            output = cursor.fetchall()
            final_output.append(list(output[0]))
            return render_template("result.html", result = final_output)
        else:
            flash("No such library ID exists ... ")
            return render_template("branchinfo.html")
        
        
@app.route('/frequentborrower.html', methods = ['POST', 'GET'])
def render_frequentborrower():
    return (render_template("frequentborrower.html")) 

@app.route('/frequentborrower', methods = ['POST', 'GET'])
def frequent_borrower():
    global database
    global cursor
    cursor = database.cursor()
    if request.method == 'POST':
        lib_id = request.form['libraryid']
        if lib_id is None or lib_id == "":
            flash("Kindly enter some values ... ")
            return render_template("frequentborrower.html")
        sql = "select readerid,count(*) AS Noofbooksborrowed from library.borrows where libid = " + str(lib_id) + " GROUP BY readerid ORDER BY Noofbooksborrowed DESC;"
        heading = ["Reader ID", "Books Borrowed"]
        final_output = []
        final_output.append(heading)
        if cursor.execute(sql) != 0:
            output = cursor.fetchall()
            for values in output:
                final_output.append(list(values))
            return render_template("result.html", result = final_output)
        else:
            flash("No such library ID exists ... ")
            return render_template("frequentborrower.html")


@app.route('/borrowedbooks.html', methods = ['POST', 'GET'])
def render_frequentbooks():
    return (render_template("borrowedbooks.html")) 

@app.route('/borrowedbooks', methods = ['POST', 'GET'])
def frequent_books():
    global database
    global cursor
    cursor = database.cursor()
    if request.method == 'POST':
        lib_id = request.form['libraryid']
        if lib_id is None or lib_id == "":
            flash("Enter some values ... ")
            return render_template("borrowedbooks.html")
        sql = "select d.docid,d.title from library.borrows b,library.document d where libid = " + str(lib_id) + " and b.docid=d.docid  GROUP BY d.docid;"
        heading = ["Document ID", "Document Title"]
        final_output = []
        final_output.append(heading)
        if cursor.execute(sql) != 0:
            output = cursor.fetchall()
            for values in output:
                final_output.append(list(values))
            return render_template("result.html", result = final_output)
        else:
            flash("No such library ID exists ... ")
            return render_template("borrowedbooks.html")
        
        
@app.route('/popularbooks.html', methods = ['POST', 'GET'])
def render_popularbooks():
    return (render_template("popularbooks.html")) 

@app.route('/popularbooks', methods = ['POST', 'GET'])
def popular_books():
    global database
    global cursor
    cursor = database.cursor()
    if request.method == 'POST':
        lib_id = request.form['libraryid']
        year = request.form['year']
        if lib_id is None or lib_id == "" or year is None or year == "":
            flash("Enter some values ... ")
            return render_template("borrowedbooks.html")
        sql = "select d.docid,d.title from library.borrows b,library.document d where libid = " + str(lib_id)+ " and b.docid=d.docid and b.bdtime like '" + str(year) + "-%' GROUP BY d.docid;"
        heading = ["Document ID", "Document Title"]
        final_output = []
        final_output.append(heading)
        if cursor.execute(sql) != 0:
            output = cursor.fetchall()
            for values in output:
                final_output.append(list(values))
            return render_template("result.html", result = final_output)
        else:
            flash("No such library ID exists ... ")
            return render_template("popularbooks.html")


@app.route('/readerfine', methods = ['POST', 'GET'])
def avg_reader_fine():
    global database
    global cursor
    cursor = database.cursor()
    if request.method == 'GET':
        sql_reader = "select READERID from READER;"
        final_output = []
        heading = ["Reader ID", "Average Fine"]
        final_output.append(heading)
        reader_list = []
        if cursor.execute(sql_reader) != 0:
            output = cursor.fetchall()
            for values in output:
                reader_list.append(values[0])
            for reader_id in reader_list:
                print ("reader ID = ", reader_id)
                sql_borrows = "select BDTIME, FINE from BORROWS where readerid = " + str(reader_id) + ";"
                fine = 0
                borrow_count = 0
                if cursor.execute(sql_borrows) != 0:
                    output = cursor.fetchall()
                    print ("Output = ", output)
                    for values in output:
                        if values[1] is not None:
                            fine = fine + values[1]
                            borrow_count = borrow_count + 1
                        else:
                            now_time = datetime.datetime.now()
                            days = (now_time - values[0]).days
                            if (days > 20):
                                fine = fine + (( days - 20 ) * 0.20)
                                borrow_count = borrow_count + 1
                            else:
                                fine = 0
                    
                    computed_list = [reader_id, fine/borrow_count]
                    final_output.append(computed_list)
                else:
                    computed_list = [reader_id, "No Fine"]
                    final_output.append(computed_list)
        
        return render_template("result.html", result = final_output)
                                
                            
                            
            
    
    