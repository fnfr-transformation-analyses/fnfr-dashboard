# -*- coding: utf-8 -*-
import pandas as pd
import requests
import json
import math
import time
from utils.utils import *

# UMLS API
# Query UMLS API with a list of labels to check if there is an exact string
# correspondance with a concept from the metathesaurus


def queryUMLSAPI_exactSearch(labels: list) -> pd.DataFrame:
    """
    Queries the Unified Medical Language System (UMLS) API with a list of labels to check if they yield 
    an exact match with any concept of UMLS Metathesaurus. 
    Arg: list of labels to look for
    Returns: Pandas DataFrame containing the results : 
    [searchTerm, matchType (failed or exact), UMLSCUI, UMLS_Source vocabulary, label from source vocabulary]
    """    

    # We will look into these source vocabularies from UMLS (can be updated if needed)
    targetSources = [
        "MSH", "MSHFRE", "PSY", "MDR", "MDRFRE", "NCI", "AOD", "ICD10", 
        "ICD10CM", "ICD10PCS", "AOT", "ATC", "CCC", "CDCREC", "CHV", "CPM", 
        "CPT", "CSP", "CST", "CVX", "DDB", "DRUGBANK", "DXP", "FMA", "GO", 
        "GS", "HPO", "ICF", "ICF-CY", "ICPC", "JABL", "LCH", "LNC", "MCM", 
        "MEDCIN", "MMX", "MMSL", "MTH", "MTHMST", "MTHSPL", "NCBI", "NEU", 
        "NIC", "NOC", "OMS", "PCDS", "WHO"
    ]

    output = []

    for label in labels:
        string = label

        url = f"https://uts-ws.nlm.nih.gov/rest/search/current?apiKey={apiKey}&string={string}&searchType=exact" 

        payload = {}
        headers = {
            'Cookie': 'AWSALB=sVwg1oKL6FU6xQZxcgE5WW5enDsYSrH0dRr1z90SdxFtR+DSEHm12S3QHd/9yl0Op0ipnbwEK23Fg2PigrndMAEn47LRC8q6fW4cycAbKxwEjz2WVddu+pjGSk4xjmbKM9hhUY02jt2cpTsHSUOo/CV6xkYfPi0m5AaJ9OdvZNg/+61nIvtG+DFoaIyCrA==; AWSALBCORS=sVwg1oKL6FU6xQZxcgE5WW5enDsYSrH0dRr1z90SdxFtR+DSEHm12S3QHd/9yl0Op0ipnbwEK23Fg2PigrndMAEn47LRC8q6fW4cycAbKxwEjz2WVddu+pjGSk4xjmbKM9hhUY02jt2cpTsHSUOo/CV6xkYfPi0m5AaJ9OdvZNg/+61nIvtG+DFoaIyCrA=='
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        try:
            results = [x for x in json.loads(response.text)['result']['results'] if x['rootSource'] in targetSources]
            if (results):
                for result in results:
                    source = result['rootSource']
                    CUI = result['ui']
                    source_label = result['name']

                    output.append({
                        'searchedTerm': string,
                        'matchType': 'exact_match',
                        'UMLSCUI': CUI,
                        'UMLS_Source': source,
                        'Source_label': source_label
                    })

                    print(string, source, result['ui'])
            
            else:
                output.append({
                    'searchedTerm': string,
                    'matchType': 'failed',
                })

                print(string, "NOT FOUND")

        except Exception as e:
            print(e)

        time.sleep(0.5)

    return pd.DataFrame(output)
