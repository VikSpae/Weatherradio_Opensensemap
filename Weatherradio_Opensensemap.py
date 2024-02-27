import requests
import json

url_source = 'https://agroberry.tailfb656.ts.net'

try:
  response_source = requests.get(url_source)


  if response_source.status_code == 200:

    data_json = response_source.json()
    print('Daten erfolgreich abgerufen:', data_json)

    url_destination = 'https://api.opensensemap.org/boxes/65aaa0371081050007f62301/data'
    
    T = data_json['weather']['BME280']['Temp']
    Pres = data_json['weather']['BME280']['Pres']
    Hum = data_json['weather']['BME280']['Hum']
    Tamb = data_json['weather']['MLX90614']['T amb']
    Tobj = data_json['weather']['MLX90614']['T obj']
    Lux = data_json['weather']['TSL2591']['Lux']
    IR = data_json['weather']['TSL2591']['IR']
    
    data_to_send = {
        '65aaa0371081050007f62302': T,
        '65aaa0371081050007f62303': Pres,
        '65aaa0371081050007f62304': Hum,
        '65aaa0371081050007f62305': Tamb,
        '65aaa0371081050007f62306': Tobj,
        '65aaa0371081050007f62307': Lux,
        '65aaa0371081050007f62308': IR,
    }
    print(data_to_send)

    try:
      response_destination = requests.post(url_destination, json=data_to_send)

      # Überprüfe, ob die Anfrage erfolgreich war (Status-Code 201)
      if response_destination.status_code == 201:  #vorher 200
        #<-- Statuscode für .GET Für Post = 201!!! Also doch alles richtig
        print('Daten erfolgreich an die andere API gesendet')
      else:
        print(
            f'Fehler bei der Anfrage an die andere API, Statuscode: {response_destination.status_code}'
        )

    except requests.exceptions.RequestException as e:
      print('Fehler bei der Anfrage an die andere API:', e)

  else:
    print(f'Fehler bei der Anfrage, Statuscode: {response_source.status_code}')

except requests.exceptions.RequestException as e:
  print('Fehler bei der Anfrage:', e)


