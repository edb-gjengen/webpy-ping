# Configuration

# Url shortening
BITLY_USERNAME = '' # username ('' = disabled)
BITLY_API_KEY = ''

DEPLOY_SCRIPT_PATH = '/opt/git-deploy.sh'
# Mappings from allowed url to deploy path.
REPOS = {
        'http://example.com': '/var/www/site',
    }
# Tuple with hostname and port
IRC_BOT_HOST = ('localhost',55666) 
