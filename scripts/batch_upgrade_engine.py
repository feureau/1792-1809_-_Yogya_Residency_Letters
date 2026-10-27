import os
import re
import json
import glob

def load_index():
    with open('39_Expanded_Keyword_Index.md', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    with open('scripts/entity_database.json', 'r', encoding='utf-8') as f:
        entities = json.load(f)
    return lines, entities

with open('data.json', 'r', encoding='utf-8') as f:
    DATA_LIST = json.load(f)

# Master entity citations dictionary
PEOPLE_MAP = {
    'Hamengkubuwana I': ('Sultan Mangkubumi (Hamengkubuwana I)', 'HB I', 11, 'Javanese Royalty and Princely Families', 'First Sultan of Yogyakarta (reigned 1749–1792), founder of the sultanate.'),
    'Hamengkubuwana II': ('Sultan Hamengkubuwana II (Sultan Sepuh)', 'HB II / Sultan', 12, 'Javanese Royalty and Princely Families', 'Second Sultan of Yogyakarta (reigned 1792–1810, 1811–1812, 1826–1828), primary sovereign in the residency letters.'),
    'Hamengkubuwana III': ('Sultan Hamengkubuwana III (Pangéran Adipati Anom / Crown Prince)', 'HB III / CP', 13, 'Javanese Royalty and Princely Families', 'Third Sultan of Yogyakarta (reigned 1812–1814), recognized as Crown Prince on 20 Aug 1792.'),
    'Hamengkubuwana IV': ('Sultan Hamengkubuwana IV (Jarot)', 'HB IV', 14, 'Javanese Royalty and Princely Families', 'Fourth Sultan of Yogyakarta (reigned 1814–1822).'),
    'Hamengkubuwana V': ('Sultan Hamengkubuwana V', 'HB V', 15, 'Javanese Royalty and Princely Families', 'Fifth Sultan of Yogyakarta (reigned 1822–1826, 1828–1855).'),
    'Pakubuwana III': ('Sunan Pakubuwana III', 'PB III', 10, 'Javanese Royalty and Princely Families', 'Sunan of Surakarta (reigned 1749–1788), signatory to the Treaty of Giyanti (1755) and Book of Klèpu (1770).'),
    'Pakubuwana IV': ('Sunan Pakubuwana IV (Sunan Bagus)', 'PB IV / Sunan', 18, 'Javanese Royalty and Princely Families', 'Sunan of Surakarta (reigned 1788–1820), prominent rival to HB II.'),
    'Pakubuwana V': ('Sunan Pakubuwana V', 'PB V', 19, 'Javanese Royalty and Princely Families', 'Sunan of Surakarta (reigned 1820–1823).'),
    'Pakubuwana VI': ('Sunan Pakubuwana VI (Radèn Mas Saperdan)', 'PB VI', 20, 'Javanese Royalty and Princely Families', 'Sunan of Surakarta (reigned 1823–1830), exiled to Ambon in 1830.'),
    'Mangkunagara I': ('Radèn Mas Said (Mangkunagara I / Prince Mangkunegara)', 'MN I', 26, 'Javanese Royalty and Princely Families', 'Legendary founder of the Mangkunagaran Principality (reigned 1757–1795).'),
    'Mangkunagara II': ('Pangéran Prangwedana (Mangkunagara II)', 'MN II / PWD', 27, 'Javanese Royalty and Princely Families', 'Ruler of the Mangkunagaran (reigned 1796–1835), creator of the Mangkunagaran Legion.'),
    'Dipanagara': ('Pangéran Dipanagara (Diponegoro)', 'DP', 10, 'Javanese Royalty and Princely Families', 'Central figure of the Java War (1825–1830), eldest son of HB III.'),
    'Mangkubumi': ('Pangéran Mangkubumi', 'MB / Mangkoeboemie', 63, 'Javanese Royalty and Princely Families', 'Son of HB I, uncle of Dipanagara, key advisor during the 1825 court crisis.'),
    'Danureja I': ('Radèn Adipati Danureja I', 'Patih Danureja I', 183, 'Javanese Officials, Commanders, and Local Leaders', 'First Patih (Grand Vizier) of Yogyakarta (in office 1755–1799).'),
    'Danureja II': ('Radèn Adipati Danureja II', 'Patih Danureja II / Danurejo', 183, 'Javanese Officials, Commanders, and Local Leaders', 'Patih of Yogyakarta (in office 1799–1811; earlier R.T. Rèksanagara).'),
    'Danureja IV': ('Radèn Adipati Danureja IV (Sumadipura)', 'PATIH / Danurejo', 184, 'Javanese Officials, Commanders, and Local Leaders', 'Pro-Dutch Patih of Yogyakarta (in office 1813–1847).'),
    'Rongga III': ('Radèn Rongga Prawiradirja III', 'Raden Rongga', 178, 'Javanese Officials, Commanders, and Local Leaders', 'Bupati Wedana of Madiun (1796–1810) and brother-in-law to HB II.'),
    'Natakusuma': ('Pangéran Natakusuma (Pakualam I)', 'PA / PA I', 23, 'Javanese Royalty and Princely Families', 'Son of HB I, created first independent ruler of the Pakualaman (reigned 1812–1829).'),
    'Ratu Ageng': ('Ratu Ageng Tegalreja', 'Ratu Ageng', 29, 'Javanese Royalty and Princely Families', 'Widow of HB I who raised Dipanagara at Tegalreja.'),
    'Ratu Kedhaton': ('Ratu Kedhaton (Ratu Ageng)', 'Ratu Kedhaton', 30, 'Javanese Royalty and Princely Families', 'Official wife of HB II, mother of HB III, died July 1820.'),
    'Ratu Kencana Wulan': ('Ratu Kencana Wulan (Ratu Wétan)', 'Ratu Kencana Wulan', 31, 'Javanese Royalty and Princely Families', 'Influential favorite consort of HB II.'),
    'Sekartaji': ('Radèn Ayu Sekartaji', 'Sekartaji', 18, 'Javanese Royalty and Princely Families', 'Sister of Sunan PB IV, married to the second son of the Panembahan of Sumenep in 1796.'),
    'Waterloo': ('Matthijs Waterloo', 'Wat / Res', 330, 'Residents of Yogyakarta', 'Dutch Resident of Yogyakarta (1803–1808) who maintained extensive correspondence with Engelhard.'),
    'Nicolaus Engelhard': ('Nicolaus Engelhard', 'Eng / Gov', 301, 'Governors and Directors of Java\'s Northeast Coast', 'Governor of Java\'s Northeast Coast at Semarang (1801–1808).'),
    'Pieter Engelhard': ('Pieter Engelhard', 'P. Engelhard', 331, 'Residents of Yogyakarta', 'Resident of Yogyakarta (1808, 1810–1811) during the Daendels administration.'),
    'Van den Berg': ('Johannes Gerardus van den Berg', 'V.d.B. / vdBerg', 329, 'Residents of Yogyakarta', 'Resident of Yogyakarta (1798–1803), authored the 1803 Memorie van Overgave.'),
    'Van Overstraten': ('Pieter Gerardus van Overstraten', 'Van Overstraten', 279, 'Governors-General', 'Governor of Java\'s Northeast Coast (1791–1796) and Governor-General (1796–1801).'),
    'Van IJsseldijk': ('Wouter Hendrik van IJsseldijk', 'Van IJsseldijck', 327, 'Residents of Yogyakarta', 'Resident of Yogyakarta (1786–1798), author of the 1798 Memorie van Overgave.'),
    'Rothenbühler': ('Frederik Jacob Rothenbühler', 'Rothenbuhler', 328, 'Residents of Yogyakarta', 'Resident of Yogyakarta (1799) and scholar of Javanese administration.'),
    'Daendels': ('Marshal Herman Willem Daendels', 'Daendels / G.G.', 282, 'Governors-General', 'Franco-Dutch Governor-General of the East Indies (1808–1811).'),
    'Raffles': ('Thomas Stamford Raffles', 'Raffles', 284, 'Lieutenant-Governors of Java', 'British Lieutenant-Governor of Java (1811–1816).'),
    'Crawfurd': ('John Crawfurd', 'Crawfurd', 333, 'Residents of Yogyakarta', 'British Resident of Yogyakarta (1811–1814, 1816) and compiler of archival manuscripts.'),
    'De Kock': ('Hendrik Merkus de Kock', 'de Kock', 289, 'Governors-General & Military Commanders', 'Lieutenant Governor-General and Dutch supreme commander during the Java War.'),
    'Wiese': ('Albert Henricus Wiese', 'Wiese', 281, 'Governors-General', 'Governor-General of the Dutch East Indies (1805–1808).'),
    'Siberg': ('Johannes Siberg', 'Siberg', 280, 'Governors-General', 'Governor-General of the Dutch East Indies (1801–1805).'),
    'Alting': ('Willem Arnold Alting', 'Alting', 278, 'Governors-General', 'Governor-General of the Dutch East Indies (1780–1796).'),
    'Smissaert': ('Anthonië Hendrik Smissaert', 'Smissaert / Res', 345, 'Residents of Yogyakarta', 'Dutch Resident of Yogyakarta (1823–1825).'),
    'Chevallier': ('Petrus Franciscus Henricus Chevallier', 'Chevallier / ASST RES', 346, 'Colonial Officials', 'Assistant Resident of Yogyakarta (1823–1825), author of the 1825 diary registers.'),
    'MacGillavry': ('Hendrik Mauritz MacGillavry', 'Macgillavry', 346, 'Residents of Yogyakarta', 'Acting Resident of Yogyakarta (1825).'),
    'Nahuys': ('Huibert Gerard Nahuys van Burgst', 'Nahuys', 341, 'Residents of Yogyakarta', 'Resident of Yogyakarta (1816–1822).'),
    'Moorrees': ('Johannes Wilhelmus Moorrees', 'Moorrees / Morris', 301, 'Colonial Officials', 'Colonial minister and acting resident for Solo and Yogya affairs under Daendels.'),
    'Driessen': ('Bartholomeus Jacobus Driessen', 'Willem Driessen', 282, 'Colonial Officials', 'Commandant of Fort Rustenburg in Yogyakarta.'),
    'Carey': ('Prof. Peter Carey', 'Carey', 1, 'Modern Historians', 'Modern British historian and biographer of Pangéran Dipanagara; compiler of these archival research dossiers.')
}

PLACES_MAP = {
    'Yogyakarta': ('Yogyakarta (Mataram / Djogja)', 'Yogya / Djogja', 405, 'Places', 'Capital and core appanage realm of the Sultanate of Yogyakarta.'),
    'Surakarta': ('Surakarta (Solo / Sala)', 'Solo / Sala', 461, 'Places', 'Court city and realm of the Sunanate of Surakarta.'),
    'Kraton': ('Kraton Yogyakarta', 'Kraton', 518, 'Cultural Concepts', 'The fortified royal palace and court of the Sultan of Yogyakarta.'),
    'Tegalreja': ('Tegalreja (Tegalrejo)', 'TR', 462, 'Places', 'Country estate of Pangéran Dipanagara northwest of Yogyakarta.'),
    'Pajang': ('Pajang', 'Pajang', 434, 'Places', 'Central agrarian province partitioned between Yogyakarta and Surakarta.'),
    'Gunung Kidul': ('Gunung Kidul', 'Gunung Kidul', 462, 'Places', 'Rugged southern karst province of Yogyakarta.'),
    'Kedu': ('Kedu (Këdhu)', 'Këdhu / Kedu', 468, 'Places', 'Rich central agricultural province contested between the courts and colonial government.'),
    'Bagelen': ('Bagelen (Bagelèn)', 'Bagelèn / Bagelen', 415, 'Places', 'Western nagara agung province of Central Java.'),
    'Banyumas': ('Banyumas', 'Banyumas', 419, 'Places', 'Western mancanagara province bordering the Sundanese lands.'),
    'Madiun': ('Madiun', 'Madiun', 401, 'Places', 'Capital of the Eastern Mancanagara and domain of Radèn Rongga III.'),
    'Boyolali': ('Boyolali', 'Boyolali', 468, 'Places', 'Strategic tollgate and garrison town on the highway between Surakarta and the North Coast.'),
    'Klaten': ('Klaten (Klathèn)', 'Klattèn / Klaten', 423, 'Places', 'Border garrison town and fortress site between Yogyakarta and Surakarta.'),
    'Magelang': ('Magelang', 'Magelang', 411, 'Places', 'Capital of the Kedu residency and military headquarters.'),
    'Semarang': ('Semarang', 'Semarang', 299, 'Places', 'Capital of Java\'s Northeast Coast government and headquarters of the Governor.'),
    'Batavia': ('Batavia (Jakarta)', 'Batavia', 277, 'Places', 'Capital of the Netherlands East Indies and seat of the Governor-General.'),
    'Surabaya': ('Surabaya', 'Surabaya', 458, 'Places', 'Major coastal port and naval center in East Java.'),
    'Sumenep': ('Sumenep (Madura)', 'Sumenep', 458, 'Places', 'Principality on eastern Madura allied with the colonial government.'),
    'Kalasan': ('Kalasan (Kalassan)', 'Kalasan', 468, 'Places', 'Royal staging post and tollgate site east of Yogyakarta.'),
    'Fort Rustenburg': ('Fort Rustenburg (Fort Vredeburg)', 'Fort Rustenburg', 631, 'Military Forts', 'Dutch fortress situated directly opposite the Kraton Yogyakarta.'),
    'Alun-alun': ('Alun-alun (Northern)', 'Alun-alun', 479, 'Cultural Concepts', 'The expansive royal parade ground fronting the Kraton.')
}

TERMS_MAP = {
    'Cacah': ('Cacah', 'Cacahs', 489, 'Peasant household tax-revenue unit used for land and population measurement (approx. 5 persons).'),
    'Jung': ('Jung', 'Jung / Jungs', 504, 'Javanese unit of agrarian land measurement (approx. 4 bau or 2.8 hectares).'),
    'Bau': ('Bau', 'Bau', 504, 'Agrarian land metric equivalent to one-fourth of a jung.'),
    'Bèkèl': ('Bèkèl (Bekel)', 'Bekil / Bèkèl', 485, 'Village-level tax collector and headman managing apanages for court nobility.'),
    'Bupati': ('Bupati', 'Bupati / Regents', 488, 'High regional administrative official or regent of a province.'),
    'Patih': ('Patih (Grand Vizier)', 'Patih / Kepatihan', 516, 'Chief Minister of the realm responsible for royal administration and diplomacy.'),
    'Mancanagara': ('Mancanagara', 'MN / E. MN / W. MN', 525, 'The outer provinces of Central Java divided between Yogyakarta and Surakarta.'),
    'Vorstenlanden': ('Vorstenlanden', 'VL / Vorstenlanden', 468, 'The Principalities of Central Java (Yogyakarta and Surakarta).'),
    'Kraton': ('Kraton', 'Kraton', 518, 'Fortified palace complex and seat of royal power.'),
    'Dalem': ('Dalem', 'Dalem', 490, 'Princely residence or compound of a senior royal or minister.'),
    'Garebeg': ('Garebeg', 'Garebeg / Poasa', 497, 'Major tri-annual Islamic-Javanese court festivals celebrating religious feast days.'),
    'Book of Klèpu': ('Book of Klèpu (1770 / 1773)', 'Book of Klepu', 489, 'Official inter-court cadastral boundary and cacah allocation treaty settling post-Giyanti land disputes.'),
    'Memorie van Overgave': ('Memorie van Overgave (MvO)', 'MvO / Memorie', 279, 'Official administrative handover memorandum submitted by outgoing Dutch governors and residents.'),
    'Treaty of Giyanti': ('Treaty of Giyanti (1755)', 'Giyanti', 11, 'Foundational peace treaty partitioning the Mataram Empire into the Yogyakarta and Surakarta realms.'),
    'Prajurit': ('Prajurit', 'Prajurit', 631, 'Royal guards and military regiments of the Central Javanese courts.'),
    'Kadipatèn': ('Kadipatèn', 'Kadipaten', 506, 'Official palace compound and administration of the Crown Prince.')
}

def expand_shorthand(text):
    # Expands common shorthand in text while preserving readability
    replacements = [
        (r'\bDP\b', 'DP [Pangéran Dipanagara]'),
        (r'\bHB II\b', 'HB II [Sultan Hamengkubuwana II]'),
        (r'\bHB I\b', 'HB I [Sultan Hamengkubuwana I]'),
        (r'\bHB III\b', 'HB III [Sultan Hamengkubuwana III]'),
        (r'\bHB IV\b', 'HB IV [Sultan Hamengkubuwana IV]'),
        (r'\bHB V\b', 'HB V [Sultan Hamengkubuwana V]'),
        (r'\bPB IV\b', 'PB IV [Sunan Pakubuwana IV]'),
        (r'\bPB III\b', 'PB III [Sunan Pakubuwana III]'),
        (r'\bMN I\b', 'MN I [Mangkunagara I]'),
        (r'\bMN II\b', 'MN II [Mangkunagara II]'),
        (r'\bPWD\b', 'PWD [Prangwedana / Mangkunagara II]'),
        (r'\bCP\b', 'CP [Crown Prince / later HB III]'),
        (r'\bTR\b', 'TR [Tegalrejo]'),
        (r'\bVL\b', 'VL [Vorstenlanden]'),
        (r'\bw/\b', 'w/ [with]'),
        (r'\bv\.\b', 'v. [against]'),
        (r'\bG\.G\.\b', 'G.G. [Governor-General]'),
        (r'\bRes\.\b', 'Res. [Resident]'),
        (r'\bAsst\. Res\.\b', 'Asst. Res. [Assistant Resident]'),
        (r'\bSp\. D\.\b', 'Sp. D. [Spanish Dollars]')
    ]
    for pattern, rep in replacements:
        # replace first occurrence per paragraph
        text = re.sub(pattern, rep, text, count=1)
    return text

print("Initialized batch upgrade engine.")
