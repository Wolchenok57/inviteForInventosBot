import datetime
import sqlite3

conn = sqlite3.connect('inventosbase.db')
cur = conn.cursor()

cur.execute('INSERT INTO `Meeting` VALUES(NULL, ?, ?, ?, ?, ?, ?, ?, ?)', ('test хз', 2041547209, 1, '456ggg', 1, 1, 1.0, (datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime('%Y-%m-%d %H:%M:%S')))
print(cur.lastrowid)
cur.execute('INSERT INTO `Queue` VALUES(NULL, ?, ?, ?, ?, ?, ?, ?);', (cur.lastrowid, 2041547209, 2041547209, False, None, True, True))
conn.commit()
