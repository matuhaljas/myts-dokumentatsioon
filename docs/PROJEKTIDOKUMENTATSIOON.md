# Projekti dokumentatsioon

> **Seis:** planeerimisjärgus. Riistvara on olemas, ühendused ja ehitussammud on paika pandud, kuid seadet pole veel kokku pandud ega testitud. Programmikood lisatakse hiljem.

## 1. Projekti eesmärk ja seadme lühikirjeldus

- Meie projekti eesmärk on luua ultraheliradar, mis pöörab kaugusandurit servo abil ja joonistab ümbruse kaardi arvutiekraanile.
- Seade näitab, mis suunas ja kui kaugel on anduri ees olevad esemed. Seda saab kasutada näiteks ruumi või laua ümbruse kaardistamiseks ja liikuvate esemete jälgimiseks.
- Iga mõõtmise kohta saadetakse arvutisse nurk ja kaugus ning neist tekib poolringikujuline radaripilt, kus esemed paistavad täppidena.
- Peamised komponendid: Arduino UNO R4 WiFi, TinkerKit sensorkilp, HC-SR04 ultraheli-kaugusandur, servo Hitec HS-322HD.

---

## 2. Sisendite loetelu

- Kaugus anduri ees oleva esemeni → HC-SR04 ultraheli-kaugusandur mõõdab 40 kHz helipiiksu kaja aega (mõõteulatus umbes 2–400 cm).
- Anduri suund → eraldi andurit ei ole; nurk on teada sellest, kuhu programm servo parajasti keeras.

---

## 3. Väljundite loetelu

- Andur pöördub vasakule / paremale → servo Hitec HS-322HD.
- Mõõtetulemus liigub arvutisse → USB jadaport, iga mõõtmise kohta rida kujul `nurk,kaugus_cm`.
- Ekraanile kuvatakse radaripilt → arvuti brauser (Chrome või Edge), mis loeb jadaporti ja joonistab punktid.

---

## 4. Nõuded loodavale seadmele

Reeglid kirjeldavad kavandatud käitumist ja täpsustuvad testimise käigus.

- Kui seade saab toite, siis hakkab servo andurit pöörama vahemikus 15°–165° sammuga 2°.
- Kui servo on jõudnud uude asendisse, siis mõõdab andur kauguse ja Arduino saadab arvutisse rea `nurk,kaugus_cm`.
- Kui kaja ei tule 25 ms jooksul tagasi (ese on kaugemal kui umbes 4 m või ei peegelda heli), siis saadetakse kauguseks 0 ja radaripildile punkti ei joonistata.
- Kui servo jõuab vahemiku piirini (15° või 165°), siis muutub pöörlemissuund vastupidiseks.
- Kui arvuti saab uue mõõtmise, siis joonistatakse radaripildile punkt vastava nurga ja kauguse kohale ning pühkimisjoon liigub samale nurgale.
- Kui ese on kaugemal kui radaripildi ulatus (200 cm), siis punkti ei kuvata.
- Kui punkti pole 6 sekundi jooksul uuendatud, siis see kustub.
- Kui ühendus Arduinoga katkeb, siis kuvab radarivaade vastava teate.

---

## 5. Süsteemi füüsiliste komponentide loetelu

| Komponent | Märkus |
|---|---|
| Arduino UNO R4 WiFi (ühilduv kloon, USB-C) | mikrokontroller, juhib andurit ja servot |
| TinkerKit sensorkilp | toob viigud 3-viiguliste pesadena välja |
| HC-SR04 ultraheli-kaugusandur | mõõteulatus umbes 2–400 cm |
| Servo Hitec HS-322HD | pöörab andurit |
| Juhtmed | 4 tk andurile |
| USB-C andmekaabel | toide ja andmeside arvutiga |
| Teip, kuumliim või kummipael | anduri kinnitamiseks servo hoovale |
| Arvuti (Arduino IDE, Chrome või Edge) | koodi laadimine ja radarivaade |

Varuks: 4×AA patareihoidik servo eraldi toiteks, kui USB toitest ei piisa.

Täpsem loetelu on failis [`hardware/komponentide-loetelu.md`](../hardware/komponentide-loetelu.md).

---

## 6. Ühendusskeem

Skeemi pilt (`hardware/wiring-diagram.png`) on veel tegemata. Ühendused tekstina:

Kõik juhtmed lähevad sensorkilbi mustadesse läbivatesse pesadesse, mitte 3-viigulistesse TinkerKiti pesadesse.

| Osa | Juhe | Arduino viik (must pesa) |
|---|---|---|
| Servo signaal | kollane / oranž | D6 |
| Servo toide | punane | 5V |
| Servo maandus | must / pruun | GND |
| HC-SR04 Trig | | D9 |
| HC-SR04 Echo | | D10 |
| HC-SR04 VCC | | 5V |
| HC-SR04 GND | | GND |

- Toide tuleb USB kaudu arvutist. GND on kõigil ühine.
- Sensorkilbi oranžid pesad on väljundid O0–O5 (O0 = D11, O1 = D10, O2 = D9, O3 = D6, O4 = D5, O5 = D3), valged sisendid I0–I5 (A0–A5). Me neid ei kasuta.

**Miks mitte TinkerKiti pesad:** TinkerKiti 3-viigulise pesa viikude järjekord ei sobi tavalise servo pistikuga. Testis põrises servo pesas O3, aga ei pöördunud. Otse D6, 5V ja GND külge ühendatuna töötas servo kohe.

