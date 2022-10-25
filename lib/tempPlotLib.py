import os, imp
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import (YEARLY, DateFormatter,
                              rrulewrapper, RRuleLocator, drange)
import matplotlib.ticker as ticker
from matplotlib.lines import Line2D
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
        dwds = []
        dwdh = []
        dates = []
        for y in range(len(werte)):
            s.append(werte[y]['temp'])
            h.append(werte[y]['hum'])
            dwds.append(werte[y]['dwdtemp'])
            dwdh.append(werte[y]['dwdhum'])
            dates.append(datetime.strptime(werte[y]['datetime'],"%Y-%m-%d %H:%M:%S"))
        firstdate = datetime.strptime(werte[0]['datetime'],"%Y-%m-%d %H:%M:%S")
        lastdate = datetime.strptime(werte[len(werte)-1]['datetime'],"%Y-%m-%d %H:%M:%S")
        #delta = DT.timedelta(minutes=10)
        #dates = drange(firstdate, firstdate+(delta*(1+int((lastdate-firstdate)/delta))), delta)
        
        
        #print("y-werte: "+str(len(werte))+" x-werte: "+str((lastdate-firstdate)/delta)+" erster: "+werte[0]['datetime']+" lrtzte "+werte[len(werte)-1]['datetime'])
        plt.ion()
        
        plt.clf()
        #plt.ylim(20,80)
        plt.title('Room temperture')
        plt.ylabel('Temp C')
        plt.xlabel('Stunden h')
        plt.plot(s, linestyle='-', label='Degrees C', linewidth=3)
        plt.plot(h, linestyle='--', label='Hum %')
        plt.plot(dwds, linestyle=':', label='DWD Degrees C')
        plt.plot(dwdh, linestyle='-', label='DWD Hum %')
        plt.legend(loc='upper center',fancybox=True, shadow=True)
        fig, ax = plt.subplots()
        plt.plot_date(dates, s)
        plt.plot_date(dates, h)
        plt.plot_date(dates, dwds)
        plt.plot_date(dates, dwdh)
        #rule = rrulewrapper(YEARLY, byeaster=1, interval=5)
        #loc = RRuleLocator(rule)
        #loc = DateLocator(tz=None, minticks=5, maxticks=None, interval_multiples=True)
        #ax.xaxis.set_major_locator(loc)
        formatter = DateFormatter('%Y-%m-%d %H:%M')
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.set_tick_params(rotation=30, labelsize=10)
        
        start, end = ax.get_ylim()
        centerNull = int(start)%5
        ax.yaxis.set_ticks(np.arange(start-centerNull, end, 5))
        ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%d'))
        
        ax.grid(True)
        fig.autofmt_xdate()
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
    try:
        #db.plot(tmpDB,Conf.tempExport['days'])
        db.plot(tmpDB,14)
    except Exception as e:
        print('Error: '+str(e))
    

if __name__ == '__main__':
    main()
