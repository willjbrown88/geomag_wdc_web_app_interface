# -*- coding: utf-8 -*-
"""
contains project level variables for the iifr error vs distance work
e.g. paths to the data directory, filenames etc. 
Created on Thu Dec 12 08:11:23 2013

@author: laurence
"""
import os.path 
from os import sep as ossep
#==============================================================================
# Set file names etc. here 
#==============================================================================
#dataDrive = os.path.join(r'\\mhsan', r'Workspace')
dataDrive = 'W:/'
dataSubDir = os.path.join('Teams','Geomag','IIFR','Data',
                            'External_Error_Analysis','Misc_Analysis','SPE',
                            'data', 'pythonWdcWebserviceQuery')                             

# excel file of Image network data 
imageExcelBasename ='imageDataAvailability'                            

# intermediate files used in meta data munging/data pairwise data availability                            
pairDictBasename ='stationPairsDict'
imageDictBasename ='imageStationsDict'
subsetDictBasename = 'pairs58-75QdLatDistLess1000km'
stationsYearsBasename = 'stationsNumYearsStartEnd'
stnsYearsWdcBasename = stationsYearsBasename+'-WdcOnly'
stnsYearsImageBasename = stationsYearsBasename+'-ImageOnly'

# extensions
textFileExtension = '.txt'
binaryFileExtension = '.npy' 
excelFileExtension = '.xlsx'
dataFrameStoreExtension = '.hd5'

logfileName = 'processing.log'

# quasi dipole working files
qDipoleDrive = 'I:/'
qDipoleSubDir = os.path.join('data','WorkZone','Laurence','iifrExtrapDistance')
qDInputBasename = 'codeLatLonGmlat'
qDOutputBasename = 'qDLatsXtrerrExtrap'
qDInExtension = '.in'
qDOutExtension = '.out'


# location for the zip files and uncompressed WDC data 
wdcDrive = 'C:/'
wdcSubDir = 'WdcXterr'
wdcDlDir = 'zipfiles'
wdcDlExtn = '.zip'

logExtn = '.log'

# parameters for the download of IMAGE tarfiles
imageSubDir = 'image_files'
imageDlDir = 'tarfiles'
imageGzDir = 'gzfiles'
imageReqLog = 'image_requests' + logExtn
imageParseLog = 'image_parse' + logExtn
imageDlExtn = '.tar'

# Quiet day time series files
iqdBasename = 'quietDays'
iqDaysListFile = 'internationalQuietDaysGeoSciAus1976-2014'
iqdTimeSeries = 'quietDays'
iqParseLog = 'quiet_day_ts' + logExtn

# detrending
detrendLogFile = 'detrending' + logExtn

# per station pair differnces
diffDrive = 'E:/'
diffSubDir = 'differences'
#==============================================================================
# Do work to make valid paths from values supplied above
#==============================================================================

outdir =  os.path.join(dataDrive, ossep, dataSubDir)
pairDictFilePath = os.path.join(outdir, pairDictBasename + binaryFileExtension)
imageDictFilePath = os.path.join(outdir, imageDictBasename + binaryFileExtension)
imageExcelPath = os.path.join(outdir, imageExcelBasename + excelFileExtension)
subsetCsvFilePath = os.path.join(outdir, subsetDictBasename + textFileExtension)
subsetBinFilePath = os.path.join(outdir, subsetDictBasename + binaryFileExtension)
stationsYearsPath = os.path.join(outdir, stationsYearsBasename + textFileExtension)
stnsYearsWdcBasename = os.path.join(outdir, stnsYearsWdcBasename + textFileExtension)
stnsYearsImageBasename = os.path.join(outdir, stnsYearsImageBasename + textFileExtension)


qDDir =  os.path.join(qDipoleDrive,ossep,qDipoleSubDir)
qDInputPath = os.path.join(qDDir, qDInputBasename + qDInExtension)
qDOutputPath = os.path.join(qDDir, qDOutputBasename + qDOutExtension)

wdcPath = os.path.join(wdcDrive, wdcSubDir)
wdcDlPath = os.path.join(wdcDrive, wdcSubDir, wdcDlDir)

logPath = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 
                       'Temp', logfileName)

imagePath =  os.path.join(wdcPath, imageSubDir)
imageDlPath =  os.path.join(imagePath, imageDlDir)
imageGzPath =  os.path.join(imagePath, imageGzDir)
imageReqLogPath = os.path.join(imagePath, imageReqLog)
imageParseLogPath = os.path.join(imagePath, imageParseLog)

iqDaysListPath = os.path.join(outdir,iqDaysListFile + textFileExtension)
iqDaysTsPath = os.path.join(wdcDrive,wdcSubDir,iqdTimeSeries)
iqLogPath = os.path.join(iqDaysTsPath, iqParseLog)

diffPath = os.path.join(diffDrive, wdcSubDir, diffSubDir)

detrendLogDir = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 
                       'Temp')
detrendLogPath = os.path.join(detrendLogDir, detrendLogFile)