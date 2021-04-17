################################ DESCRIPTION ##################################
#For FMW 11g classpath 
#C:\AppServers\FMW_HOME11G\Oracle_OSB1\modules\com.bea.common.configfwk_1.9.0.0.jar
#C:\AppServers\FMW_HOME11G\Oracle_OSB1\modules\com.bea.alsb.statistics_1.4.0.0.jar
#C:\AppServers\FMW_HOME11G\Oracle_OSB1\lib\sb-kernel-wls.jar
#C:\AppServers\FMW_HOME11G\Oracle_OSB1\lib\sb-kernel-api.jar
#
#  
###############################################################################

# Import Section
import socket
import os
import time
import TableIt

from com.bea.wli.sb.management.configuration import ALSBConfigurationMBean
from com.bea.wli.sb.management.configuration import DelegatedALSBConfigurationMBean
from com.bea.wli.config import Ref
from java.lang import String
from com.bea.wli.config import Ref
from com.bea.wli.sb.util import Refs
from com.bea.wli.sb.management.configuration import CommonServiceConfigurationMBean
from com.bea.wli.sb.management.configuration import SessionManagementMBean
from com.bea.wli.sb.management.configuration import ProxyServiceConfigurationMBean
from com.bea.wli.monitoring import StatisticType
from com.bea.wli.monitoring import ServiceDomainMBean
from com.bea.wli.monitoring import ServiceResourceStatistic
from com.bea.wli.monitoring import StatisticValue
from com.bea.wli.monitoring import ResourceType

from weblogic.management.mbeanservers.edit import NotEditorException

# Set some constants
DESCRIPTION = 'List ALL Services and stats deployed in OSB Domain.'
AUTHOR = 'Tanmoy Roy (Troy)'

WL_USERNAME = 'weblogic'
WL_PASSWORD = 'Welcome1'

RUN_USERNAME = os.getlogin()
LOCALHOST = socket.gethostname()
DOMAIN_NAME = os.getenv('WL_DOMAIN')
DOMAIN_PORT = '7001'
DOMAIN_DIR = os.getenv('WL_DOMAIN_DIR')
MWHOME = os.getenv('MW_HOME')
URL_CONNECT ='t3://' + LOCALHOST + ':' + DOMAIN_PORT

ACTUAL_TIME = time.strftime("%H:%M:%S")
ACTUAL_DATE = time.strftime("%d/%m/%Y")
 
# Information Screen
print '#########################################################################'
print '#'
print '#  DATE:           ' + ACTUAL_DATE
print '#  TIME:           ' + ACTUAL_TIME
#print '#  MW HOME:        ' + MWHOME
print '#  DESCRIPTION:    ' + DESCRIPTION
print '#  URL CONNECTION: ' + URL_CONNECT
print '#  AUTHOR:         ' + AUTHOR
print '#'
print '#########################################################################'
print
print

# Connect with WL Server..
print 'Try connection ..'
print
connect(WL_USERNAME, WL_PASSWORD, URL_CONNECT)

### Get the Configuration Manager
cfgManager = getConfigManager()
try:
   cfgManager.getChanges()
   print '===> Currently there is a Session'
   if cfgManager.isEditor() == true:
       ### You are making changes!!!
       print '===> Looks like you started that session'
       print '===> You can check the console for any pending changes'
       print '===> Try rerunning this script after you release or commit the pending changes'
   #exit()

except NotEditorException, e:
   if cfgManager.getCurrentEditor() is None:
   ### No session
       print 'No active session  .. OK'
       pass
   else:
       ### Someone else is making changes
       userWithSession = cfgManager.getCurrentEditor().replace(' ', '')
       print '===> Currently there is a Session'
       print '===> User \"' +userWithSession+'\" is making the changes'
       print '===> Wait until \"' +userWithSession+'\" complete the current session'
       #exit()
   pass
except Exception:
   ### Other Errors
   print '===> Error, see log for more info'
   exit()


print
print
# Main
domainRuntime()

servers = domainRuntimeService.getServerRuntimes();
print('################################################################')
print('# Java heap information per server')
print('################################################################')
print('%20s %10s %8s %8s %4s' % ('Server','Current','Free','Max','Free'))
for server in servers:
   free    = int(server.getJVMRuntime().getHeapFreeCurrent())/(1024*1024)
   freePct = int(server.getJVMRuntime().getHeapFreePercent())
   current = int(server.getJVMRuntime().getHeapSizeCurrent())/(1024*1024)
   max     = int(server.getJVMRuntime().getHeapSizeMax())/(1024*1024)
   print('%20s %7d MB %5d MB %5d MB %3d%%' % (server.getName(),current,free,max,freePct))
 
print
print
print 'Look for ALSB Object ..'
alsbCore = findService(ALSBConfigurationMBean.NAME, ALSBConfigurationMBean.TYPE)
print '.. OK'
print 'Find info about OSB Service Deployed ..'

allRefs = alsbCore.getRefs(Ref.DOMAIN)
#it = refs.iterator()
print "======================= Projects ======================="
for ref in allRefs: 
	# Get Types
	typeID = ref.getTypeId()
	# and listing them by type
	if typeID == Ref.PROJECT_REF:
		print 'Project : '  + ref.getProjectName()

		
