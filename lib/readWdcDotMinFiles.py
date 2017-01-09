# -*- coding: utf-8 -*-
"""
connect to an ipython cluster and farm out the .min file to hfd processing
to the compute nodes
Created on Fri Feb 28 13:36:58 2014

@author: laurence
"""
def getpid():
    import os
    return os.getpid()

def checkhostname():
    import socket
    return socket.gethostname()
    
def getLogFile(folder):
    import os.path
    return os.path.join(folder,str(getpid())+checkhostname()+'.log')    


if __name__ == "__main__":

    from projectFilenameVariables import wdcPath,logPath
    import logging
    import os
    import re
    from IPython.parallel import Client 
    
    logFmt = r"%(asctime)s %(levelname)s  %(funcName)s %(message)s"
    logging.basicConfig(filename=logPath, format=logFmt, level=logging.DEBUG) 
    logging.info('reading IAGA month files parsing to annual HDF')  
   
    
    # regexp filters for iaga codes, year folders and minute files
    reIagaCode = re.compile(r'^[A-z]{3}$') 

    # find each station to process by reading the directory
    stns = os.listdir(wdcPath)
    # filter out any directories not conforming to iaga 3 letter codes
    stns = filter(lambda i: reIagaCode.search(i), stns)

# DEBUG short list of stations    
#    stns = ['bjn','gdh','hrn','lyc', 'sdo', 'tro']
    
    try:
        rc = Client(profile='default')
        dv = rc.direct_view()
        lv = rc.load_balanced_view()
        
        with dv.sync_imports():
            from dotMinFilesToHdfStores import makeAnnualHdf
            import logging
    
        export_dict = {k: globals()[k] for k in 
                    ('getpid', 'checkhostname', 'getLogFile', 'wdcPath', 'logFmt')}
        dv.push(export_dict, block=True)
    
        res = dv.execute('logFile = getLogFile(wdcPath)')
        res = dv.execute('logging.basicConfig(filename=logFile, format = logFmt, level=logging.DEBUG)')
        
        
        
        logging.info('parsing on {0} enginess'.format(len(lv)))         
        resParse = lv.map(makeAnnualHdf, stns)
        
        lv.wait(resParse) # wait until we've done everything on all processes
        res = dv.execute('logging.info("finished parsing IAGA2002 files")')
        res = dv.execute('logging.shutdown()')


    except:
        strOut=("######### ERROR ###########\n"      +
                "could not connect to ipcluster\n"   +
                "check cluster is running\n"         +
                "in folder with access to modules\n" +
                "to start at command prompt: \n"     +
                "     > ipcluster start --n=4 --profile=default")
        print(strOut)
        logging.error(strOut)     
        
    finally:
        logging.info('IAGA2002 parser controller program finished')
        logging.shutdown()
    #    x = logging._handlVers.copy()
    #    for i in x:
    #        logging.getLogger().removeHandler(i)
    #        i.flush()
    #        i.close()