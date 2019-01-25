import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from dateutil.parser import parse

def get_forecast(lat, lon, height):
    """
    Weather forecasting from MET Norway Weather API using the location forecast (LTS) endpoint [1]. 

        :param lat: Latitude
        :param lon: Longitude
        :param height: Height over sea level
        :type lat: float
        :type lon: float
        :type height: int
        :return: return list of dictionaries with weather observations
        :rtype: list

    [1]: https://api.met.no/weatherapi/locationforecastlts/1.3/documentation
    """
    url = f'https://api.met.no/weatherapi/locationforecastlts/1.3/?lat={lat}&lon={lon}&msl={height}'
    res = requests.get(url)

    root = ET.fromstring(res.content)

    forecasts = []
    for el in root.findall('.//time'):

        ts_from = parse(el.get('from'))
        ts_to = parse(el.get('to'))

        # Get temp, humidity, vind etc. hourly observation
        if ts_from == ts_to:
            obs = {}
            obs['timestamp'] = el.get('from')
            obs['temperature'] = el[0].find('temperature').get('value')
            obs['windDirection'] = el[0].find('windDirection').get('deg')
            obs['windSpeed'] = el[0].find('windSpeed').get('mps')
            obs['humidity'] = el[0].find('humidity').get('value')
            obs['pressure'] = el[0].find('pressure').get('value')
            obs['cloudiness'] = el[0].find('cloudiness').get('percent')
            obs['fog'] = el[0].find('fog').get('percent')
            
            #Extract last hour of precipitation (Only data for next 48 hours)
            for ele in root.findall('.//time'):
                p_ts_from = parse(ele.get('from'))
                p_ts_to = parse(ele.get('to'))
                if p_ts_from == (ts_from - timedelta(hours=1)) and p_ts_to == ts_to:
                    obs['precipitationPrevHour'] = ele[0].find('precipitation').get('value')

            forecasts.append(obs)

    return forecasts

if __name__ == "__main__":
    lat = 55.675806
    lon = 12.510884
    height = 5

    forecast = get_forecast(lat, lon, height)
    
    import pprint
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(forecast)
