# -*- coding: utf-8 -*-
"""
Requests data from the BGS WDCWebApp (host: app.geomag.bgs.ac.uk, 
web portal:http://www.wdc.bgs.ac.uk/dataportal/).
Needs an iPython cluster running in a folder with access to our modules.
Connects to the cluster and instructs worker nodes to request all the data
needed from a given wdc observatory.
Parallelsed via map which only takes single argument. Main program exports 
various variables and modules for use by worker processes.
Request minutely data from WDC and stores zip files.
Logs processing steps on controller and worker nodes.
Created on Mon Jan 20 10:41:32 2014

@author: laurence

"""

"""
Makes a POST request to the WDC webapp for minutely data from an observatory
identified by the string argument.
Used with ipcluster map and can only take a single argument so kludgy export of
variables and modules done in calling program.
"""
def reqYearOfDataFromStn(stn):#, stnsDf):


    import numpy as np
    import os
    import requests as rq
    from time import sleep
#    import logging
    from zipfile import is_zipfile
    
    kyFmt = 'format'
    kyData = 'datasets'
    kyAcpt = 'Accept'
    kyContent = 'Content-Type'
    kyAcptEncoding = 'Accept-Encoding'
    csHostname = 'http://app.geomag.bgs.ac.uk'
    csURL = csHostname + '/wdc/datasets/download'
    csDtBasename = '/wdc/datasets/minute/'
    csAccepted = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0'
    csContent = 'application/x-www-form-urlencoded'
    csEncodings = 'gzip,deflate,sdch'   
    dataFmt = 'text/x-iaga2002'
    
    
    start = int(np.floor(byStnDf.ix[stn]['earlyYear']))
    end = int(np.ceil(byStnDf.ix[stn]['lateYear']))
    dataYears = np.arange(start, end+1)#
# TODO @@ DEBUG
#    dataYears = [int(a) for a in byStnDf.ix[stn].dropna().values.tolist()]

    dataMonths = np.arange(1,13)
    dSets = [0]*len(dataMonths)
    
    logging.info('about to form POST requests for {0} from {1}-{2}'
                .format(stn, start, end))
#    logging.info('about to form POST requests for {0} #padding',stn)
    for yr in dataYears:
            i = 0
            for mt in dataMonths:
                dSets[i] = csDtBasename + stn.lower() + str(yr) + str(mt).zfill(2)
                i += 1   
     
            cslDSets = ','.join(dSet for dSet in dSets)
            # form the dicts for making the resuest   
            payload = {kyFmt:  dataFmt, 
                       kyData: cslDSets}    
            headers = {kyAcpt:         csAccepted,
                       kyAcptEncoding: csEncodings,
                       kyContent:      csContent}

            zFile=os.path.join(wdcDlPath,stn.lower()+str(yr)+wdcDlExtn)
            
            if (is_zipfile(zFile)):
                 logging.info('zipfile: %s exists, skipping download', zFile)
                 continue
            
            # make the request
            try:
                logging.info('making POST request for datasets: %s',cslDSets)
                r = rq.post(csURL,data=payload,headers=headers)
                #            except rq.ConnectionError as err:
                #                logging.error(err.message)
                #                logging.warning('could not write zip file (%s) returned by WDCservice datasets: %s',
                #                                    zFile,cslDSets)
                
                if (not r.status_code == rq.codes.ok):                   
                    logging.warning('POST request returned failure for reason: %s',r.reason)
                    continue
                    
                try:
                    output = open(zFile, 'wb')
                    output.write(r.content)
                except rq.ConnectionError as err:
                    logging.error(err.message)
                    logging.warning('could not write zip file (%s) returned by WDCservice datasets: %s',
                                    zFile,cslDSets)
                except:
                    logging.warning('could not write zip file (%s) returned by WDCservice datasets: %s',
                                    zFile,cslDSets)
                finally:
                   output.close()
                
            except:
                logging.warning('data POST request failed for datasets: %s',cslDSets)
                    #n.b this string formatting used so it is only evaluated on exception
                    #    ' {0}'.format and (' %' %) would be eval every pass   
            sleep(5)  # wait 5 seconds  as the webapp server 
                      # is easily overloaded as of 2014-07-16


                

if __name__ == "__main__":

    import pandas as pd
    import logging
    from IPython.parallel import Client   
    from projectFilenameVariables import wdcDlPath, wdcDlExtn, stnsYearsWdcBasename, logPath

   
    logFmt = r"%(asctime)s %(levelname)s  %(funcName)s %(message)s"
    logging.basicConfig(filename=logPath, format=logFmt, level=logging.DEBUG)
    logging.info('requesting data from WDC webservice, expect .zip files')  
     
    byStnDf = pd.read_csv(stnsYearsWdcBasename,delim_whitespace=True, index_col=0)
    byStnDf.index.name = 'station'
     
     # TODO @@ DEBUG
#    f = ('W:/Teams\\Geomag\\IIFR\\Data\\External_Error_Analysis\\'
#           'Misc_Analysis\\SPE\\data\\pythonWdcWebserviceQuery\\'
#           'wdcAllPadDataNeeded.txt')
#  
# 
#    tmp_df =pd.read_csv(f,
#                                 delim_whitespace=True, 
#                                 header=None,
#                                 names=[ 'stn','year'])
#    
#    stns_set = set(tmp_df.stn.values)
#    years_arr =   [tmp_df[tmp_df.stn==s].year.values for s in stns_set]
#    byStnDf = pd.DataFrame(index=stns_set,
#                           data=years_arr)
                 
    stns = byStnDf.index.tolist()
    stns = ['DED']
#   we need an array even for testing a single observatory: syntax like this:    
#    stns = ['LYC']
    
    ## make sure there is an ipcluster started in the same directory as this file
    try:

        rcReq = Client(profile='default')
        dvReq = rcReq[:]
        
        with dvReq.sync_imports():
             from readWdcDotMinFiles import getpid, checkhostname, getLogFile
             import logging
             


    
        export_dict = {k: globals()[k] for k in 
                    ('reqYearOfDataFromStn','wdcDlPath', 'wdcDlExtn','byStnDf','logFmt')}
                     

        dvReq.push(export_dict, block=True)
        
        exWorkersLogFile = 'logFile = getLogFile(wdcDlPath)'   
        exWorkersLogConf = ('logging.basicConfig(filename=logFile, format=logFmt, level=logging.DEBUG)') 
        resLFile =  dvReq.execute(exWorkersLogFile)
        resLConf = dvReq.execute(exWorkersLogConf)
        
        
        logging.info('requesting WDC webservice data  on {0} engines', len(dvReq)) 
        
        resReq = dvReq.map(reqYearOfDataFromStn, stns)
        res = dvReq.execute('logging.info("finished all POST requests")')
         
        dvReq.wait(resReq) # wait until we've done everything on all processes
        res = dvReq.execute('logging.shutdown()')
            

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
        logging.shutdown()
        
 
