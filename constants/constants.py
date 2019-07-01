COLLECTIONS = ['users']
MONGO_MONTHLY_DATES = ['2015-08-04','2015-10-03','2015-12-01']
MONGO = 'mongo'
MYSQL = 'mysql'
MONGO_DAILY_DUMPS_START_DATE = '2015-12-02'
DUMPS_START_DATE = {
    MONGO: '2015-08-04',
    MYSQL: '2015-09-25'
}
MONGO_MONTHLY_DUMPS_URLS = 'http://ghtorrent-downloads.ewi.tudelft.nl/mongo-full/'
MONGO_DAILY_DUMPS_URL = 'http://ghtorrent-downloads.ewi.tudelft.nl/mongo-daily/mongo-dump-'
MYSQL_MONTHLY_DUMPS_URL = 'http://ghtorrent-downloads.ewi.tudelft.nl/mysql/mysql-'
MYSQL_TABLES = [
        'users',
        'organization_members',
        'projects',
        'project_members',
        'project_languages',
        'commits',
        'commit_parents',
        'project_commits',
        'commit_comments',
        'followers',
        'watchers',
        'pull_requests',
        'pull_request_history',
        'pull_request_commits',
        'pull_request_comments',
        'issues',
        'issue_events',
        'issue_comments',
        'repo_labels',
        'issue_labels'
]
