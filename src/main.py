import requests, json
import datetime

class parser:

    def __init__(self):

        with open('./data/states_ii.json') as f:
            self.s_ii = json.load(f)

        with open('./data/districts_ii.json') as f:
            self.d_ii = json.load(f)

        with open('./data/district_state.json') as f:
            self.d_s = json.load(f)

    def centres(self, district, date):
        headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}
        URL = f"https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByDistrict?district_id={district}&date={date}"
        page = requests.get(URL, headers=headers)
        return page.json()
    
    def no_punct(self, phrase):
        punctuations = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
        no_punct = ""
        for char in phrase:
            if char not in punctuations:
                no_punct = no_punct + char
        return(no_punct)


    def ii_finder(self, phrase, iindex):
        keys = iindex.keys()
        if type(phrase) == list:
            words = phrase
        else:
            words = [word.lower() for word in phrase.lower().split(' ') if len(word) > 1]
        cands = []
        non = []
        for word in words:
            if word in keys:
                #print(word)
                cands.append(set(iindex[word]))
            else:
                non.append(word)
        if len(cands) == 0:
            return (None, non)
        elif len(cands) == 1:
            return (list(cands[0]), non)
        else:
            for c in cands[1:]:
                cands[0] = cands[0] & c
            return (list(cands[0]), non)

    def get_dis_code(self, phrase):
        phrase = self.no_punct(phrase).replace('west bengal', 'bengal')

        (states, non) = self.ii_finder(phrase, self.s_ii)
        (districts, _) = self.ii_finder(phrase, self.d_ii)

        if districts == None and states == None:
            print("here")
            return None
        elif len(districts) == 0:
            return None
        elif len(districts) == 1:
            return districts[0]
        else: # len(districts) > 1
            if len(states) == 1:
                return districts[0]
            else:
                for district in districts:
                    if s_d[str(district)]["state_id"] in states:
                        return district
        print("here now")
        return None
    
    def get_centres(self, district, dates):
        cx = []
        for date in dates:
            cx.append(self.centres(district, date))
        return cx
    
    def get_weeks(self):
        pass
    
    def dater(self, number = None, start = None):
        dates = []
        if start == None:
            dates.append(datetime.datetime.today() + datetime.timedelta(days = 1))
        for i in range(6):
            dates.append(dates[-1] + datetime.timedelta(days = 1))
        dates = [f"{d.day}-{d.month}-{d.year}" for d in dates]
        return dates

    def main(self, phrase):
        district = self.get_dis_code(phrase)
        dates = self.dater()
        if district == None:
            return("The place could not be found")
        cntrs = self.get_centres(district, dates)
        slots = [len(cntr["sessions"]) for cntr in cntrs if cntr != []]
        print(slots)
        if slots[0] != 0:
            h1 = cntrs[0]["sessions"][0]["name"]
            return(f"{sum(slots)} sessions found over the next week, with {slots[0]} slots tomorrow. Vaccines are available in {h1} and {sum(slots) - 1} more places.")
        elif sum(slots) > 0:
            return(f"{sum(slots)} sessions found over the next week, with {slots[0]} slots tomorrow.")
        else:
            return("No slots found over the next week")

