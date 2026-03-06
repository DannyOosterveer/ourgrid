# OurGrid — Home Assistant Integratie

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/hacs/integration)
![GitHub release](https://img.shields.io/github/v/release/dannyoosterveer/ourgrid)

Met deze integratie koppel je [OurGrid](https://ourgrid.nl) aan Home Assistant. OurGrid is een Nederlandse dienst die beloningen uitkeert wanneer je jouw energieverbruik verlaagt tijdens piekmomenten op het elektriciteitsnet (netcongestie).

## Wat doet de integratie?

- Toont wanneer er een uitdaging actief is
- Laat je automatisch deelnemen aan uitdagingen via een button
- Toont de start- en eindtijd van de uitdaging
- Toont de vermogenslimiet en je actuele verbruik
- Toont je punten, wisselkoers en verwachte opbrengst
- Bevat blueprints om apparaten automatisch aan te sturen

![OurGrid apparaat in Home Assistant](https://github.com/dannyoosterveer/ourgrid/blob/main/custom_components/ourgrid/brand/icon.png?raw=true)

## Vereisten

- Een actief OurGrid-account
- De OurGrid app, met daarin je apparaatgegevens (te vinden onder Apparaten → Jouw huis automatisering)

## Installatie via HACS

1. Ga in Home Assistant naar **HACS → Integraties**
2. Klik op de **+** knop en zoek op `OurGrid`
3. Installeer de integratie en herstart Home Assistant

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

## Blueprints

De integratie bevat twee blueprints voor veelgebruikte automatiseringen:

### Laadpaal pauzeren tijdens uitdaging
Zet de laadstroom van je EV-lader naar 0 tijdens de uitdaging en herstelt hem daarna.

### Zendure SolarFlow ontladen tijdens uitdaging
Stuurt de Zendure SolarFlow 2400 AC batterij om het verbruik onder de uitdagingslimiet te houden, op basis van de P1-meter.

## Problemen of vragen?

Maak een [issue aan op GitHub](https://github.com/dannyoosterveer/ourgrid/issues).