**Servo toide:** HS-322HD võtab liikudes paarsada mA ja kinni jäädes kuni umbes 0,8 A. Kui plaat USB toitel taaskäivitub või servo tõmbleb, tuleb servole anda eraldi toide patareidest (4×AA) ja ühendada patareide miinus Arduino GND-ga.

---

## 7. Süsteemi juhtiv kood (või pseudokood)

Kood pole veel reposse lisatud. Kavandatud loogika pseudokoodina:

```
seadistus:
    ava jadaport kiirusel 115200
    määra Trig väljundiks ja Echo sisendiks
    ühenda servo viiguga D6

mõõda_kaugus:
    saada Trig viigule 10 mikrosekundi pikkune impulss
    mõõda, kui kaua on Echo viik kõrge (kuni 25 ms)
    kaugus_cm = kestus / 58
    kui kaja ei tulnud, siis kaugus_cm = 0

skaneeri(nurk):
    keera servo nurga alla
    oota 40 ms (servo jõuab kohale, eelmine kaja sumbub)
    saada jadaporti "nurk,kaugus_cm"

põhitsükkel:
    iga nurga kohta 15°-st 165°-ni sammuga 2°: skaneeri(nurk)
    iga nurga kohta 165°-st 15°-ni sammuga 2°: skaneeri(nurk)
```

Arvutipoolne radarivaade:

```
loe jadapordist ridu kujul "nurk,kaugus_cm"
jäta meelde iga nurga viimane kaugus ja mõõtmise aeg
joonista pidevalt:
    poolringikujuline võrgustik (kaared iga 50 cm järel, kiired iga 30° järel)
    punkt iga nurga kohta, mille kaugus on vahemikus 1–200 cm
    punkt muutub läbipaistvamaks ja kustub 6 sekundiga
    pühkimisjoon viimati mõõdetud nurga suunas
```

Heli läbib 1 cm edasi-tagasi umbes 58 mikrosekundiga, sellest tuleb kauguse arvutamise jagaja.

---

## 8. Ehitussammud

1. Paigalda Arduino IDE ja lisa Boards Manageris "Arduino UNO R4 Boards". Vali plaadiks "Arduino UNO R4 WiFi".
2. Pane sensorkilp Arduino peale.
3. Ühenda andur ja servo tabeli järgi mustadesse läbivatesse pesadesse (USB lahti).
4. Laadi kood plaadile. Servo peab hakkama edasi-tagasi pühkima.
5. Ava Serial Monitor kiirusel 115200. Read `nurk,kaugus` peavad muutuma, kui käsi anduri ette panna.
6. Sulge Serial Monitor, muidu jääb port hõivatuks.
7. Kinnita andur servo hoovale nii, et saatja ja vastuvõtja vaatavad horisontaalselt ette. Kinnita servo alusele.
8. Ava radarivaade brauseris ja ühenda Arduino pordiga.
9. Testi kõva sileda esemega 30–100 cm kaugusel.

Hinnanguline ehitusaeg on 2–3 tundi.

---

## 9. Piirangud

- **Ainult otsenähtavus.** Ultraheli ei läbi seinu ega muid takistusi.
- **Lai vihk (umbes 15°).** Peenike ese paistab pildil laia kaarena.
- **Pehmed ja viltused pinnad** (riie, kardin, nurga all sein) peegeldavad halvasti ja võivad jääda nägemata.
- **Aeglane.** Üks täispühkimine võtab mõne sekundi.

---

## 10. Veaotsing

| Sümptom | Tõenäoline põhjus |
|---|---|
| Kaugus on alati 0 | Trig ja Echo on vahetuses või anduri toide puudub |
| Servo tõmbleb või plaat taaskäivitub | servo vajab eraldi toidet |
| Radarivaade ei leia porti | Serial Monitor on lahti või brauser pole Chrome/Edge |
| Pilt on peegelpildis | andur on servol tagurpidi |
| Täpid hüplevad | pind peegeldab heli halvasti |
| Arvuti ei näe plaati | USB-C kaabel on ainult laadimiseks |
| Servo põriseb, aga ei pöördu | servo on TinkerKiti pesas, viikude järjekord ei sobi; ühenda otse D6, 5V ja GND külge |
| Serial Monitoris on ainult `?` märgid | Serial Monitori kiirus pole 115200 |

---

## 11. Kaalutud ja kõrvale jäetud variandid

- **Läbi seina nägev radar.** Olemasolevate osadega pole võimalik: ultraheli ja infrapuna seina ei läbi. WiFi-signaali kõikumise järgi saaks tuvastada ainult seda, et keegi seina taga liigub, ilma kauguse ja suunata. Päris radariks oleks vaja eraldi moodulit (nt HLK-LD2410), mis läbib vaid õhukest seina.
- **Pilt 2,8" TFT-ekraanil.** Jäi välja kahel põhjusel: Elegoo TFT teegid ja MCUFRIEND_kbv ei toeta UNO R4 WiFi-t ning sensorkilbi püstised pistikud ei mahu ekraanikilbi alla. UNO R3-ga oleks see teostatav (TFT kasutab viike D2–D9 ja A0–A4, radarile jääksid D10, D11 ja A5).

---

## 12. Tegemata

- [x] Sensorkilbi pesade viigujärjekorra kontroll (ei sobi servoga, kasutame musti pesi)
- [ ] Seadme kokkupanek
- [ ] Koodi kompileerimine ja testimine riistvaraga
- [ ] Servo toite katsetamine USB pealt
- [ ] Anduri kinnitus ja korpus
- [ ] Ühendusskeemi pilt `hardware/wiring-diagram.png`
- [ ] Programmikoodi lisamine kataloogi `src/`
- [ ] Pildid ja videod kataloogi `media/`
