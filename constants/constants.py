COLLECTIONS = ['users']
MONGO_MONTHLY_DATES = ['2015-08-04','2015-10-03','2015-12-01']
MONGO = 'mongo'
MYSQL = 'mysql'
DUMPS_START_DATE = {
    MONGO: '2015-08-04',
    MYSQL: '2013-10-12'
}
MONGO_MONTHLY_DUMPS_URLS = {
    'users': 'http://ghtorrent-downloads.ewi.tudelft.nl/mongo-full/users-dump.'
}
MONGO_DAILY_DUMPS_URL = 'http://ghtorrent-downloads.ewi.tudelft.nl/mongo-daily/mongo-dump-'
MYSQL_MONTHLY_DUMPS_URL = 'http://ghtorrent-downloads.ewi.tudelft.nl/mysql/mysql-'
DUMPS_DATE_PATH = {
    MONGO: 'dumps/mongo/date.txt'
    MYSQL: 'dumps/mysql/date.txt'
}