.. _admin_accounts:

Accounts
========

Onder het menu-item "Accounts" en op het dashboard onder het kopje "Accounts" wordt toegang geboden tot het beheer van:

* Gebruikers
* Groepen
* TOTP devices
* Webauthn devices

Door hierop te klikken wordt het desbetreffende beheerscherm geopend.

Gebruikers
----------

.. tip:: Als je van Single Sign On (SSO) met OpenID Connect gebruik maakt, dan worden
   de gebruikersaccounts automatisch beheerd.

Beheerscherm
~~~~~~~~~~~~

In het beheerscherm van de gebruikers zie je een lijst van personen die toegang hebben
tot de publicatiebank. Deze lijst toont *alle* gebruikers, ongeacht of je een lokale
gebruikersaccount hebt, of via een organisatie-account inlogt.

Op dit scherm zijn een aantal acties mogelijk:

* Rechtsboven op het beheerscherm zit een knop **Gebruiker toevoegen** waarmee je een
  nieuwe lokale gebruikersaccount kan aanmaken.
* Bovenaan staat een zoekveld, waar je gebruikers op gebruikersnaam, voornaam, achternaam
  en email kan vinden.
* Er is een bulk-actie om gebruikers te verwijderen, maar het is beter om accounts te
  deactiveren in plaats van verwijderen zodat audit-informatie gekoppeld blijft.
* Rechts kan je filteren op een aantal eigenschappen:

    - Stafstatus ja/nee: enkel gebruikers met stafstatus kunnen op de beheeromgeving
      inloggen.
    - Supergebruikerstatus ja/nee: supergebruikers hebben altijd alle rechten om alle
      acties uit te voeren.
    - Actief ja/nee: inactieve gebruikers kunnen niet inloggen.
    - Groepen: een gebruiker kan lid zijn van één of meerdere groepen waaraan bepaalde
      rechten gekoppeld zijn.

* De "Overnemen" knop laat (super)gebruikers toe zich voor te doen als de geselecteerde
  gebruiker. Dit is handig om de rechten te controleren of een probleem te reproduceren.

**Gebruiker bewerken**

Wanneer je de gebruikersnaam van een gebruiker aanklikt, dan opent een scherm met
nadere details. Hier zie je:

* **Alle gegevens**. Deze lichten we hieronder toe.
* Rechtsboven een knop **Geschiedenis**. Deze toont de beheer-handelingen die vanuit de
  beheerinterface zijn uitgevoerd op de *gebruiker*.
* Linksonder de mogelijkheid om de wijzigingen op te slaan.
* Rechtsonder de mogelijkheid om de gebruiker te **verwijderen**.

Bij een gebruiker zijn de volgende gegevens beschikbaar. Op het scherm worden verplichte
velden **dikgedrukt** weergegeven.

* ``Gebruikersnaam``. De gebruikersnaam waarmee de gebruiker inlogt. Voor inloggen met
  organisatie-account is dit veelal een technische systeemwaarde.
* ``Wachtwoord``. Gemaskeerde informatie over het gehashte wachtwoord. De wachtwoorden
  zelf zijn nooit te achterhalen.
* ``Persoonlijke gegevens``. Naam en e-mail van de gebruiker.
* ``Actief``. Vlag die aangeeft of de gebruiker kan inloggen.
* ``Stafstatus``. Vlag die aangeeft of de gebruiker kan inloggen op de beheeromgeving.
* ``Supergebruikerstatus``. Vlag die aangeeft of de gebruiker altijd alle rechten heeft.
* ``Groepen``. Je kan gebruikers aan groepen toewijzen zodat ze de rechten van die groep
  krijgen. Dit is aangeraden.
* ``Gebruikersrechten``. Je kan individuele rechten aan gebruikers toekennen, naast of
  in plaats van groepsrechten.

.. warning:: Van supergebruikers wordt verwacht dat ze goed weten wat ze doen, dus ken
   deze rechten alleen toe als het echt noodzakelijk is. Over het algemeen kan je beter
   een gebruiker aan een groep toewijzen.

Groepen
-------

Groepen bestaan om gebruikersrechten te organiseren.

.. tip:: Als je van Single Sign On (SSO) met OpenID Connect gebruik maakt, dan worden
   sommige groepen automatisch aangemaakt en toegekend aan gebruikers, afhankelijk van
   de OpenID Connect-instellingen.

Beheerscherm
~~~~~~~~~~~~

In het beheerscherm van de groepen zie je een lijst van groepen die bestaan in het
systeem.

.. note:: Een aantal groepen zijn "vastgezet" in de applicatie en wijzigingen aan deze
   groepen worden teruggedraaid bij updates:

   * Technisch beheer
   * Functioneel beheer

Op dit scherm zijn een aantal acties mogelijk:

* Rechtsboven op het beheerscherm zit een knop **Groep toevoegen** waarmee je een
  nieuwe groep kan aanmaken.
* Bovenaan staat een zoekveld, waar je groepen op naam doorzoekt.
* Er is een bulk-actie om groepen te verwijderen.

**Groep bewerken**

Wanneer je de naam van een groep aanklikt, dan opent een scherm met nadere details. Hier
zie je:

* **Alle gegevens**. Deze lichten we hieronder toe.
* Rechtsboven een knop **Geschiedenis**. Deze toont de beheer-handelingen die vanuit de
  beheerinterface zijn uitgevoerd op de *groep*.
* Linksonder de mogelijkheid om de wijzigingen op te slaan.
* Rechtsonder de mogelijkheid om de groep te **verwijderen**.

Bij een groep zijn de volgende gegevens beschikbaar. Op het scherm worden verplichte
velden **dikgedrukt** weergegeven.

* ``Naam``. Een unieke naam waaraan je de groep herkent, en waarmee inloggen met
  organisatie-account koppelt voor de groepensynchronisatie.
* ``Rechten``. De mogelijke rechten op objecten die in de beheeromgeving zichtbaar zijn,
  typisch onderverdeeld in *toevoegen*, *wijzigen*, *verwijderen* en *inzien*.

TOTP devices
------------

.. warning:: Dit onderdeel behoort tot de geavanceerde/technische functies. Maak hier
   enkel wijzingen als je weet wat je doet.

TOTP-devices zijn een onderdeel van de functionaliteiten voor
multi-factor-authenticatie (MFA). Het bevat de technische gegevens voor gebruikers om
een éénmalige code te kunnen generen bij het inloggen met lokale gebruikersaccounts.

We documenteren deze functionaliteit verder niet.

Webauthn devices
----------------

.. warning:: Dit onderdeel behoort tot de geavanceerde/technische functies. Maak hier
   enkel wijzingen als je weet wat je doet.

Webauthn devices zijn een onderdeel van de functionaliteiten voor
multi-factor-authenticatie (MFA). Het bevat de technische gegevens voor gebruikers om
bij het inloggen met lokale gebruikersaccounts een hardware token te gebruiken in plaats
van een éénmalige code.

We documenteren deze functionaliteit verder niet.
