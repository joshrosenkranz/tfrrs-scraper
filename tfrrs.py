from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import matplotlib.pyplot as plt
import numpy as np

def splitByDelim(s, delim):
    #Takes in a string and a delimiting character and returns a list
    #  of strings that were separated by delim in the original string
    #Empty strings are not included (if the delimiter appears multiple times
    #  consecutively)
    return [x for x in s.split(delim) if x]

def convertTimeToMins(time):
    #Converts a time of the form MM:SS to the number of minutes and
    #  fractional minutes
    mins, secs = time.split(":")
    return int(mins) + float(secs)/60

def getTags(link):
    #Returns a BeautifulSoup result set with an entry for each runner
    #  on the results page
    req = Request(link, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    soup = BeautifulSoup(webpage, "html.parser")
    tags = soup.find_all('tr')
    return tags

def parseLink(link):
    tags = getTags(link)
    atRunners = False
    atMen = True
    runners = {}
    for i in range(len(tags)):
        tag = tags[i].text
        if not atRunners:
            #Wait for the "NAME" header to appear to avoid parsing
            #  team results
            if "name" in tag.lower().split() and atMen:
                atRunners = True
                atMen = False
        else:
            #Stop when the team results appear again
            if "team" in tag.lower().split() and "name" not in tag.lower().split():
                atRunners = False
            else:
                #Store the different fields for the runner in a dictionary
                values = splitByDelim(tag, '\n')
                name = values[1]
                runnerDict = {}
                runnerDict["Place"] = values[0]
                runnerDict["Year"] = values[2]
                runnerDict["Team"] = values[3]
                runnerDict["Time"] = convertTimeToMins(values[5])
                runnerDict["Score"] = values[6]
                runners[name] = runnerDict
    return runners

def runComparison(meet1, meet2, stat, meet_dict):
    #Finds runners that competed in both meet1 and meet2 and plot
    #  their result for the given statistic where meet1 is on the
    #  x-axis and meet2 is on the y-axis
    runners1 = parseLink(meet_dict[meet1])
    runners2 = parseLink(meet_dict[meet2])

    xs = []
    ys = []
    for runner in runners1:
        if runner in runners2:
            xs.append(float(runners1[runner][stat]))
            ys.append(float(runners2[runner][stat]))

    plt.plot(xs, ys, '.')

    slope, intercept = np.polyfit(xs, ys, 1)
    equation = stat + " at " + meet2 + " = " + stat + " at " + meet1 + " * " + str(round(slope, 2)) + " + " + str(round(intercept, 2))
    xl = [min(xs), max(xs)]
    yl = [slope*xx + intercept  for xx in xl]
    plt.plot(xl, yl)
    plt.xlabel(stat + " at " + meet1)
    plt.ylabel(stat + " at " + meet2)
    plt.title(equation)
    plt.show()

meet_dict = {}
meet_dict["Purple Valley"] = "https://www.tfrrs.org/results/xc/Purple_Valley_XC_Invite/12846.html"
meet_dict["NEICAAA Championships"] = "https://www.tfrrs.org/results/xc/NEICAAA_Cross_Country_Championship/12251.html"
meet_dict["Pre-Nationals"] = "https://www.tfrrs.org/results/xc/Principia_College_Cowbell_XC_Invite/13224.html"
meet_dict["NEWMAC Championships"] = "https://www.tfrrs.org/results/xc/2017_NEWMAC_Cross_Country_Championship/12340.html"
meet_dict["New England Regionals"] = "https://www.tfrrs.org/results/xc/NCAA_Division_III_New_England_Region_Cross_Country_Championships/13033.html"
meet_dict["Nationals"] = "https://www.tfrrs.org/results/xc/NCAA_Division_III_Cross_Country_Championships/13424.html"

runComparison("Pre-Nationals", "Nationals", "Place", meet_dict)

