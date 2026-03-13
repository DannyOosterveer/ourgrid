# OurGrid — Home Assistant Integratie

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
![GitHub release](https://img.shields.io/github/v/release/dannyoosterveer/ourgrid)

Met deze integratie koppel je OurGrid aan Home Assistant. OurGrid is een Nederlandse dienst die beloningen uitkeert wanneer je jouw energieverbruik verlaagt tijdens piekmomenten op het elektriciteitsnet (netcongestie).

## Wat doet de integratie?

- Toont wanneer er een uitdaging actief is
- Laat je via een knop deelnemen aan de uitdaging
- Toont de start- en eindtijd van de uitdaging
- Toont de vermogenslimiet en je actuele verbruik
- Toont je punten, huidige wisselkoers en verwachte opbrengst

## Wat kan je er mee?

Dankzij deze integratie kun je automatisch meedoen aan uitdagingen om netcongestie in de wijk te voorkomen. Dat doe je met deze integratie en een automatisering. Dat ziet er zo uit:
1. Er komt een uitdaging binnen, incl. start- en eindtijd, met een vermogenslimiet waar jij je verbruik onder moet houden
2. Je accepteert de uitdaging via de knop
3. Je zet bijvoorbeeld je laadpaal naar 0 watt of laat je thuisbatterij precies genoeg ontladen zodat je onder de vermogenslimiet blijft. Voor deze twee voorbeelden vind je hieronder een automatisering.

![OurGrid apparaat in Home Assistant](https://github.com/dannyoosterveer/ourgrid/blob/main/custom_components/ourgrid/brand/icon.png?raw=true)

## Vereisten

- Een actief OurGrid-account
- De OurGrid app, met daarin je gebruikersdata (te vinden onder Apparaten → Jouw huis automatisering)

## Installatie via HACS

> **Let op:** Deze integratie is nog niet opgenomen in de officiële HACS-store. Voeg de repository handmatig toe als custom repository.

1. Ga in Home Assistant naar **HACS → Integraties**
2. Klik op de **⋮** (drie puntjes) rechtsbovenin en kies **Custom repositories**
3. Voeg `https://github.com/DannyOosterveer/ourgrid` toe als categorie **Integration**
4. Zoek op `OurGrid` en installeer de integratie
5. Herstart Home Assistant

### Handmatige installatie

Kopieer de map `custom_components/ourgrid/` naar de map `custom_components/` in je Home Assistant configuratie.

## Configuratie

1. Ga naar **Instellingen → Apparaten & diensten → Integratie toevoegen**
2. Zoek op `OurGrid`
3. Vul de volgende gegevens in (te vinden in de OurGrid app onder Apparaten → Jouw huis automatisering):

| Veld | Omschrijving |
|------|--------------|
| **Regio** | Jouw OurGrid-regio (bijv. `arnhem`) |
| **Client ID** | Jouw unieke client-ID |
| **Client Secret** | Jouw wachtwoord / geheime sleutel |
| **Challenge Asset ID** | Asset ID van de uitdagingsmodule |
| **Meter Asset ID** | Asset ID van jouw meter |

## Entiteiten

Na installatie verschijnt er één apparaat **OurGrid** met de volgende entiteiten:

| Entiteit | Type | Omschrijving |
|----------|------|--------------|
| Uitdaging actief | Binary sensor | Aan als er een uitdaging beschikbaar is |
| Verbindingsstatus | Binary sensor | Aan als de verbinding werkt |
| Starttijd uitdaging | Sensor | Tijdstip waarop de uitdaging begint |
| Eindtijd uitdaging | Sensor | Tijdstip waarop de uitdaging eindigt |
| Uitdaging vermogenslimiet | Sensor | Maximaal toegestaan vermogen (W) |
| Huidig vermogen | Sensor | Huidig energieverbruik (W) |
| Wisselkoers | Sensor | Waarde per punt (€) |
| Verwachte opbrengst | Sensor | Geschatte verdienste huidige uitdaging (€) |
| Totaal punten | Sensor | Totaal verdiende punten |
| Uitdagingspunten (huidig) | Sensor | Punten van de huidige uitdaging |
| Uitdagingspunten | Sensor | Uitdagingspunten teller |
| Pieken vermeden | Sensor | Aantal vermeden pieken |
| Uitdaging accepteren | Button | Druk om deel te nemen aan een uitdaging |

## Automatiseringen

Kopieer onderstaande YAML naar Home Assistant via **Instellingen → Automatiseringen → ⋮ → YAML bewerken**.

### Laadpaal pauzeren tijdens uitdaging

Accepteert automatisch een uitdaging, zet de laadstroom van je laadpaal op 0A bij de starttijd en herstelt hem daarna. In dit voorbeeld werkt hij met mijn Alfen laadpaal. Pas `number.alfen_laadpaal_max_station_current` aan naar jouw laadpaal. Na de uitdaging zet hij het ampère van de laadpaal weer op 16A.

```yaml
alias: OurGrid - Laadpaal pauzeren tijdens uitdaging
description: >
  Accepteert automatisch een OurGrid-uitdaging, zet de laadstroom op 0 ampère
  bij de starttijd en herstelt deze na afloop.
trigger:
  - platform: state
    entity_id: binary_sensor.ourgrid_uitdaging_actief
    to: "on"
    id: available
  - platform: time
    at: sensor.ourgrid_uitdaging_start
    id: start
  - platform: time
    at: sensor.ourgrid_uitdaging_einde
    id: stop
condition: []
action:
  - choose:
      - conditions:
          - condition: trigger
            id: available
        sequence:
          - service: button.press
            target:
              entity_id: button.ourgrid_uitdaging_accepteren
      - conditions:
          - condition: trigger
            id: start
        sequence:
          - service: number.set_value
            target:
              entity_id: number.alfen_laadpaal_max_station_current
            data:
              value: 0
      - conditions:
          - condition: trigger
            id: stop
        sequence:
          - service: number.set_value
            target:
              entity_id: number.alfen_laadpaal_max_station_current
            data:
              value: 16
mode: single
```

### Met een Zendure SolarFlow thuisbatterij ontladen tijdens netcongestie

Accepteert automatisch een uitdaging en stuurt de Zendure SolarFlow 2400 AC batterij aan om het verbruik onder de vermogenslimiet van de uitdaging te houden. Elke minuut wordt het ontlaadvermogen herberekend op basis van de P1-meter. Is gebouwd op de [Gielz1986/Zendure-HA-zenSDK](https://github.com/Gielz1986/Zendure-HA-zenSDK) integratie.

```yaml
alias: OurGrid - Zendure SolarFlow ontladen tijdens uitdaging
description: >
  Accepteert automatisch een OurGrid-uitdaging en stuurt de Zendure SolarFlow
  batterij aan om het verbruik onder de vermogenslimiet te houden.
  Elke minuut wordt het ontlaadvermogen herberekend op basis van de P1-meter.
  Na de uitdaging schakelt de batterij terug naar "Nul op de meter".
trigger:
  - platform: state
    entity_id: binary_sensor.ourgrid_uitdaging_actief
    to: "on"
    id: available
  - platform: time
    at: sensor.ourgrid_uitdaging_start
    id: start
  - platform: time_pattern
    minutes: /1
    id: loop
  - platform: time
    at: sensor.ourgrid_uitdaging_einde
    id: stop
condition: []
action:
  - choose:
      - conditions:
          - condition: trigger
            id: available
        sequence:
          - service: button.press
            target:
              entity_id: button.ourgrid_uitdaging_accepteren
      - conditions:
          - condition: trigger
            id: start
        sequence:
          - service: input_select.select_option
            target:
              entity_id: input_select.zendure_2400_ac_modus_selecteren
            data:
              option: Handmatig
          - service: input_number.set_value
            target:
              entity_id: input_number.zendure_2400_ac_handmatig_vermogen
            data:
              value: >
                {% set p1 = states('sensor.p1_meter_power') | float(0) %}
                {% set limit = states('sensor.ourgrid_uitdaging_vermogenslimiet') | float(0) %}
                {% set target = limit - 100 %}
                {% set discharge = [p1 - target, 0] | max %}
                {% set capped = [discharge, 2400] | min | round(0) | int %}
                {{ capped * -1 }}
      - conditions:
          - condition: trigger
            id: loop
          - condition: template
            value_template: >
              {% set start = states('sensor.ourgrid_uitdaging_start') %}
              {% set end = states('sensor.ourgrid_uitdaging_einde') %}
              {% if start not in ['unknown', 'unavailable'] and end not in ['unknown', 'unavailable'] %}
                {% set now_ts = now().timestamp() %}
                {% set start_ts = as_timestamp(start) | float(0) %}
                {% set end_ts = as_timestamp(end) | float(0) %}
                {{ start_ts < now_ts < end_ts }}
              {% else %}
                false
              {% endif %}
        sequence:
          - service: input_number.set_value
            target:
              entity_id: input_number.zendure_2400_ac_handmatig_vermogen
            data:
              value: >
                {% set p1 = states('sensor.p1_meter_power') | float(0) %}
                {% set limit = states('sensor.ourgrid_uitdaging_vermogenslimiet') | float(0) %}
                {% set target = limit - 100 %}
                {% set discharge = [p1 - target, 0] | max %}
                {% set capped = [discharge, 2400] | min | round(0) | int %}
                {{ capped * -1 }}
      - conditions:
          - condition: trigger
            id: stop
        sequence:
          - service: input_number.set_value
            target:
              entity_id: input_number.zendure_2400_ac_handmatig_vermogen
            data:
              value: 0
          - service: input_select.select_option
            target:
              entity_id: input_select.zendure_2400_ac_modus_selecteren
            data:
              option: Nul op de meter
mode: single
max_exceeded: silent
```

## Problemen of vragen?

Maak een [issue aan op GitHub](https://github.com/dannyoosterveer/ourgrid/issues).