print "======================= Proxy Service ======================="

for ref in allRefs:
        # Get Types
        typeID = ref.getTypeId()
	if typeID == "ProxyService":
		
		project = ""
		service = ref.getLocalName()
		
		serviceResourcePath = ref.getNames()
		length = len(serviceResourcePath)
				
		for i in range(length-1):
			project = project + serviceResourcePath[i] + "/"
				
		print 'Proxy Service : ' + project + service
		cd('domainRuntime:/DomainServices/ServiceDomain')  
		#ls()
		##print cmo.getProxyServiceStatistics([ref],ResourceType.SERVICE.value(),'')        
		props = cmo.getProxyServiceStatistics([ref],ResourceType.SERVICE.value(),'')        
		#props = cmo.getStatistics([ref],ResourceType.SERVICE.value(),'')        
		#print props        
		for rs in props[ref].getAllResourceStatistics():            
			for e in rs.getStatistics():
				#if e.getType() == StatisticType.COUNT:                        
				#	print e.getName() + "("+ str(e.getType()) +"): " + str(e.getCount())
				if e.getType() == StatisticType.INTERVAL and e.getName() == "response-time":
					print " |"
					print " -- " + e.getName() + "("+ str(e.getType()) +"): " 
					print " -- Min Response Time : " +  str(e.getMin()) 
					print " -- Max Response Time : " +  str(e.getMax()) 
					print " -- Avg Response Time : " +  str(e.getAverage()) 
					print " -- Sum Response Time : " +  str(e.getSum())
					
					#If max time is above 1000 then disable the service and reset the stats so that next loop will get the fresh data.
					if e.getMax() > 1000:
						sessionName = String("Troy-OSB-Disable-PS" + service + "-" +Long(System.currentTimeMillis()).toString())
						sessionMBean = findService(SessionManagementMBean.NAME,SessionManagementMBean.TYPE)
						sessionMBean.createSession(sessionName)
						mbean = findService(String("ProxyServiceConfiguration.").concat(sessionName),'com.bea.wli.sb.management.configuration.ProxyServiceConfigurationMBean')
						projectName = Refs.makeParentRef(project)
						proxyRef = Refs.makeProxyRef(projectName, service)
						print "Disabling... " + service
						if mbean.isEnabled(proxyRef) == 1:
							mbean.disableService(proxyRef)
							refArray = []
							refArray.append(Ref(typeID,projectName,service))
							cmo.resetStatistics(refArray)
							print " === Resetting statistics for this service."
						else:
							print "Service already disabled."
						sessionMBean.activateSession(sessionName, "Auto Disabled BS ")
		print ""

print "===================== Business Service ====================="

for ref in allRefs:
        # Get Types
	typeID = ref.getTypeId()
	if typeID == "BusinessService":
		
		project = ""
		service = ref.getLocalName()
		
		serviceResourcePath = ref.getNames()
		length = len(serviceResourcePath)
		
		for i in range(length-1):
			project = project + serviceResourcePath[i] + "/"
				
		print 'Business Service : ' + project + service
		cd('domainRuntime:/DomainServices/ServiceDomain')  
		##print cmo.getProxyServiceStatistics([ref],ResourceType.SERVICE.value(),'')        
		props = cmo.getBusinessServiceStatistics([ref],ResourceType.SERVICE.value(),'')        
		#props = cmo.getStatistics([ref],ResourceType.SERVICE.value(),'')        
		#print props        
		for rs in props[ref].getAllResourceStatistics():            
			for e in rs.getStatistics():
				if e.getType() == StatisticType.INTERVAL and e.getName() == "response-time":
					print " |"
					print " -- " + e.getName() + "("+ str(e.getType()) +"): " 
					print " -- Min Response Time : " +  str(e.getMin()) 
					print " -- Max Response Time : " +  str(e.getMax()) 
					print " -- Avg Response Time : " +  str(e.getAverage()) 
					print " -- Sum Response Time : " +  str(e.getSum())
					
					#If max time is above 1000 then disable the service and reset the stats so that next loop will get the fresh data.
					if e.getMax() > 1000:
						sessionName = String("Troy-OSB-Disable-BS-" + Long(System.currentTimeMillis()).toString())
						sessionMBean = findService(SessionManagementMBean.NAME,SessionManagementMBean.TYPE)
						sessionMBean.createSession(sessionName)
						mbean = findService(String("BusinessServiceConfiguration.").concat(sessionName),'com.bea.wli.sb.management.configuration.BusinessServiceConfigurationMBean')
						projectName = Refs.makeParentRef(project)
						proxyRef = Refs.makeBusinessSvcRef(projectName,service)
						print " === Disabling... " + service 
						if mbean.isEnabled(proxyRef) == 1:
							mbean.disableService(proxyRef)
							refArray = []
							refArray.append(Ref(typeID,projectName,service))
							cmo.resetStatistics(refArray)
							print " === Resetting statistics for this service."
						else:
							print "Service already disabled."
						sessionMBean.activateSession(sessionName, "Auto Disabled BS ")
			print " "
print
print
# Disconnect from Server..
print 'Disconnecting from Server ..'
disconnect()
# The End
print
print 'Exiting from the script now ..'
exit()