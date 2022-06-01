__author__ = 'Юзов Евгений Борисович'

## -*- coding: utf-8 -*-
# coding:utf-8

import requests
import xmltodict
import time
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError


def start_rec(fqdn):
    # id пространств (coSpace) начинаются на 140742, см. настройку CUCM "Conference Bridge Prefix"
    url_get = 'https://' + fqdn + ':8443/api/v1/coSpaces?filter=140742'
    # url_get = 'https://srv-uc-cms.taif.loc:8443/api/v1/coSpaces'
    # url_get = 'https://srv-uc-cms.taif.loc:8443/api/v1/coSpaces/886f18f4-53b9-4636-ac87-c58c6a934979'
    url_put = 'https://' + fqdn + ':8443/api/v1/coSpaces/'
    # Существующий профиль звонка с автоматической записью
    callProfile_auto = '53fd64d2-9d6f-4207-8e66-707d86a483c2'
    # Существующий профиль звонка с ручной записью
    callProfile_man = '91aa2fd5-e76c-4f9e-ac13-6dcd4e5cb34f'
    DEBUG = 0
    total = 0

    try:
        # Запрос автоматически созданных ad-hoc пространств (coSpace)
        response = requests.get(url_get, auth=HTTPBasicAuth('apiadmin', 'Cisc0Api@1'), verify=False)
        response.raise_for_status()
    except HTTPError as http_error:
        print(f'HTTP error occurred: {http_error}')
    except Exception as error:
        print(f'Other error occurred: {error}')
    else:
        doc = xmltodict.parse(response.text)
        if DEBUG == 1:
            print(doc)
        # Общее количество найденных ad-hoc пространств (coSpace)
        total = doc['coSpaces']['@total']
        if int(total) > 0:
            for coSpace in doc['coSpaces']['coSpace']:
                # Здесь исправляем непонятный глюк с извлечением значений из OrderedDict
                if int(total) == 1:
                    coSpaceId = doc['coSpaces']['coSpace']
                    url_put_full = url_put + coSpaceId['@id']
                else:
                    url_put_full = url_put + coSpace['@id']
                try:
                    response = requests.get(url_put_full, auth=HTTPBasicAuth('apiadmin', 'Cisc0Api@1'),
                                            verify=False)
                    doc_coSpace = xmltodict.parse(response.text)
                    # Проверяем есть ли среди индексов конкретного пространства (coSpace) индекс "callProfile"
                    profile = 'callProfile'
                    coSpaceIdx = []
                    for key in doc_coSpace['coSpace']:
                        coSpaceIdx.append(key)
                    '''# Если нет, то присваиваем "callProfile", т.е. включаем автозапись
                    if profile not in coSpaceIdx:
                        response = requests.put(url_put_full, auth=HTTPBasicAuth('apiadmin', 'Cisc0Api@1'),
                                                verify=False, data={'callProfile': callProfile_auto})'''
                    # Если нет, то присваиваем "callProfile", т.е. включаем ручную запись
                    if profile not in coSpaceIdx:
                        response = requests.put(url_put_full, auth=HTTPBasicAuth('apiadmin', 'Cisc0Api@1'),
                                                verify=False, data={'callProfile': callProfile_man})
                        response.raise_for_status()
                        print('Запись включена!')
                except HTTPError as http_error:
                    print(f'HTTP error occurred: {http_error}')
                except Exception as error:
                    print(f'Other error occurred: {error}')


if __name__ == '__main__':
    while True:
        start_rec('srv-uc-cms.taif.loc')
        time.sleep(10)