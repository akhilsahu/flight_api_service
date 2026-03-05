#!/usr/bin/env python3
"""
Cleartrip Itinerary Creation API Request
Makes a POST request to create a flight itinerary
"""

import requests
import json

# API endpoint
url = "https://www.cleartrip.com/itin/v7/itinerary/create"

# Headers from the original request
headers = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
    "api-version": "3.0",
    "app-agent": "DESKTOP",
    #"baggage": "sentry-environment=production,sentry-public_key=38a8785b30295eec5bb15535a6fc01f8,sentry-trace_id=b681b440039a4074af107b981f17945d,sentry-org_id=4510040130650112,sentry-transaction=%2Fflights%2Fresults,sentry-sampled=true,sentry-sample_rand=0.09813687084257194,sentry-sample_rate=0.1",
    "channel": "desktop",
    "content-type": "application/json",
    "origin": "https://www.cleartrip.com",
    "partner-id": "10000000",
    "priority": "u=1, i",
    "referer": "https://www.cleartrip.com/flights/results?adults=1&childs=0&infants=0&class=Economy&depart_date=20/04/2026&from=DEL&to=LKO&intl=n&origin=DEL%20-%20New%20Delhi,%20IN&destination=LKO%20-%20Lucknow,%20IN&sft=&sd=1772652407070&rnd_one=O&isCfw=false&utm_source=google&utm_medium=cpc&utm_campaign=BR_Cleartrip-Desktab&isFF=false&sourceCountry=New%20Delhi&destinationCountry=Lucknow&nonStop=",
    "sec-ch-ua": '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
  #  "sentry-trace": "b681b440039a4074af107b981f17945d-b7f930f1302f3b9a-1",
  #  "traceparent": "00-9787d9e36bbcbbb86ba9c39270ba4048-88d38a5e2a963415-01",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
    "x-client-id": "cleartrip",
    "x-source-type": "Desktop",
    "x-unified-header": '{"platform":"desktop","trackingId":"72942707-4d81-4486-b3a2-6b52594fdf5c","source":"CLEARTRIP","deviceModel":"macintosh"}',
    "demand-core-enabled": "true",
    "dataid": "DEL|LKO|20/04/2026|1|0|0|ECONOMY|10000000|10000000|UNKNOWN|IN|DEFAULT|5e1708912322f7f988785d0e2d654bba4ec0d45b449b926091f8be50a303308b_1772703408611--DEL|LKO|20/04/2026||1|0|0|ECONOMY|DEFAULT|RETAIL|CORPORATE|SEGMENT_COUNT|PRICE|CHEAPEST_FARE_FILTER_1|10000000|INR|IN|UNKNOWN",
    "cookie": "Apache=f0da3c5a.64b5a955c8c2b; ct-auth-preferences=IN|INR; currency-pref=INR; statsig-stableid=6e898a0a-9b8d-4d20-9a78-edee2d188751; WZRK_G=498fe5717e3346b094d09f698b6b640a; ct-dvId=qhG%2BepkOmgr5PNReOLGw1Uas29W6GBdrTR9l9PGN5Jbl68iA%2BSfUeefOmTYbQSA%2FAWX0tydXK%2FoKgjVHsitr37981cLcP%2BquCOVzKRNVy5c%3D; _gcl_au=1.1.463754701.1771702287; mfKey=eardqr.1771702286993; _fbp=fb.1.1771702287303.392917479931502507; _ga=GA1.1.1083071623.1771702287; Source-Metafirstsource=GFS_Search; 35BS11281-cp-6AMDY5-previous=a7654e2958-1771702286985; ffEnabled=false; _ga_M9WKWY8MDB=GS2.1.s1771742184$o2$g0$t1771743761$j60$l0$h0; 35BS11281-cp-6AMDB1-previous=a7654e2958-1771702286985,8425dd474f-1771742183188; _ga_N9K6RL6ZY1=GS2.1.s1771742183$o1$g1$t1771743807$j21$l0$h0; source_Meta=google; source_firstsource=google; campaign_firstsource=BR_Cleartrip-Desktab; medium_firstsource=cpc; _gcl_gs=2.1.k1$i1772365791$u245072215; 35BS11281-gclid=Cj0KCQiA5I_NBhDVARIsAOrqIsYK58_8DPN9K1dJ_0EgKDVHFl2kE4JC2SSFeviImhcvzq2h0T9Hg3waAhudEALw_wcB|1772365793; utm_source=google; ct_statsig_experiments={\"search_v3\":\"b\"}; utm_marketing_tactic=; utm_creative_format=; utm_source_platform=; utm_content=; utm_term=; utm_campaign=BR_Cleartrip-Desktab; utm_medium=cpc; _gcl_aw=GCL.1772624348.Cj0KCQiAwYrNBhDcARIsAGo3u30nUlO1G7NqfQBA9YEwsHntNRlzlehQ0bLJqu4ncOsc6mftAR2ZfxYaAn8uEALw_wcB; noncleartrip=false; 35BS11281-ref=direct|direct|direct|direct|1772699598019; 35BS11281-last-referrer-time-stamp=direct|1772699598021; 35BS11281=115b276348-1772699598021; 35BS11281-cp=a7654e2958-1771702286985,8425dd474f-1771742183188,Cj0KCQiAwYrNBhDcARIsAGo3u30nUlO1G7NqfQBA9YEwsHntNRlzlehQ0bLJqu4ncOsc6mftAR2ZfxYaAn8uEALw_wcB,Cj0KCQiA5I_NBhDVARIsAOrqIsYK58_8DPN9K1dJ_0EgKDVHFl2kE4JC2SSFeviImhcvzq2h0T9Hg3waAhudEALw_wcB,f95f920ea9-1772645683282,115b276348-1772699598021; 35BS11281-cplp=a7654e2958-1771702286985,8425dd474f-1771742183188,f95f920ea9-1772645683282,115b276348-1772699598021; ak_bmsc=0719947D19688305BBEB6D5603E686E3~000000000000000000000000000000~YAAQVfEBF6CmnZ6cAQAAkbQwvR8K5gD7IoUrzJ7PnDwjCMqc0ctwkgxSB9aLgbjxkgqY0xnVq4YiVHFuGBccnO0/dZSpWv0KQlaoXGZT9Wo+n9LNj+s2Mg9qtIcvPuTSPqR9XMbnCvGnwJfQVcrTkA6J3HeFCqtaZfbb9vbT3qwTtfv9o3C9tQ3Ccp0tXkAjf0q4wMttK0Thx2O5uJlQv6Q3Qc9hr21kcf7yHjbetdxa7eUqB4avt9c0HiA8venygKyVLe/ZuUnDPTAupjScUdnkEBza63qm25lPGIkYXtig/F2GjcTJkTAqC6x4c9Uvw5xNtxxwi36WfQTSyHMzy9NYjud06OY8CLTusoNbmhTC/hK5LB3cRTz53LJDfn/57xhTyF3xyvosUVauM4O5C9DVSwvnyKPY/5aLZOwHkY/CsjLw51i2dLe9CazlAEp3TrF/I+GbzztMFWsjjgsMjNQJiFgsFLFOw5u9q8fmQnY=; mob=0; mf_visitid=1lubic2.1772704258481; mf_utms=%7B%22infants%22%3A%220%22%2C%22from_header%22%3A%22New%2520Delhi%22%2C%22adults%22%3A%221%22%2C%22intl%22%3A%22n%22%2C%22childs%22%3A%220%22%2C%22depart_date%22%3A%2220%2F04%2F2026%22%2C%22isOD%22%3A%22true%22%2C%22isCfw%22%3A%22false%22%2C%22to_header%22%3A%22Lucknow%22%2C%22from%22%3A%22DEL%22%2C%22isFF%22%3A%22true%22%2C%22to%22%3A%22LKO%22%2C%22isMultiFare%22%3A%22true%22%2C%22class%22%3A%22Economy%22%2C%22return_date%22%3A%22%22%7D; _uetsid=c2565ce017be11f1b372c51631ddbc79; _uetvid=9591b8807a0c11f0a49b0714e3af5ebc; bm_sv=2BD9EF824C9A1D9D0E8F735CDDBA335A~YAAQVfEBF8KVnp6cAQAA/t5tvR+POdNT14QuL08SwBBEqlfSRaPCQOBMpLH+ARtSvxYXtl9nhfRktbHYUEAVU/dYF01XTo0GvGImTx3Z3RFgIDONY9UnFuJE5fzjwzp5smhQH7VyyEP6oH/s1Fw31ppI9tRG03piOQx8rK5nuicoSnPqsmHWv98cYC0WpEhwgAJztPcWADhc0WzPCgbIh1yuEP4HvNLAR6gJ05A/Vrq9ZFaegu/7e/1JDH61DBCXMzIQReo=~1; WZRK_S_W8R-KK8-W74Z=%7B%22s%22%3A1772698630%2C%22t%22%3A1772704620%2C%22p%22%3A43%7D; cto_bundle=FbGQbF9lSVdhcnBCZnhpYkg4VTk4bzhFdFYwUXJZWjhCdjk2OTMweG1oN2VtZHpRZCUyQnl4Tk1EbUh4R280Wk5lOFVwVmclMkZrRE1RNHpZZGR5blhLdWFnVkk3Z0dOMktLZXIyblBqQ3BKeDZ0VE4lMkZKR2lkQ3pqeTFoenhIczM0VHRlRDFLckZrakswQXAxU0pDSVRJWVVGbmVncUtoc3Y2UW5PZ0NNTW1qOEoxaWxla1JDSFVVZ1RWcUJXMjJBdkViWlZ2blQ; _ga_5CWGPF7QB9=GS2.1.s1772698630$o20$g1$t1772704683$j60$l0$h0"
}

