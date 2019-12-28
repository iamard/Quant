#import shioaji as sj
#TBD

class Sinopac(BrokerBase):
    def __init__(self):
        super().__init__()

        #self.api = sj.Shioaji(backend = 'http', simulation = False)
        
    #def login(self):
        #self.api.login(person_id = config.person_id , passwd = config.password)
        #print(api.fut_account)
        #self.api.list_accounts()
        #pass

if __name__ == '__main__':
    broker = Sinopac()
    broker.login()
