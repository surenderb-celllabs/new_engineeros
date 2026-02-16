
import os
from dotenv import load_dotenv
load_dotenv()

from serpapi import GoogleSearch

from utils.colored_logger import ColoredLogger
logger = ColoredLogger(name="External APIs")

class GoogleApis:
    @staticmethod
    def trends(keywords: list) -> dict:
        try:
            params = {
                "engine": "google_trends",
                "q": "",
                "data_type": "TIMESERIES",
                "api_key": os.environ["SERPAPI_API_KEY"],
                "date": "today 12-m"
            }

            result_dict =  {} 
            chunked_list = []
            
            chunked_list = [keywords[i: i+5] for i in range(0, len(keywords), 5)]

            for l in chunked_list:
                logger.trace(f"Getting trends for {l}")
                params['q'] = ",".join(l)
                google_trend = GoogleSearch(params_dict=params)
                results = google_trend.get_dict()
                result_dict.update(
                    {i["query"]:i["value"] for i in results["interest_over_time"]["averages"]}
                )

            logger.trace(result_dict)
            return result_dict
        
        except Exception as e:
            logger.error(f"Error in GoogleApis.trends is: {e}")

# search = GoogleApis.trends(["coffee", "tea"])
# print(search)