# Request payload
payload = {
    "searchId": "DC_Search-9b761dc2-8a98-4038-a501-dbd292220679",
    "queryContext": {
        "searchIntents": {
            "sectors": [
                {
                    "index": 1,
                    "origin": "DEL",
                    "destination": "LKO",
                    "departDate": "20/04/2026",
                    "cabinType": "ECONOMY",
                    "journeyId": "J1",
                    "paxInfos": [
                        {
                            "paxType": "ADT",
                            "paxCount": 1
                        }
                    ]
                }
            ],
            "sft": ""
        },
        "travelOptionMap": {
            "J1": {
                "subTravelOptions": [
                    {
                        "subTravelOptionId": "6E-6479-DEL-LKO-1776696600",
                        "fareId": "FARE_FAMILY__DEL|LKO|1776623400000|1|0|0|ECONOMY|IN|AJORST|FR||REGULAR|production_IN_search_indigo_newskies_new_XO~DEL^LKO^6E^6479__INDIGO__RUIP__J__RETAIL__FLEXI__true__DOMESTIC",
                        "price": 3525
                    }
                ],
                "travelOptionId": "6E-6479-DEL-LKO-1776696600"
            }
        },
        "specialRtData": {}
    },
    "responseContext": {
        "domain": "IN",
        "currency": "INR",
        "responseVersion": "V1"
    },
    "demandContext": {
        "userId": "",
        "loggedInStatus": "NON_LOGGED_IN"
    },
    "metaDataContext": {
        "defaultCoupon": "",
        "abFeatures": [],
        "trackingDetails": {
            "selectedCardListId": [
                3
            ]
        },
        "od": True,
        "multiFare": True
    }
}


