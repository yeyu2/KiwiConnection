from streamlit.connections import ExperimentalBaseConnection
from streamlit.runtime.caching import cache_data

import requests

class KiwiConnection(ExperimentalBaseConnection):
    """Basic st.experimental_connection implementation for DuckDB"""

    def _connect(self, **kwargs) -> dict:
        if 'apikey' in kwargs:
            key = kwargs.pop('apikey')
        else:
            key = self._secrets["KIWI_API_KEY"]
        self.headers = {"apikey": key}
        return self.headers


    def query(self, ttl=3600, **kwargs) -> dict:
        @cache_data(ttl=ttl)
        def _query(headers, **kwargs) -> dict:
            BASE_URL = 'https://api.tequila.kiwi.com/v2/search'
            params = {
                "fly_from": kwargs.get('fly_from'),
                "fly_to": kwargs.get('fly_to'),
                "date_from": kwargs.get('date_from'),
                "date_to": kwargs.get('date_to'),
                "adults": kwargs.get('adults'),
                "children": kwargs.get('children'),
                "infants": kwargs.get('infants'),
                "sort": kwargs.get('sort'),
                "limit": kwargs.get('limit'),
                "curr": kwargs.get('curr', 'USD')
            }
            if kwargs.get('return_from'):
                params['return_from'] = kwargs.get('return_from')
            if kwargs.get('return_to'):
                params['return_to'] = kwargs.get('return_to')
            if kwargs.get('max_fly_duration'):
                params['max_fly_duration'] = kwargs.get('max_fly_duration')
            if kwargs.get('max_sector_stopovers'):
                params['max_sector_stopovers'] = kwargs.get('max_sector_stopovers')

            response = requests.get(BASE_URL, params=params, headers=headers)
            response = response.json()
            
            return response
        
        return _query(self.headers, **kwargs)