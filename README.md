# OsbServiceMonitor
Oracle Service Bus moniroing services statistics and disable service using python.

This is sdemo python scripts for disable service if Max response time goes above 1000MiliSec.
There are three script,
1) osb-list-all-service for OSB 11g.
2) osb-list-all-service-12.2 for OSB 12.2
3) osb-auto-disable-service-table, using TableIT python lib for printing output in table formate. To run this script make sure TableIT https://github.com/SuperMaZingCoder/TableIt install on machine

Script collect data as below and compare 'e.getMax()' if greater than 1000 then disable the service.
```
					print " -- " + e.getName() + "("+ str(e.getType()) +"): " 
					print " -- Min Response Time : " +  str(e.getMin()) 
					print " -- Max Response Time : " +  str(e.getMax()) 
					print " -- Avg Response Time : " +  str(e.getAverage()) 
					print " -- Sum Response Time : " +  str(e.getSum())
					
					if e.getMax() > 1000:
```
          
Also, it is important to reset the stats once disable the service, else e.getMax() will comapre old stats and try to disable service again.
```
          cmo.resetStatistics(refArray)
```
