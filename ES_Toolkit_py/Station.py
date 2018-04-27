from StationDateRange import StationDateRange
from StationData import StationData
from common import missingValue
from ACIS import ACIS


class Station(object):
    '''
    Class for all daily wx station objects.
    Object containing all station metadata (e.g., uid, elev, sids, etc) and weather data by parameter
    '''
    def __init__(self, observationClass):
        self.observationClass = observationClass
        self._metaTags = ('uid', 'name','longitude', 'latitude',  'sid1', 'sid1_type', #tags defining order of metadata elements to show when presenting stationMetadata
            'sid2', 'sid2_type', 'sid3', 'sid3_type', 'state',
            'elev', 'minDate', 'maxDate', 'isHCNStation', 'unitCode')
        self._dataTags = ('uid', 'name', 'longitude', 'latitude', 'sid1', 'sid1_type',
            'sid2', 'sid2_type', 'sid3', 'sid3_type', 'state',
            'elev') #station metadata to include with data export
        self.missingValue = missingValue

    def _set(self, stationMeta, climateParameters, stationData = None ):
        '''
        Method to set up a new station with station metadata and station data
        for one or more climate parameters
        '''
        self.climateParameters = climateParameters
        self._setStationMetadata(stationMeta)
        if stationData:
            self._addStationWxData(stationData)

    def _setStationMetadata(self, stationInfo):
        '''
        Sets the station metadata. Values that are not present are set to missing value
        '''

        default = self.missingValue
        self.name = stationInfo.get('name', default).encode()
        try:
            self.sid1 = str(stationInfo['sids'][0]).encode()
        except:
            self.sid1 = default
        try:
            self.sid2 = str(stationInfo['sids'][1]).encode()
        except:
            self.sid2 = default
        try:
            self.sid3 = str(stationInfo['sids'][2]).encode()
        except:
            self.sid3 = default
        self.sid1_type = self._setStationType(self.sid1)
        self.sid2_type = self._setStationType(self.sid2)
        self.sid3_type = self._setStationType(self.sid3)
        self.latitude = stationInfo.get('ll', default)[1]
        self.longitude = stationInfo.get('ll', default)[0]
        self.state = stationInfo.get('state', default).encode()
        self.elev = stationInfo.get('elev', default)
        self.uid = int(stationInfo.get('uid'))
        self.sids = str(stationInfo.get('sids', default)).encode()
        self.isHCNStation = stationInfo.get('isHCNStation', default)
        self.unitCode = stationInfo.get('unitCode', default)
        self.validDateRange = StationDateRange(stationInfo.get('valid_daterange', self.missingValue), self.climateParameters)
        self.maxDate = self.validDateRange.maxRange
        self.minDate = self.validDateRange.minRange

    def _setStationType(self, sid):
        '''
        Identifies the type of station based on the station ID since ACIS
        does't do this explicitly.  If the station ID identifies it as being from
         GHCN, then sub-type is used.
        '''
        acis = ACIS()
        if sid <> self.missingValue:
            stationType = acis.stationSources[str(sid.split()[1])]['description'].encode()
            if stationType == 'GHCN':
                try:
                    stationType = acis.stationSources['6']['subtypes'][sid[0:3]].encode()
                except:
                    pass # Keep it GHCN
            return stationType
        else:
            return self.missingValue

    def _dumpMetaToList(self):
        '''
        Iterates through all metadata tags to create a list of of tag values
        '''
        return [self.__dict__[t] for t in self._metaTags]

    def __str__(self):
        '''
        Pretty representation of Station object
        '''
        return str(self._dumpMetaToList())


    def _addStationWxData(self, stationData):
        '''
        Method to add weather data to Station object
        '''
        if stationData <> 'error':
            self.data = StationData(observationClass = self.observationClass)
            self.data._set(stationData, self.climateParameters)

    @property
    def hasWxData(self):
        '''
        Boolean indicating whether Station object has associated weather observations
        True - Yes
        False - No
        '''
        try:
            self.data
            return True
        except:
            return False

    def _dumpDataToList(self, includeHeader = True):
        '''
        Dumps all station data to a list by iterating through all climate parameters
        '''
        if includeHeader:
            self._dataAsList = [self._header]
        else:
            self._dataAsList = []

        if self.hasWxData:
            for date in self.data.observationDates:
                a = [self.uid, self.name, self.longitude, self.latitude,
                     self.sid1, self.sid1_type, self.sid2,
                     self.sid2_type, self.sid3, self.sid3_type,
                     self.state,  self.elev, date]
                for param in self.climateParameters:
                    a.extend(self.data[param][date].toList(includeDate = False))
                self._dataAsList.append(a)
        return self._dataAsList

    @property
    def _header(self):
        '''
        returns a header as a list by calling the parameter series object to create
        a header
        '''
        oClass = self.observationClass()
        header = list(self._dataTags[:]) #set header to copy of _dataTags values
        header.extend(['date'])
        for p in self.climateParameters:
            header.extend(self.data[p]._createHeader())
        return header


if __name__=='__main__':

    from WxOb import DailyWxOb
    meta= {'name': 'Elliot Ridge', 'll': [-106.42, 39.86], 'sids': [u'USS0006K29S 6'], 'state': 'CO', 'valid_daterange': [['1983-01-12', '2016-04-05']], 'uid': 77459}
    data =  [[u'2012-01-01', [u'21.5', u' ', u'U'], [u'5', u' ', u'U']],
           [u'2012-01-02', [u'29.5', u' ', u'U'], [u'12', u' ', u'U']],
           [u'2012-01-03', [u'32.0', u' ', u'U'], [u'19', u' ', u'U']],
           [u'2012-01-04', [u'27.5', u' ', u'U'], [u'12', u' ', u'U']],
           [u'2012-01-05', [u'35.5', u' ', u'U'], [u'18', u' ', u'U']]]
    climateParams = ['maxt', 'mint' ]

    s = Station(observationClass = DailyWxOb)
    s._set(stationMeta = meta, climateParameters = climateParams)
    print s.name
    print s.hasWxData

    s = Station(observationClass = DailyWxOb)
    s._set(stationMeta = meta, climateParameters = climateParams, stationData = data)
    print s.name
    print s.hasWxData

    print s._dumpDataToList(includeHeader = True)



