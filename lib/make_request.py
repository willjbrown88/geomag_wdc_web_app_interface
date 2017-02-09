import requests as rq

kyFmt = 'format'
kyData = 'datasets'
kyAcpt = 'Accept'
kyContent = 'Content-Type'
kyAcptEncoding = 'Accept-Encoding'
csHostname = 'http://app.geomag.bgs.ac.uk'
url = csHostname + '/wdc/datasets/download'
cadence = 'minute'
csDtBasename = '/wdc/datasets/{}/'.format(cadence)
csAccepted = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0'
csContent = 'application/x-www-form-urlencoded'
csEncodings = 'gzip,deflate,sdch'
fmtIaga = 'text/x-iaga2002'
fmtWdc = 'text/x-wdc'
station = 'ESK'
year = 2015
month = 4
headers = {
    kyAcpt: csAccepted,
    kyAcptEncoding: csEncodings,
    kyContent:      csContent
 }
payload_data = {'format': '', 'datasets': ''}



dSets = csDtBasename + station.lower() + str(year) + str(month).zfill(2)
if isinstance(dSets, str):
    dSets = [dSets]
cslDSets = ','.join(dSet for dSet in list(dSets))

payload_data[kyData] = cslDSets

# iaga_rq_data = {
    # kyFmt:  fmtIaga,
    # kyData: cslDSets
# }
payload_data[kyFmt] = fmtIaga
reqiaga = rq.post(url, data=payload_data, headers=headers)
with open('./esk_test_iaga2k2_{}.zip'.format(cadence), 'wb') as file_:
    file_.write(reqiaga.content)

# wdc_rq_data = {
#     kyFmt:  'text/x-wdc',
#     kyData: cslDSets
# }

payload_data[kyFmt] = fmtWdc
reqwdc = rq.post(url, data=payload_data, headers=headers)
with open('./esk_test_wdc_{}.zip'.format(cadence), 'wb') as file_:
    file_.write(reqwdc.content)