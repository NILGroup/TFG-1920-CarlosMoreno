from googleapiclient.discovery import build
import config
import auth

def main():
    """
    Analyse the emails of the user and obtain the style metrics
    """
    #Creation of a Gmail resource
    service = build('gmail', 'v1',
        credentials = auth.get_credentials(config.SCOPES, config.CLIENT_SECRET_FILE))


if __name__ == '__main__':
    main()