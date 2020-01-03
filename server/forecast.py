import requests
from typing import List, Dict
from lxml import etree as ET
from datetime import datetime, timedelta
from dateutil.parser import parse

def get_forecast(lat: float, lon: float, height: int) -> List[Dict[str, str]]:
    """Get weather data from https://api.met.no/weatherapi/locationforecastlts/1.3/documentation

    Arguments:
        lat {float} -- Latitude
        lon {float} -- Longitude
        height {int} -- Height

    Returns:
        List[Dict[str, str]] -- List of observation dictionaries
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
            
            fmo = (ts_from - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
            t = ts_to.strftime("%Y-%m-%dT%H:%M:%SZ")
            
            e = root.xpath(f".//time[@from='{fmo}' and @to='{t}']")
            if len(e) > 0:
                obs["precipitationPrevHour"] = e[0].find(".//precipitation").get("value")
            
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
