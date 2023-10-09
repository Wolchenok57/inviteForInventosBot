
import sqlite3

f = open('inventosbase.db', 'w')
f.write('')
f.close()

connection = sqlite3.connect('inventosbase.db')
cursor = connection.cursor()
cursor.execute('CREATE TABLE `User` (`id` INTEGER  PRIMARY KEY , `name1` TEXT NOT NULL , `name2` TEXT NOT NULL , `chat_id` int(11) NOT NULL, `telega_name` int(11) NOT NULL, `telega_tag` int(11) NOT NULL);')
cursor.execute('CREATE TABLE `Queue` (`id` INTEGER  PRIMARY KEY AUTOINCREMENT , `idMeeting` INT NOT NULL , `idUser` INT NOT NULL, `guestOf` INT NOT NULL , `payStatus` BOOLEAN NOT NULL DEFAULT FALSE , `payDate` DATE NULL , `attendStatus` BOOLEAN NOT NULL DEFAULT TRUE , `isNewAdmin` BOOLEAN NOT NULL DEFAULT FALSE , UNIQUE (idUser, `idMeeting`));')
cursor.execute('CREATE TABLE `Meeting` (`id` INTEGER  PRIMARY KEY AUTOINCREMENT , `name` TEXT NOT NULL , `idCreator` INT NOT NULL , `allowNotification` BOOLEAN NOT NULL DEFAULT TRUE , `notificationText` TEXT NULL , `notificationTime` INT NULL , `maxUsers` INT NOT NULL , `cost` FLOAT NULL , `date` DATE NOT NULL );')

connection.commit()
connection.close()
