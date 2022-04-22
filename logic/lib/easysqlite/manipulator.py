from __init__ import *


class EasySqlite:

    def __init__(self, file: str = ""):
        """
        <FILE> : Path/Directory to your database file. \"New file is generated automatically if file doesn't exists\"
        """
        self.database = file

    # create new table and add columns
    def add_columns(self, new_table: str, columns: tuple):
        """
        <NEW_TABLE> : Creates new table for your data.
        \n
        <COLUMNS> : Columns for which you'd want to insert in your table. \"e.g [name, lastname, gender, phonenumber]\"
        """

        # continue if columns type is tuple
        connect = sqlite3.connect(self.database)
        cursor = connect.cursor()
        
        try:
            cursor.execute("""
            CREATE TABLE {} {}
        """.format(new_table, columns))

        except sqlite3.Error as error:
            return error

        connect.commit() # save
        connect.close() # close

    # add row with data in the database
    def add_values(self, table: str, values: tuple):
        """
        <TABLE> : Target table to add values to.
        \n
        <VALUES> : Values or data you want to add to columns.
        """
        connect = sqlite3.connect(self.database)
        cursor = connect.cursor()
        
        try:
            cursor.execute("""
            INSERT INTO {} VALUES {}
        """.format(table, values))

        except sqlite3.Error as error:
            raise error

        connect.commit() # save
        connect.close() # close
    
    # add many values to the business
    def add_many_values(self, table: str, placeholders: str, values: tuple):
        """
        <TABLE> : Target table to add values to.\n
        <PLACEHOLDERS> : These are placeholder \"(?,?,?)\". Use these question-marks to declare how many values should be expected.\n
        ____________PLACEHOLDERS-EXAMPLE____________
        \n
        (?,?,?,?) this means the database should expect 2 <tuple> objects like this. \n\n[('name', 'lastname', 'gender', phonenumber), ('name', 'lastname', 'gender', phonenumber)]
        """

        connect = sqlite3.connect(self.database)
        cursor = connect.cursor()
        
        try:
            cursor.executemany("""
            INSERT INTO {} VALUES {}
        """.format(table, placeholders), values)

        except sqlite3.Error as error:
            raise error

        connect.commit() # save
        connect.close() # close

    # TODO: FIX WHOLE METHOD
    def update_values(self, table, old_value, old_column, column, value):
        """
        <TABLE> : Target table to add values to.\n
        <ROWID> : Sqlite3-rowid specifies the target-row to manipulate, It can be any interger from 1^.
        """
        connect = sqlite3.connect(self.database)
        cursor = connect.cursor()
        
        try:
            cursor.execute(f"""
            UPDATE {table} SET {column} = {value} WHERE {old_column} LIKE {old_value}
        """)

        except sqlite3.Error as error:
            raise error

        connect.commit() # save
        connect.close() # close

    # TODO: REMOVE VALUES USING COLUMNS NOT ROWID
    # remove row from the database
    def remove_values(self, table: str, rowid: int):
        """
        <TABLE> : Target table to add values to.\n
        <ROWID> : Sqlite3-rowid specifies the target-row to manipulate, It can be any interger from 1^.
        """
        connect = sqlite3.connect(self.database)
        cursor = connect.cursor()
        
        try:
            cursor.execute("""
            DELETE from {} WHERE rowid = {}
        """.format(table, rowid))

        except sqlite3.Error as error:
            raise error

        connect.commit() # save
        connect.close() # close

    # search database for specified data
    def find(self, table: str, column: str, value: str):
        """
        <TABLE> : Target table to find data from.\n
        <COLUMN> : Column to find value from.\n
        <VALUE> : Value to find from the database.\n
        ____________________DESCRIPTION____________________
        \n
        To manipulate data found from your database, Assign function \"find()\" to a 
        variable like this \"result = find(table, column, value)\"
        \n
        print(result) \"This should print data found from your database\"
        """
        
        try:
            with open(self.database) as targetDatabase:
                connect = sqlite3.connect(self.database)
                cursor = connect.cursor()
                
                try:
                    cursor.execute("""
                    SELECT * FROM {} WHERE {} LIKE '{}'
                """.format(table, column, value))
                    results = cursor.fetchall()

                    connect.commit() # save
                    connect.close() # close
                    return results # search results

                # error
                except sqlite3.Error as error:
                    raise error
            
        except IOError as error:
            if error.errno != errno.ENOENT:
                raise error
