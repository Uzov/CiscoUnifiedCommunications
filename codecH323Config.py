__author__ = 'Юзов Евгений Борисович'

## -*- coding: utf-8 -*-
# coding:utf-8

import requests
import xmltodict
import time
import chardet
from subprocess import PIPE, Popen
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError

"""В функции с помощью утилиты ping проверяется доступность сетевых узлов. Аргументом функции является
кортеж, в котором каждый сетевой узел представлен именем хоста или ip-адресом."""


def host_ping(hosts):
    access_dict = {}
    for host in hosts:
        reply = Popen(['ping', host], stdout=PIPE, stderr=PIPE, shell=True)
        reply.wait()
        line = reply.communicate()[0]
        line = line.decode(chardet.detect(line)['encoding'])
        if DEBUG == 1:
            print(line)
        if reply.returncode == 0 and line.find('Request timed out.') == -1 \
                and line.find('Destination host unreachable.') == -1 \
                and line.find('PING: transmit failed. General failure.') == -1:
            if DEBUG == 1:
                print(f'Адрес {host} доступен!')
            access_dict_item = {host: True}
            access_dict.update(access_dict_item)
        else:
            if DEBUG == 1:
                print(f'Адрес {host} не доступен!')
            access_dict_item = {host: False}
            access_dict.update(access_dict_item)
    return access_dict


def get_sip_registration(ip):
    url_get_sip_status = '/getxml?location=Status/SIP/Registration/Status'
    try:
        # Запрос статуса регистрации на Call Manager
        response = requests.get('https://' + ip + url_get_sip_status,
                                auth=HTTPBasicAuth('admin', 'P@ssw0rd'), verify=False)
        response.raise_for_status()
    except HTTPError as http_error:
        print(f'HTTP error occurred: {http_error}')
    except Exception as error:
        print(f'Other error occurred: {error}')
    else:
        doc = xmltodict.parse(response.text)
        status = doc['Status']['SIP']['Registration']['Status']
        if DEBUG == 1:
            print(f'Статус регистрации {ip} SIP: {status}')
    return status


def get_h323_registration(ip):
    # возможные значения Registered или Inactive
    url_get_gatekeeper = '/getxml?location=/Status/H323/Gatekeeper/Status'
    try:
        # Запрос статуса регистрации на гейткипере
        response = requests.get('https://' + ip + url_get_gatekeeper,
                                auth=HTTPBasicAuth('admin', 'P@ssw0rd'), verify=False)
        response.raise_for_status()
    except HTTPError as http_error:
        print(f'HTTP error occurred: {http_error}')
    except Exception as error:
        print(f'Other error occurred: {error}')
    else:
        doc = xmltodict.parse(response.text)
        status = doc['Status']['H323']['Gatekeeper']['Status']
        if DEBUG == 1:
            print(f'Статус регистрации {ip} H323: {status}')
    return status


"""Функция дополняет конфиг живого кодека так, чтобы он зарегистрировался на гейткипере."""


