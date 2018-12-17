import os, imp
import matplotlib.pyplot as plt
from matplotlib.dates import (YEARLY, DateFormatter,
                              rrulewrapper, RRuleLocator, drange)
from datetime import datetime, date, time
import datetime as DT
def load_src(name, fpath):
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), fpath))
 
load_src("conf", "../conf.py")
import conf as Conf

class TempPlot:

    def plotNow(self,werte):
        s = []
        h = []
        for y in range(len(werte)):
            s.append(werte[y]['temp'])
            h.append(werte[y]['hum'])
        firstdate = datetime.strptime(werte[0]['datetime'],"%Y-%m-%d %H:%M:%S")
        lastdate = datetime.strptime(werte[len(werte)-1]['datetime'],"%Y-%m-%d %H:%M:%S")
        delta = DT.timedelta(minutes=10)
        #delta = DT.timedelta((lastdate - firstdate).days)
        #delta = lastdate - firstdate
        dates = drange(firstdate, lastdate, delta)
        
        
        print("werte: "+str(len(werte))+"erste: "+werte[0]['datetime']+" lrtzte "+werte[len(werte)-1]['datetime'])
        plt.ion()
        
        plt.clf()
        #plt.ylim(20,80)
        plt.title('Room temperture')
        plt.grid(True)
        plt.ylabel('Temp C')
        plt.xlabel('Stunden h')
        plt.plot(s, 'r-', label='Degrees C')
        plt.plot(h, 'b-', label='Hum %')
        plt.legend(loc='upper right')
        fig, ax = plt.subplots()
        plt.plot_date(dates, s)
        plt.plot_date(dates, h)
        #rule = rrulewrapper(YEARLY, byeaster=1, interval=5)
        #loc = RRuleLocator(rule)
        #loc = DateLocator(tz=None, minticks=5, maxticks=None, interval_multiples=True)
        #ax.xaxis.set_major_locator(loc)
        formatter = DateFormatter('%Y-%m-%d %H:%M')
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.set_tick_params(rotation=30, labelsize=10)
        fig.savefig(Conf.tempExport['file'])
        
        plt.show()
        

    def plot(self,tmpDB,days):
        werte = tmpDB.getValues(days)
        self.plotNow(werte)
        #update.message.reply_text(
        #    'Werte: Time:'+str(werte['datetime'])+' Temp:'+str(werte['temp'])+' Hum:'+str(werte['hum']),
        #    reply_markup=user_data['keyboard'])

def main():
    
    from tempDatabaseLib import TempDatabase
    tmpDB = TempDatabase()
    db = TempPlot()
    db.plot(tmpDB,Conf.tempExport['days'])
    

if __name__ == '__main__':
    main()