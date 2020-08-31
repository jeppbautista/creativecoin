class Config:
    DEBUG = False
    TEMPLATE = "template"

    SECRET_KEY = "233c752bf9ebc2ec932c5974aa8dc8e4"
    SECRET_SALT_KEY = "8DB1B03A7D6DA536EB79BB5D2B3EFAB2"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SMTP = "mail.creativecoin.net"
    SMTP_PORT = 465
    SMTP_USER = "autoemail@creativecoin.net"
    SMTP_PASS = "7270TBCcsbn7270###$$$"
    SMTP_FROM = "CreativeCoin<autoemail@creativecoin.net>"

    # ADMIN_MAIL = "clcefiedu@gmail.com"
    ADMIN_MAIL = "tbcmsapp@gmail.com"
    TEST_TO = "jeppbautista@gmail.com"
    REFERRAL_PCT = 0.05

    FILE_USD = "creativecoin/repo-usd.txt"
    FILE_GRAIN = "creativecoin/repo-grain.txt"


class DevConfig(Config):
    DEBUG = True
    # LOGIN_DISABLED = True
    
    SERVER_NAME = "localhost:5000"
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://cisateducation:{password}@206.72.201.67:3306/cisatedu_ccn_test".format(
                                password="7270TBCcsbn7270###$$$")

    COINPAYMENTS_MERCHANT_ID = "8c79258b6bc2cf3541da99725f6efe8d"
    COINPAYMENTS_PUBLIC_KEY = "71c298dabdaf11759bc427d318c52e87b0163633386ac7d1367990ebe038072e"
    COINPAYMENTS_PRIVATE_KEY = "a3b179B5f4CFeC1f25f69C1B391E0446e78b6D6943e38Ab32644F2112203228f"


class ProdConfig(Config):
    # LOGIN_DISABLED = False
    SERVER_NAME = "creativecoin.net"
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://cisateducation:{password}@206.72.201.67:3306/cisatedu_ccn_test".format(
                                password="7270TBCcsbn7270###$$$")
    #TODO For Production 
    COINPAYMENTS_MERCHANT_ID = "8c79258b6bc2cf3541da99725f6efe8d"                     
    COINPAYMENTS_PUBLIC_KEY = "71c298dabdaf11759bc427d318c52e87b0163633386ac7d1367990ebe038072e"
    COINPAYMENTS_PRIVATE_KEY = "a3b179B5f4CFeC1f25f69C1B391E0446e78b6D6943e38Ab32644F2112203228f"