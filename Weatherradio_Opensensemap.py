import turtle 

import json
import requests
import numpy as np
import math 
from datetime import time
from datetime import date
from datetime import datetime
import time 

url_source = 'https://agroberry.tailfb656.ts.net'
url_destination = 'https://api.opensensemap.org/boxes/65aaa0371081050007f62301/data'

def getdata():
  
  global response_source
  response_source = requests.get(url_source)
  sensor_data_json = response_source.json()
  
  if response_source.status_code == 200:
      
  
      print('Daten erfolgreich abgerufen:' + "\n", sensor_data_json)
       
      T = round((sensor_data_json['weather']['BME280']['Temp']), 2)
      Pres = round((sensor_data_json['weather']['BME280']['Pres']), 2)
      Hum = round((sensor_data_json['weather']['BME280']['Hum']),2)
      Tamb = round((sensor_data_json['weather']['MLX90614']['T amb']),2)
      Tobj = round((sensor_data_json['weather']['MLX90614']['T obj']),2)
      Lux = round((sensor_data_json['weather']['TSL2591']['Lux']),5)
      IR = round((sensor_data_json['weather']['TSL2591']['IR']),2)

      # Berechnung - Taupunkt 
      #(Der Punkt, der Temperatur, wo sich das Wasser auf die Oberfläche absetzt ): 

      # vorgeschlagene Konstanten für die "Magnus Formel"
      a = 7.5
      b = 237.5
      c = 6.1078
      
      # Berechung des Sättigungs-Dampfdrucks 
      # saturationVapourPressure (sVP) = Sättigungsdampfdruck 


    
      # Durschnittstemperatur der Luft: 
      Tmit = round(((T+Tamb)/2),2) 
      print("Das ist der Durschnittswert der Umgebungstemperatur:", Tmit )
      sVP = c * pow(10, ((Tmit * a) / (Tmit + b)))
      print("Das ist der Sättigungs-Dampfdrucks :", sVP)

    
      # Berechnung des Dampfdrucks (vapourPressure)
      VP = ( (Hum * sVP) / 100)  
      print("Das ist der VP:", VP)

    
      # Dewpoint - Taupunkt (Tau)
      v = math.log10(VP / c) 
      Tau = round(( b * v / (a - v) ), 2)
      print("Das ist der Dewpoint:", Tau)

    
      #Berechnung - Cloud couverage   
      #K1 Werte ändern, wenn die Funktion des Graphen nicht konstant bleibt (siehe Opensensemap)
      if Tamb >= 30:
        K1 = 33
        K2 = 0
        K3 = 8
        K4 = 100
        K5 = 100
        K6 = 0
        K7 = 0
      else: 
        K1 = 33
        K2 = 0
        K3 = 4
        K4 = 100
        K5 = 100
        K6 = 0
        K7 = 0

      if((K2/10-Tamb)) < 1:
        print("Bedingung:", K2/10-Tamb)
        T67 = np.sign(K6) * np.sign(Tamb - K2/10) * abs((K2/10-Tamb))
        print("Das ist T67 (1):", T67)
      else: 
        T67 = (K6/10) * np.sign(Tamb-K2/10)* ((np.log(abs(K2/10-Tamb)))/np.log(10)+K7/100)
        print("Das ist T67 (2):", T67)

      print(T67)
      Td = Tobj - (K1/100)*(Tamb-K2/10)+(K3/100)*(math.exp(K4/1000*Tamb))*(K5/100) + T67
      print("Das ist der Td", Td)

      
      Tskycorrect = round((Tobj-Td),2) 
      print('Das ist korr. Himm. Temp:', Tskycorrect)
      sTc_clear = -8  # Stc = skytempeaturcoefficient 
      sTc_overcast = 3 # EXPERIMENT!: von 0 auf 3 geänder, da am 4.3.2024 sich Nebel gebildet hat, wird es
      # als "100%" Bew. angenommen. Warum 3? er korr. Himm. Wert kommt aufgerundet auf 3.   
      # Ausprobieren, ob es bessere Werte liefert. 


      # Die eigentliche Rechnung:
      if Tskycorrect < sTc_clear:
        Tskycorrect = sTc_clear
      elif Tskycorrect > sTc_overcast:
         Tskycorrect = sTc_overcast 
      print('Das ist korr. Himm. Temp2 : ', Tskycorrect)
      # Bew = rel. Bewölkungsgrad, da Weatherradio ein kleinen Teil vom Himmel abdeckt 
      Bew = ((Tskycorrect - (sTc_clear)) * 100) / (sTc_overcast - (sTc_clear)) 
      print('Das ist der Bewölkungsgrad:', Bew)

      # eigener Versuch Regenwahrscheinlichkeit zu berechnen:
      Rain = round(((Bew/Tau)),2) #vorherige Idee: /(Tau*Bew)/100)
      print("Regenwahrscheinlichkeit:", Rain)

      # zweiter Ansatz für die Berechnung der Himmelstemperatur: 
      U = time.gmtime().tm_hour + 1
      print("Uhrzeit:", U)
      Tsky2 = Tmit * ((0.711 + 0.0056 * Tau + 0.000073 * (Tau)**2 + 0.013 * math.cos(15* U))**0.25)
      print("Sky2:", Tsky2)
      # Ausgabe zeigt einen zu hohen Wert für eine Himmelstemp., daher wird dieser Wert nicht genommen

      #Berechnung - SQM 
      #SQM = Himmelshelligkeit --> Je höher der Wert, desto sichtbarer das Sternenmeer 
      SQM = round((np.log10((Lux)/108000)/-0.4), 2)
      print('Das ist der SQM:', SQM) 
    
      global data_to_send
      data_to_send = {
        '65aaa0371081050007f62302': T,
        '65aaa0371081050007f62303': Pres,
        '65aaa0371081050007f62304': Hum,
        '65aaa0371081050007f62305': Tamb,
        '65aaa0371081050007f62306': Tobj,
        '65aaa0371081050007f62307': Lux,
        '65aaa0371081050007f62308': IR,
        '65e112512ddccf0008f07173': SQM,
        '65e112512ddccf0008f07175': Bew,
        '65e48871cbf57000074204af': Rain,
        '65e48871cbf57000074204b1': Tau,
        '65ef41d304301300070f7269': Tskycorrect
        
      }
    #print(data_to_send)
  else:
    print(f'Fehler bei der Anfrage, Statuscode: {response_source.status_code}')

def senddata():
  response_destination = requests.post(url_destination, json=data_to_send)
  try:
      # Überprüfe, ob die Anfrage erfolgreich war 
      #(Status-Code 201 für erfolgreiche Übertragung erforderlich)
    if response_destination.status_code == 201:  
      print('Daten erfolgreich an die andere API gesendet')
    else:
      print(
        f'Fehler bei der Anfrage an die andere API, Statuscode: {response_destination.status_code}'
        )

  except requests.exceptions.RequestException as e:
    print('Fehler bei der Anfrage an die andere API:', e)

  




# Der "runtergebrochene Code"
getdata()
senddata()



