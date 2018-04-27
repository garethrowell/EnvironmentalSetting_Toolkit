import json
import urllib2

from StationDict import StationDict
from WxOb import WxOb
from ACIS import ACIS

class StationFinder(ACIS):
    '''
    INFO
    -------
    Object to find weather stations using ACIS Web Services.

    '''
    interval = None     #Not applicable when finding stations
    add = None          #Not applicable when finding stations
    duration = None     #Not applicable when finding stations
    reduceCodes = []    #Not applicable when finding stations

    def __init__(self, *args, **kwargs):
        super(StationFinder, self).__init__(*args, **kwargs)
        self.webServiceSource = 'StnMeta'

    def _formatElems(self):
        '''
        Unfortunately, the formatting of elements is different when requesting
        a list of stations. Thus, there is the need to override the standard ACIS
        method.
        '''
        self.elems = self.climateParameters

    def findStation(self, unitCode = None, distance = 0,
        climateParameters = None, sdate = None, edate = None
        ,filePathAndName = None, customBBox = None):
        '''
        INFO
        ----
        Standard method to find all stations and associated metadata
        based on zero or more criteria.


        ARGUMENTS
        ---------
        unitCode           4-Letter park code (searches for station within buffer)

        distance            buffer distance around the provided unitCode (if provided).
                            Default is 0 km.

        climateParameters    Parameter code for climate/weather element (e.g., mint, avgt, pcpn)

        sdate               (Optional) - Start date as yyyy-mm-dd or yyyymmdd.
                             If not provided, the default is the period of record.

        edate               (Optional) - End date as yyyy-mm-dd or yyyymmdd.
                             If not provided, the default is the period of record

        filePathAndName    If provided, a csv text file is saved to specific location.

        customBBox (optional) String containing bounding box geographic coordinates (longitude,latitude) using the WGS84 datum in the following format: Lower Left Longitude, Lower Left Latitude, Upper Right Longitude, Upper Right Latitude. Note: longitude is negative in the western hemisphere. Example: "-114.291153779, 35.5612153111, -111.252315168, 37.0351548001".

        RETURNS
        -------
        An object of station metadata (See StationDict.py)
        '''

        #ACIS handles start and end dates differently when searching for stations
        if not sdate:
            sdate = 'NA'
        if not edate:
            edate = 'NA'

        metadata = ('uid', 'name', 'state', 'll', 'elev', 'valid_daterange', 'sids')

        kwargs = self._formatArguments(unitCode = unitCode, distance = distance
            , climateParameters = climateParameters, reduceCodes = self.reduceCodes,
            sdate = sdate, edate = edate, meta = metadata, customBBox = customBBox )

        results =  self._call_ACIS(kwargs = kwargs)
        self._checkResponseForErrors(results)

        si = StationDict(observationClass = WxOb, queryParameters = self._input_dict, climateParameters = self.climateParameters)
        # Convert pandas.numpy array to list (plain text)
        hcnLookup = self._hcn_lookups.coopid.values.tolist()
        #if hcnLookup[5:10].strip() in station['sids']:
        for station in results['meta']:
            station['unitCode'] = unitCode #added to associate each station with a unit code
            #if station['sids'].split(" ") in self._hcn_lookups.coopid.values:
            # sids element is a list of unicode strings
            if (x[5:10].encode('latin1') for x in station['sids'] if x in y[5:10] for y in hcnLookup):
                station['isHCNStation'] = 'Y'
            else:
                station['isHCNStation'] = 'N'
            si._addStation(stationID = station['uid'], stationMeta = station)
        if filePathAndName:
                si.exportMeta(filePathAndName)
        return si

if __name__ == '__main__':
    sf = StationFinder()

    wxStations = sf.findStation(unitCode = 'NOCA',
        sdate = '1940-01-01', edate = '1940-01-01')
    print wxStations.queryParameters
    print wxStations
    print sf.supportedParameters
    print wxStations[26202].validDateRange
    print wxStations[26202].validDateRange.keys()

    wxStations = sf.findStation(unitCode = 'ROMO', climateParameters = 'mint, maxt,pcpn')
    print wxStations
    print wxStations[48106].validDateRange
    print wxStations[48106].validDateRange['pcpn']

    wxStations = sf.findStation(unitCode = 'ROMO', climateParameters = ['mint', 'maxt','pcpn'])
    print wxStations[48106].validDateRange

    stationList = sf.findStation(unitCode = 'AGFO', distance = 10, climateParameters = 'pcpn'
        ,sdate = '2015-08-01', edate = '2015-08-04')
    print stationList

    wxStations = sf.findStation(unitCode = 'NOCA',
         sdate = '2014-01-01', edate = '2016-01-01')
    print wxStations


