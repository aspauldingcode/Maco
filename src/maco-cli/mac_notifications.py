import codecs
import sqlite3
import sys
import os
import uuid
import biplist
import datetime
import subprocess
from biplist import *

def find_notification_db():
    try:
        result = subprocess.run(
            "lsof -p $(ps aux | grep -m1 usernoted | awk '{ print $2 }') | awk '{ print $NF }' | grep 'db2/db$' | xargs dirname",
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        db_path = result.stdout.strip()
        if db_path:
            return os.path.join(db_path, 'db')
        else:
            print("Notification Center database directory not found.")
            sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error finding Notification Center database: {e}")
        sys.exit(1)

def RemoveTabsNewLines(str):
    try:
        return str.replace("\t", " ").replace("\r", " ").replace("\n", "")
    except:
        pass
    return str
    
def ReadMacAbsoluteTime(mac_abs_time): # Mac Absolute time is time epoch beginning 2001/1/1
    '''Returns datetime object, or empty string upon error'''
    try:
        return datetime.datetime.utcfromtimestamp(mac_abs_time + 978307200)
    except:
        pass
    return ''

def GetText(string_or_binary):
    '''Converts binary or text string into text string. UUID in Sierra is now binary blob instead of hex text.'''
    uuid_text = ''
    if uuid_text:
        try:
            if type(string_or_binary) == bytes:
                #hex_str = ''.join('{:02X}'.format(ord(x)) for x in string_or_binary)
                uuid_text = str(uuid.UUID(bytes=string_or_binary)).upper()
            else:
                uuid_text = string_or_binary.upper()
        except Exception as ex:
            print('Error trying to convert binary value to hex text. Details: ' + str(ex))
    return uuid_text

def GetDbVersion(conn):
    try:
        cursor = conn.execute("SELECT value from dbinfo WHERE key LIKE 'compatibleVersion'")
        for row in cursor:
            print('db compatibleversion = {}'.format(row[0]))
            return int(row[0])
    except Exception as ex:
        print("Exception trying to determine db version : " + str(ex))
    return 15 #old version

def Parse_ver_17_Db(conn, inputPath, outputPath):
    '''Parse High Sierra's notification db'''
    try:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT (SELECT identifier from app where app.app_id=record.app_id) as app, "\
                                "uuid, data, presented, delivered_date FROM record")

        try:
            print ("Trying to create file '" + outputPath + "' for writing..")
            with codecs.open(outputPath, 'w', encoding='utf-16') as csv:
                csv.write ("Time\tShown\tBundle\tAppPath\tUUID\tTitle\tSubTitle\tMessage\r\n")
                rowcount = 0
                try:
                    for row in cursor:
                        rowcount += 1
                        try:
                            plist = readPlistFromString(row['data'])
                            try:
                                req = plist['req']
                                title = RemoveTabsNewLines(req.get('titl', ''))
                                subtitle = RemoveTabsNewLines(req.get('subt', ''))
                                message = RemoveTabsNewLines(req.get('body', ''))
                            except Exception as ex: print('Error reading field req - ' + str(ex))
                        except (InvalidPlistException, NotBinaryPlistException, Exception) as e:
                            print ("Invalid plist in table." + str(e) )
                        try:
                            csv.write ('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\r\n' %(ReadMacAbsoluteTime(row['delivered_date']), row['presented'], row['app'], '', GetText(row['uuid']), title, subtitle, message))
                        except Exception as ex:
                            print ("Error while writing to file, error details:\n", str(ex))
                    print ("Finished processing! Wrote " + str(rowcount) + " rows of data.")                      
                except Exception as ex:
                    print ("Db cursor error while reading file " + inputPath)
                    print(str(ex))
        except Exception as ex:
            print ("Failed to create file '" + outputPath + "' for writing. Is it locked? Perhaps a permissions issue")
            print ("Error details: " , ex.args)
    except Exception as ex:
        print ("Sqlite error - \nError details: \n" + str(ex))

def ProcessNotificationDb(inputPath, outputPath):
    try:
        conn = sqlite3.connect(inputPath)
        print ("Opened database successfully");

        if GetDbVersion(conn) >= 17: # High Sierra
            Parse_ver_17_Db(conn, inputPath, outputPath)
            conn.close()
            return

        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT datetime(date_presented + 978307200, 'unixepoch') as time_utc, "
                                "datetime(date_presented + 978307200, 'unixepoch', 'localtime') as time, "
                                "actually_presented AS shown, "
                                "(SELECT bundleid from app_info WHERE app_info.app_id = presented_notifications.app_id)  AS bundle, "
                                "(SELECT last_known_path from app_loc WHERE app_loc.app_id = presented_notifications.app_id)  AS appPath, "
                                "(SELECT uuid from notifications WHERE notifications.note_id = presented_notifications.note_id) AS uuid, "
                                "(SELECT encoded_data from notifications WHERE notifications.note_id = presented_notifications.note_id) AS dataPlist "
                                "from presented_notifications ")

        # Print to file
        try:
            print ("Trying to create file '" + outputPath + "' for writing..")
            with codecs.open(outputPath, 'w', encoding='utf-16') as csv:
                csv.write ("Time\tShown\tBundle\tAppPath\tUUID\tTitle\tSubTitle\tMessage\r\n")
                rowcount = 0
                for row in cursor:
                    rowcount += 1
                    title    = ''
                    subtitle = ''
                    message  = ''
                    try:
                        plist = readPlistFromString(row['dataPlist'])
                        title_index = 2 # by default
                        subtitle_index = -1 # mostly absent!
                        text_index = 3 # by default
                        try:
                            title_index = int(plist['$objects'][1]['NSTitle'])
                        except: pass
                        try:
                            subtitle_index = int(plist['$objects'][1]['NSSubtitle'])
                        except: pass
                        try:
                            text_index = int(plist['$objects'][1]['NSInformativetext'])
                        except: pass
                        try:
                            title = RemoveTabsNewLines(plist['$objects'][title_index])
                        except: pass
                        try:
                            subtitle = RemoveTabsNewLines(plist['$objects'][subtitle_index]) if subtitle_index > -1 else ""
                        except: pass                        
                        try:
                            message = RemoveTabsNewLines(plist['$objects'][text_index])
                        except: pass
                    except (InvalidPlistException, NotBinaryPlistException, Exception) as e:
                        print ("Invalid plist in table.", e )
                    try:
                        csv.write ('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\r\n' %(ReadMacAbsoluteTime(row['time']), row['shown'], row['bundle'], row['appPath'], row['uuid'], title, subtitle, message))
                    except Exception as ex:
                        print ("Error while writing to file, error details:\n", ex.args)
                print ("Finished processing! Wrote " + str(rowcount) + " rows of data.")
        except Exception as ex:
            print ("Failed to create file '" + outputPath + "' for writing. Is it locked? Perhaps a permissions issue")
            print ("Error details: " , ex.args)
        conn.close()
    except Exception as ex:
        print ("Failed to open database, is it a valid Notification DB? \nError details: ", ex.args)

## Main Program
print ("Using Python %i.%i" % (sys.version_info.major, sys.version_info.minor) )

# Set default output path
outputPath = "/tmp/Maco-notifications.csv"
inputPath = find_notification_db()

try:
    if os.path.exists(inputPath):
        ProcessNotificationDb(inputPath, outputPath)
    else:
        print(f"Error: Failed to find file at specified path. Path was: {inputPath}")
        print("Please make sure you have the necessary permissions to access the Notification Center database.")
        print("You may need to grant Full Disk Access to your terminal application in System Preferences > Security & Privacy > Privacy.")
except Exception as ex:
    print(f"Error: Unknown exception, error details are: {str(ex)}")