def make_request():
    """Make the POST request to Cleartrip API using a session to imitate a browser"""
    try:
        print("Making POST request to Cleartrip API...")
        print(f"URL: {url}\n")
        
        # Create a session to maintain cookies and connection pooling like a browser
        session = requests.Session()
        
        # Set default headers for the session
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Connection": "keep-alive",
        })
        
        # Parse and set cookies from the cookie string
        cookie_string = headers.get("cookie", "")
        if cookie_string:
            cookie_pairs = cookie_string.split("; ")
            for pair in cookie_pairs:
                if "=" in pair:
                    key, value = pair.split("=", 1)
                    session.cookies.set(key, value, domain=".cleartrip.com")
        
        # Remove cookie from headers since we're using session cookies
        request_headers = headers.copy()
        if "cookie" in request_headers:
            del request_headers["cookie"]
        
        # Make the request with the session
        response = session.post(
            url,
            headers=request_headers,
            json=payload,
            timeout=30,
            allow_redirects=True
        )
        
        # Print response details
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
        
        print("\n" + "="*80)
        print("Response Body:")
        print("="*80)
        
        # Pretty print JSON response
        try:
            response_json = response.json()
            print(json.dumps(response_json, indent=2))
        except json.JSONDecodeError:
            print(response.text)
        
        # Close session
        session.close()
        
        return response
        
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return None


if __name__ == "__main__":
    response = make_request()
    
    if response and response.status_code == 200:
        print("\n✓ Request successful!")
    else:
        print("\n✗ Request failed!")