def codec_config(ip_address, gatekeeper):
    # MAC адрес формата 08:4F:A9:6D:CF:7F
    url_get_mac = '/getxml?location=/Status/Network/Ethernet/MacAddress'
    # телефонный номер?
    url_get_e164 = '/getxml?location=/Status/UserInterface/ContactInfo/ContactMethod/Number'
    headers = {'Content-Type': 'application/xml'}
    """Регистрируем кодек на гейткипере только если он уже зарегистрирован на Call Manager, т.к. иначе мы не узнаем 
    телефонный номер, что приведёт к ошибке регистрации на гейткипере."""
    if get_sip_registration(ip_address) == 'Registered':
        try:
            # Узнаём телефонный номер с настроек сервера Call Manager
            response = requests.get('https://' + ip_address + url_get_e164,
                                    auth=HTTPBasicAuth('admin', 'P@ssw0rd'), verify=False)
            response.raise_for_status()
        except HTTPError as http_error:
            print(f'HTTP error occurred: {http_error}')
        except Exception as error:
            print(f'Other error occurred: {error}')
        else:
            doc = xmltodict.parse(response.text)
        if 'Number' in (doc['Status']['UserInterface']['ContactInfo']['ContactMethod']):
            tel_number = doc['Status']['UserInterface']['ContactInfo']['ContactMethod']['Number']
        else:
            if 'Number' in (doc['Status']['UserInterface']['ContactInfo']['ContactMethod'])[0]:
                tel_number = doc['Status']['UserInterface']['ContactInfo']['ContactMethod'][0]['Number']
            else:
                if 'Number' in (doc['Status']['UserInterface']['ContactInfo']['ContactMethod'])[1]:
                    tel_number = doc['Status']['UserInterface']['ContactInfo']['ContactMethod'][1]['Number']
                else:
                    tel_number = 9999
            if DEBUG == 1:
                print(f'Телефонный номер {ip_address}: {tel_number}')

        try:
            # Включаем на кодеке H323 протокол, даже если он уже был включен ранее
            xml = """
            <Configuration>
                <NetworkServices>
                        <H323>
                            <Mode valueSpaceRef="/Valuespace/TTPAR_OnOff">On</Mode>
                        </H323>
                </NetworkServices>
            </Configuration>"""
            # set what your server accepts
            response = requests.post('http://' + ip_address + '/putxml', auth=HTTPBasicAuth('admin', 'P@ssw0rd'),
                                     verify=False, data=xml, headers=headers)
            doc = xmltodict.parse(response.text)
            if DEBUG == 1 and str(*doc['Configuration']) == 'Success':
                print(f'H323 режим на {ip_address} включен!')
        except HTTPError as http_error:
            print(f'HTTP error occurred: {http_error}')
        except Exception as error:
            print(f'Other error occurred: {error}')
        if get_h323_registration(ip_address) == 'Inactive':
            try:
                # Регистрация кодека на гейткипере
                xml = f"""
                <Configuration>
                    <H323>
                        <CallSetup>
                            <Mode valueSpaceRef="/Valuespace/TTPAR_H323_GkMode">Gatekeeper</Mode>
                        </CallSetup>		
                        <Gatekeeper>
                            <Address valueSpaceRef="/Valuespace/STR_0_255_NoFilt">{gatekeeper}</Address>
                        </Gatekeeper>
                        <H323Alias>
                            <E164 valueSpaceRef="/Valuespace/STR_0_30_NoFilt"></E164>
                            <ID valueSpaceRef="/Valuespace/STR_0_49_NoFilt">{tel_number + '@' + gatekeeper}</ID>	
                        </H323Alias>
                    </H323>
                </Configuration>"""
                # set what your server accepts
                response = requests.post('http://' + ip_address + '/putxml', auth=HTTPBasicAuth('admin', 'P@ssw0rd'),
                                         verify=False, data=xml, headers=headers)
                doc = xmltodict.parse(response.text)
                if DEBUG == 1 and str(*doc['Configuration']) == 'Success':
                    print(f'Регистрация на H323 гейткипере {gatekeeper} включена!')
                    print(f'Состояние регистрации кодека {ip_address}: {get_h323_registration(ip_address)}.')
            except HTTPError as http_error:
                print(f'HTTP error occurred: {http_error}')
            except Exception as error:
                print(f'Other error occurred: {error}')


if __name__ == '__main__':
    DEBUG = 1
    gatekeeperIP = ('expc.taif.ru',)
    codecsIpTuple = ('10.100.76.10', '10.100.76.13', '10.100.76.14', '10.100.76.19', '10.100.76.21', '10.100.76.25',
                     '10.100.76.26', '10.100.76.27', '10.100.76.24', '10.100.76.37', '10.100.76.36', '10.100.76.42',
                     '10.100.76.43', '10.100.76.44', '10.100.76.51', '10.100.76.53', '10.100.76.54', '10.100.76.73')
    # Это для тестирования и дебага:
    # codecsIpTuple = ('10.100.76.10', '10.100.76.13')
    while True:
        alive_gatekeeper = host_ping(gatekeeperIP)
        """Если гейткипер пингуется, то регистрируем кодеки на этом гейткипере; если не пингуется ничего не делаем,
        а ждём 120 секунд"""

        if alive_gatekeeper.get(*gatekeeperIP):
            alive_codecs = host_ping(codecsIpTuple)
            for codecs, alive in alive_codecs.items():
                # Если кодек живой, то конфигурируем его
                if alive:
                    codec_config(codecs, *gatekeeperIP)
        time.sleep(120)
