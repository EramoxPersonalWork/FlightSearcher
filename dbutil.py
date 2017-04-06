import xml.sax
class LocaleHandler(xml.sax.ContentHandler):
   def __init__(self):
      self.Code = ""
      self.Name = ""

def insert_into_db (table, format, array_data):
        import MySQLdb

        db = MySQLdb.connect("localhost","root","root","testdb" )
        cursor = db.cursor()

        # Prepare SQL query to INSERT a record into the database.
        sql = "INSERT INTO " + table + " " + format + " VALUES " + data_to_insert
        try:
                # Execute the SQL command
                cursor.execute(sql)
                # Commit your changes in the database
                db.commit()
        except:
                # Rollback in case there is any error
                db.rollback()

        # disconnect from server
        db.close()
