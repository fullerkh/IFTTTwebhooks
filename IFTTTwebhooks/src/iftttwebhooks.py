import json 
from base64 import b64encode
from urllib.parse import urlencode
from urllib.request import Request, urlopen, ProxyHandler, build_opener, install_opener, urlretrieve
import datetime

#functions 
def DataGrab(file):
    # opens json file and return the data
    with open(file) as json_data:
        data = json.load(json_data)
        return data 
    
def removekey(d, key): 
    #given the dictionary and the key remove key from dictionary and return the dictionary
    r = dict(d)
    del r[key]
    return r

    
class Shooting:
    def __init__(self,neighborhood = "unknown",victims = 0, fatality = "unknown", location = []):
        if fatality not in ("fatal","nonfatal","fatal and nonfatal","unknown") or type(neighborhood)!= str or type(location) != list or type(victims) != int :
            raise ValueError()        
        self.neighborhood = neighborhood
        self.victims = victims
        self.fatality = fatality
        self.location = location
        self.count = 1
    
    def getNieghborhood(self):
        return self.neighborhood
    def setNeighborhood(self,neighborhood):
        self.neighborhood=neighborhood
    def getVictims(self):
        return self.victims
    def addVictims(self,victims):
        self.victims += victims    
    def setVictims(self,victims):
        self.victims = victims  
    def getFatality(self):
        return self.fatality
    def setFatality(self,fatality):
        self.fatality=fatality
    def updateFatality(self,fatality):
        if self.fatality != fatality:
            self.fatality = "fatal and nonfatal"
    def getLocation(self):
        return self.location
    def setLocation(self,location):
        self.location = location
    def addLocation(self, location):
        self.location.append(location)
    def getCount(self):
        return self.count
    def addCount(self):
        self.count += 1 
    def setCount(self,count):
        self.victims = count  
        
def yesterdayData(allData, yesterday):
    # select our chosen data
    yesterdayData = []
    for incident in allData:
        # will grab data for all records
        #keep.append(incident)
        #raw data filter
        if incident.get("datetime")[0:10] == "2013-03-20": # replace second date with yesterday
                    yesterdayData.append(incident)
    return yesterdayData
def selectAttributes(data):
    edits = []
    for dictionary in data:
        for key in dictionary:
            if key != "race" and key != "inclocation_x" and key != "sex" and key != "type" and key != "neighborhood" and key != "datetime" and key != "viccount":
                dictionary = removekey(dictionary,key)
        edits.append(dictionary)
    return edits

def populate(oldConfiguration):
    newConfiguration = {}
    for dictionary in oldConfiguration:  
        if dictionary["neighborhood"] in newConfiguration: 
            #edit shootings in shooing list
            newConfiguration[dictionary["neighborhood"]].addVictims(int(dictionary["viccount"]))
            newConfiguration[dictionary["neighborhood"]].updateFatality(dictionary["type"].lower())
            newConfiguration[dictionary["neighborhood"]].addLocation(dictionary["inclocation_x"])
            newConfiguration[dictionary["neighborhood"]].addCount()
        else: 
            #add new shooting to shootings dictionary
            newConfiguration[dictionary["neighborhood"]] =  Shooting(dictionary["neighborhood"],int(dictionary["viccount"]), dictionary["type"].lower(), [dictionary["inclocation_x"]])
    return newConfiguration

def formatEmail(neighborhoods, victims, fatality, numberOfShootings):
    
    emailH = "" # will be email title 
    emailB = [] # will be email body
    
    neighborStr = ""
    i = 0 
    while i < len(neighborhoods):
        if len(neighborhoods) == 1:
            neighborStr += neighborhoods[i].title().strip()
            break
        if len(neighborhoods) != 1 and i+1 == len(neighborhoods):
            neighborStr += "and " +neighborhoods[i].title()
            break
        neighborStr += neighborhoods[i].title() + ", "
        i+=1

    emailH = "There has been a Shooting in " + neighborStr
    if len(neighborhoods) > 1 : 
        emailH = "There have been Shootings in " + neighborStr

    emailB = [("Yestday there were "+ str(numberOfShootings)+" shootings in " +  neighborStr)+".", 
                ("\nThere were ", str(victims) + " " + fatality, " victims."),
                ("\nfor more information please visit the Cincinnati Shootings Insight at: \nhttps://insights.cincinnati-oh.gov/stories/s/xw7t-5phj/")]

    if numberOfShootings ==1: 
        emailB[0] = "Yestday there was " +  str(numberOfShootings) + " shooting in " +  neighborStr+"."

    if victims == 1:
        emailB[1] = "\nThere was " + str(victims) + " " + fatality + " victim."
        
    #print(emailH)
    #print(*emailB)
    
    return [emailH, ''.join(emailB)]

def post(subject,body):
    # if there was a shooting push the data to the open data portal
    # this is about where I'm at with the actual data. Could I try to spoof a browser with a header? how do I send header information? 
    
    #create the object, assign it to a variable
    proxy = ProxyHandler({'http': 'webgate.rcc.org:8080'})
    # construct a new opener using your proxy settings
    opener = build_opener(proxy)
    # install the openen on the module-level
    install_opener(opener)
    # make a request
    url = 'https://maker.ifttt.com/trigger/shooting/with/key/Ms0dKrkIhW22BVfL42T1D'
    data = urlencode({"value1" : "subject", "value2" : "body", "value3" : "congrats" }).encode()
    headers = {'content-type': 'application/json'}
    response = urlopen(Request(url, data, headers=headers))

    

def main(args=None):
    
    print("Welcome to Shootings IFTTT v0.1 \n")
    
    file = 'shootingstest - Copy (2).json'
    count = ""
    data = "" # raw data json file
    keep = [] # the list that will hold our dictionary
    edits = []# the list that'll hould our edits for the dictionary
    neighborhoods = []
    victims = 0
    fatality = ""
    numberOfShootings = 0
    emailHeader = ""
    emailBody = ""
    # grabs today's date and subtracts one day from it. then formats as "yyyy-mm-dd"
    yesterday = (datetime.datetime.today()-datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    shootings = {} # dictionary with neighborhood name and shooting objects

    #go get the raw data
    data = DataGrab(file)
    keep = yesterdayData(data, yesterday)
    keep = selectAttributes(keep)
    shootings = populate(keep)

    #neighborhoods = []
    #victims = 0
    #fatality = ""
    #numberOfShootings

    for neighborhood in shootings:
        neighborhoods.append(shootings[neighborhood].getNieghborhood())
        victims += shootings[neighborhood].getVictims()
        if fatality == "": 
            fatality = shootings[neighborhood].getFatality()
        if fatality != shootings[neighborhood].getFatality():
            fatality = "fatal and nonfatal"
        numberOfShootings += shootings[neighborhood].getCount()
    #    print(shootings[neighborhood].getNieghborhood())
    #    print(shootings[neighborhood].getVictims())
    #    print(shootings[neighborhood].getFatality())
    #    print(shootings[neighborhood].getLocation())
    #    print(shootings[neighborhood].getCount())

    emailHeader = formatEmail(neighborhoods, victims, fatality, numberOfShootings)[0]
    emailBody = formatEmail(neighborhoods, victims, fatality, numberOfShootings)[1]

    print("the email will look like ...\n"+emailHeader+"\n"+emailBody)

    post(emailHeader,emailBody)
    print("all good on this end")
    
if __name__ == "__main__":
    main()