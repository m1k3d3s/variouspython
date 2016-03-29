#!/usr/bin/python
import os,time
import datetime
import MySQLdb
import sys
import re
import smtplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

#global date variable to be used in file names
date = datetime.date.today().strftime("%Y%m%d")

#get the list of files(no sub dir) in logfiledir
def getdirfiles():
    logfiledir = ("/log/file/dir/")   #modify this line
    filename = 'logfileinfo'
    files = [f for f in os.listdir(logfiledir) if os.path.isfile(os.path.join(logfiledir,f))]
    erroroutfile = open('/tmp/logfilescripterrors.txt','w')
    try:
        outfile = open('/tmp/'+filename+date+'.csv','w')
    except IOError as e:
        erroroutfile.write("I/O error({0}): {1}".format(e.errno, e.strerror))
    except ValueError:
        erroroutfile.write("Issue with values of csv file")
    except:
        erroroutfile.write("Unexpected error. Could not continue")

    outfile.write("filename,filesize,filecreationdate\n")

    for fname in files:
        size = os.path.getsize(logfiledir+fname)
        fulldate = time.ctime(os.path.getctime(logfiledir+fname))
        a = fname.split('.')
        filedate=a[-1]
        outfile.write(fname+','+str(size)+','+str(filedate)+'\n')

    erroroutfile.close()
    outfile.close()

#def getfileowner():
    
#def setlogthreshold():

#find logs greater than 20MB(20971520 bytes) and create local file in /tmp
def getlogfileresults():
    defaultsize = 20971520
    f_date = datetime.date.today().strftime("%Y-%m-%d")
    results = 'logfileresults'
    resultsfile=open('/tmp/'+results+date+'.csv','w')
    res_file_name='/tmp/'+results+date+'.csv'
    db=MySQLdb.connect("server","user","pwd","table")   #modify this line
    #sql = """select * from vmlogsizes where logsize > %s""",(defaultsize)
    try:
        resultsfile.write("VM name, vm log size(bytes), file created date\n")
        cursor = db.cursor()
        cursor.execute("select * from vmlogsizes where logsize > %s and logdate=%s",(defaultsize,f_date))
        data = cursor.fetchall()
        for name,logsize,logdate in data:
            resultsfile.write(str(name)+', '+str(logsize)+', '+str(logdate)+'\n')
    except:
        resultsfile.write("Connection failed. Please check DB")
    finally:
        db.close()
    
    resultsfile.close()
    send_email("user@email.com",res_file_name) #modify this line

#when info file is created load infile to feedback.vmlogsizes Db
def dbinsert():
    dbinfile=MySQLdb.connect("server","user","pwd","table", local_infile = 1) #modify this line
    lfi_name='/tmp/logfileinfo'+date+'.csv'
    try:
        cursor = dbinfile.cursor()
        cursor.execute("LOAD DATA LOCAL INFILE %s REPLACE INTO TABLE vmlogsizes FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n' IGNORE 1 LINES",(lfi_name))
    except:
        dbinfile.rollback()
        print "Did not load local infile. Please check Db connection\n"
    finally:
        dbinfile.commit()
        dbinfile.close()


def send_email(userEmail, filename):
    sender="user@email.com" #modify this line
    toaddr = [userEmail]
    #toaddr = [userEmail, sender]
    #if(userEmail):
    if re.match("^[a-zA-Z0-9._%-]+@[a-zA-Z0-9._%-]+.[a-zA-Z]{2,6}$", userEmail):
        msg = MIMEMultipart()
        with open(filename,'r') as fp:
            attachment=MIMEText(fp.read())
        msg.attach(attachment)
        msg['Subject'] = date + " Log file overage email - Default 20 MB"
        msg['From'] = sender
        msg['To'] = userEmail
        #msg['Cc'] = sender 
        s=smtplib.SMTP('localhost')
        s.sendmail(sender,toaddr,msg.as_string())
        fp.close
        s.quit()
    else:
        print "Unable to email username and password to user."

getdirfiles()
dbinsert()
getlogfileresults()

