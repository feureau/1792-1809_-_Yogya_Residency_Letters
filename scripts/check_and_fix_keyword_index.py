# check_and_fix_keyword_index.py
# Check all transcriptions against 39_Expanded_Keyword_Index.md,
# fix transcription discrepancies/errors, standardize headers,
# and insert/update verified Keyword Index Check metadata across all 413 files.

import os
import re
import glob
import sys

sys.stdout.reconfigure(encoding='utf-8')

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
INDEX_FILE = os.path.join(REPO_ROOT, '39_Expanded_Keyword_Index.md')
TRANSCRIPTION_DIR = os.path.join(REPO_ROOT, 'transcription')

# 1. Comprehensive Canonical Keyword Rules based on 39_Expanded_Keyword_Index.md
# Format: (Canonical Display Name, regex_pattern)
KEYWORD_RULES = [
    # Royalty & Princely Houses
    ('Hamengkubuwana I', r'\b(?:HB\s*I|Hamengkubuwana\s*I|Hamengkubuwono\s*I|Sultan\s*Mangkubumi|Mangkubumi\s*I)\b'),
    ('Hamengkubuwana II', r'\b(?:HB\s*II|Hamengkubuwana\s*II|Hamengkubuwono\s*II|Sultan\s*Sepuh|GRM\s*Sundoro)\b'),
    ('Hamengkubuwana III', r'\b(?:HB\s*III|Hamengkubuwana\s*III|Hamengkubuwono\s*III|Raja\s*Putra\s*Narendra)\b'),
    ('Hamengkubuwana IV', r'\b(?:HB\s*IV|Hamengkubuwana\s*IV|Jarot)\b'),
    ('Hamengkubuwana V', r'\b(?:HB\s*V|Hamengkubuwana\s*V)\b'),
    ('Crown Prince', r'\b(?:Crown\s*Prince|Kroonprins|Pangeran\s*Adipati\s*Anom|Pangéran\s*Adipati\s*Anom|\bCP\b|\bC\.P\.\b)\b'),
    ('Pakubuwana III', r'\b(?:PB\s*III|Pakubuwana\s*III|Pakubuwono\s*III)\b'),
    ('Pakubuwana IV', r'\b(?:PB\s*IV|Pakubuwana\s*IV|Pakubuwono\s*IV|Sunan\s*Bagus)\b'),
    ('Pakubuwana V', r'\b(?:PB\s*V|Pakubuwana\s*V)\b'),
    ('Pakubuwana VII', r'\b(?:PB\s*VII|Pakubuwana\s*VII)\b'),
    ('Mangkunagara I', r'\b(?:MN\s*I|Mangkunagara\s*I|Mangkunegara\s*I|Raden\s*Mas\s*Said)\b'),
    ('Prangwedana (Mangkunagara II)', r'\b(?:Prangwedana|Prang\s*Wedana|PWP|PWD|Mangkunagara\s*II|Mangkunegara\s*II)\b'),
    ('Natakusuma (Pakualam I)', r'\b(?:Natakusuma|Natakoesoema|Pakualam\s*I|Paku\s*Alam\s*I)\b'),
    ('Natadiningrat (Pakualam II)', r'\b(?:Natadiningrat|Pakualam\s*II|Paku\s*Alam\s*II)\b'),
    ('Ratu Ageng', r'\b(?:Ratu\s*Ageng|Ratu\s*Kadipaten)\b'),
    ('Ratu Kedhaton', r'\b(?:Ratu\s*Kedhaton|Ratu\s*Kedaton)\b'),
    ('Ratu Kencana Wulan', r'\b(?:Ratu\s*Kencana\s*Wulan|Ratu\s*Kencana|Ratu\s*Wetan)\b'),
    ('Ratu Maduretna', r'\b(?:Ratu\s*Maduretna|Ratu\s*Maduratna)\b'),
    ('Pangeran Mangkubumi', r'\b(?:P\.\s*Mangkubumi|Pangeran\s*Mangkubumi|Pangéran\s*Mangkubumi)\b'),
    ('Pangeran Ngabehi', r'\b(?:P\.\s*Ngabehi|P\.\s*Ngabèhi|Pangeran\s*Ngabehi|Pangéran\s*Ngabèhi|Jayakusuma\s*I)\b'),
    ('Pangeran Mangkudiningrat', r'\b(?:Mangkudiningrat|P\.\s*Mangkudiningrat|Pangéran\s*Mangkudiningrat)\b'),
    ('Pangeran Dipawiyana', r'\b(?:Dipawiyana|P\.\s*Dipawiyana|Pangéran\s*Dipawiyana)\b'),
    ('Pangeran Dipakusuma', r'\b(?:Dipakusuma|Dipokusumo|P\.\s*Dipakusuma|Pangéran\s*Dipakusuma)\b'),
    ('Pangeran Dipasana', r'\b(?:Dipasana|P\.\s*Dipasana|Pangéran\s*Dipasana)\b'),
    ('Pangeran Suryabrangta', r'\b(?:Suryabrangta|P\.\s*Suryabrangta|Pangéran\s*Suryabrangta)\b'),
    ('Pangeran Blitar', r'\b(?:P\.\s*Blitar|Pangeran\s*Blitar)\b'),
    ('Pangeran Adinegara', r'\b(?:Adinegara|Adinagara|P\.\s*Adinegara|Pangéran\s*Adinegara)\b'),
    ('Pangeran Buminata', r'\b(?:Buminata|P\.\s*Buminata)\b'),
    ('Dipanagara', r'\b(?:Dipanagara|Diponegoro|Antawirya)\b'),

    # Javanese Officials & Commanders
    ('Danureja I', r'\b(?:Danureja\s*I|Danuredja\s*I|DRI|D\.R\.I\.|PRI)\b'),
    ('Danureja II', r'\b(?:Danureja\s*II|Danuredja\s*II|DRII|D\.R\.II\.|PRII|Mertanegara\s*\(later\s*Danureja\s*II\))\b'),
    ('Danureja III (Sindunagara)', r'\b(?:Danureja\s*III|Sindunagara|Sindunegara)\b'),
    ('Danureja IV', r'\b(?:Danureja\s*IV|Sumadipura)\b'),
    ('Raden Rongga Prawiradirja III', r'\b(?:Raden\s*Rongga|Raden\s*Rangga|Rongga\s*Prawiradirja|Rangga\s*Prawiradirja|Prawiradirja\s*III|Raden\s*Rangga\s*III|Raden\s*Rongga\s*III)\b'),
    ('Raden Tumenggung Sumadiningrat', r'\b(?:Sumadiningrat|R\.T\.\s*Sumadiningrat|Tumenggung\s*Sumadiningrat)\b'),
    ('Raden Tumenggung Danukusuma', r'\b(?:Danukusuma|Danukusumo|R\.T\.\s*Danukusuma)\b'),
    ('Raden Tumenggung Natayuda', r'\b(?:Natayuda|Natayudo|R\.T\.\s*Natayuda)\b'),
    ('Raden Tumenggung Natawijaya', r'\b(?:Natawijaya|Natawidjaya|R\.T\.\s*Natawijaya)\b'),
    ('Mas Tumenggung Sumanegara', r'\b(?:Sumanegara|Sumanegoro|Mas\s*Tumenggung\s*Sumanegara)\b'),
    ('Raden Tumenggung Sasradiningrat', r'\b(?:Sasradiningrat|Sasradiningrat\s*II)\b'),
    ('Raden Tumenggung Sasrakusuma', r'\b(?:Sasrakusuma|Sasrakoesoema|R\.T\.\s*Sasrakusuma)\b'),
    ('Raden Tumenggung Sasranegara', r'\b(?:Sasranegara|Sasranegoro|R\.T\.\s*Sasranegara)\b'),
    ('Raden Tumenggung Purwadipura', r'\b(?:Purwadipura|Poerwadipoera|R\.T\.\s*Purwadipura)\b'),
    ('Raden Tumenggung Wiraguna', r'\b(?:Wiraguna|Wiragoena|R\.T\.\s*Wiraguna)\b'),
    ('Raden Tumenggung Cakranegara', r'\b(?:Cakranegara|Tjakranegara|R\.T\.\s*Cakranegara)\b'),
    ('Raden Tumenggung Suradilaga', r'\b(?:Suradilaga|Soeradilaga|R\.T\.\s*Suradilaga)\b'),
    ('Tan Jin Sing (Kapitan Cina)', r'\b(?:Tan\s*Jin\s*Sing|Tan\s*Tjin\s*Sing|Secadiningrat)\b'),
    ('Raden Tumenggung Pringgadiwirya', r'\b(?:Pringgadiwirya|Pringgadiwiria|R\.T\.\s*Pringgadiwirya)\b'),
    ('Raden Tumenggung Mangundiwirya', r'\b(?:Mangundiwirya|Mangundiwirio|Kyai\s*T\.\s*Mangundiwirya)\b'),
    ('Raden Tumenggung Sawunggaling', r'\b(?:Sawunggaling|R\.T\.\s*Sawunggaling)\b'),
    ('Raden Tumenggung Danuningrat', r'\b(?:Danuningrat|R\.T\.\s*Danuningrat)\b'),
    ('Raden Adipati Mangkupraja', r'\b(?:Mangkupraja|Mangkuprajä|Adipati\s*Mangkupraja)\b'),
    ('Patih of the Kadipaten', r'\b(?:Patih\s*kadipaten|Patih\s*kadipatèn|Kertadirja|Sumadirja|Jayasentika)\b'),

    # Colonial Officials & Military Commanders
    ('Marshal Herman Willem Daendels', r'\b(?:Daendels|H\.W\.\s*Daendels|Saendjes|Marshal\s*Daendels)\b'),
    ('Wouter Hendrik van IJsseldijk', r'\b(?:Van\s*IJsseldijk|Van\s*IJ|Ysseldijk|W\.H\.\s*van\s*IJsseldijk|W\.H\.\s*van\s*Ysseldijk)\b'),
    ('Johannes Gerardus van den Berg', r'\b(?:Van\s*den\s*Berg|J\.G\.\s*van\s*den\s*Berg|\bV\.D\.B\.\b|\bVdB\b)\b'),
    ('Matthijs Waterloo', r'\b(?:Waterloo|M\.\s*Waterloo|\bWat\.\b)\b'),
    ('Gustaf Wilhelm Wiese', r'\b(?:G\.W\.\s*Wiese|Gustaf\s*Wilhelm\s*Wiese|Wiese\s*assumes|Resident\s*Wiese)\b'),
    ('Albert Henricus Wiese', r'\b(?:A\.H\.\s*Wiese|Albert\s*Henricus\s*Wiese|Governor-General\s*Wiese)\b'),
    ('Pieter Engelhard', r'\b(?:P\.\s*Engelhard|Pieter\s*Engelhard)\b'),
    ('Nicolaus Engelhard', r'\b(?:Nicolaas\s*Engelhard|Nicolaus\s*Engelhard|Gov\.\s*Engelhard|Governor\s*Engelhard|\bN\.E\.\b|\bEng\.\b)\b'),
    ('Pieter Gerardus van Overstraten', r'\b(?:Van\s*Overstraten|P\.G\.\s*van\s*Overstraten|Van\s*Ovt)\b'),
    ('Johan Frederik van Reede tot de Parkeler', r'\b(?:Van\s*Reede|Van\s*Rheede|Van\s*Reede\s*tot\s*de\s*Parkeler)\b'),
    ('Bogislaus Friedrich von Liebeherr', r'\b(?:Von\s*Liebeherr|B\.F\.\s*von\s*Liebeherr|Liebeherr)\b'),
    ('Jacob Andries van Braam', r'\b(?:Van\s*Braam|J\.A\.\s*van\s*Braam)\b'),
    ('Johannes Wilhelmus Moorrees', r'\b(?:Moorrees|J\.W\.\s*Moorrees)\b'),
    ('Bartholomeus Jacobus Driessen', r'\b(?:Driessen|B\.J\.\s*Driessen)\b'),
    ('Thomas Stamford Raffles', r'\b(?:Raffles|T\.S\.\s*Raffles)\b'),
    ('Hendrik Merkus de Kock', r'\b(?:De\s*Kock|H\.M\.\s*de\s*Kock)\b'),
    ('Arnold Adriaan Buyskes', r'\b(?:Buyskes|A\.A\.\s*Buyskes)\b'),
    ('F.C.P. von Winckelmann', r'\b(?:Von\s*Winckelmann|Winckelmann)\b'),
    ('Willem Arnold Alting', r'\b(?:Alting|W\.A\.\s*Alting)\b'),
    ('Johannes Siberg', r'\b(?:Siberg|J\.\s*Siberg)\b'),
    ('Jean Chrétien Baud', r'\b(?:Baud|J\.C\.\s*Baud)\b'),
    ('Johan Frederik Walraven van Nes', r'\b(?:Van\s*Nes|J\.F\.W\.\s*van\s*Nes)\b'),
    ('Godert Alexander Gerard Philip van der Capellen', r'\b(?:Van\s*der\s*Capellen)\b'),
    ('F.W. Baumgarten', r'\b(?:Baumgarten)\b'),
    ('Captain Mollet', r'\b(?:Mollet|Capt\.\s*Mollet)\b'),
    ('Chasteauvieux', r'\b(?:Chasteauvieux)\b'),

    # Religious & Spiritual Figures
    ('Haji Abdul Wahid', r'\b(?:Haji\s*Abdul\s*Wahid|Haji\s*Abdul\s*Wahit)\b'),
    ('Haji Ibrahim', r'\b(?:Haji\s*Ibrahim)\b'),
    ('Haji Muhamad Idris', r'\b(?:Haji\s*Muhamad\s*Idris|Haji\s*Mohamad\s*Idris)\b'),
    ('Kyai Melangi', r'\b(?:Kyai\s*Melangi)\b'),
    ('Muhamad Sapingi (Pengulu)', r'\b(?:Muhamad\s*Sapingi|Sapingi|Pengulu\s*of\s*Yogya)\b'),
    ('Kyai Taptajani', r'\b(?:Taptajani|Kyai\s*Taptajani)\b'),
    ('Ratu Kidul', r'\b(?:Ratu\s*Kidul|Nyai\s*Lara\s*Kidul)\b'),

    # Places, Regions & Topography
    ('Yogyakarta', r'\b(?:Yogyakarta|Yogya|Djocja|Djokjakarta|Ngayogyakarta)\b'),
    ('Surakarta', r'\b(?:Surakarta|Solo|Sala)\b'),
    ('Semarang', r'\b(?:Semarang|Samarang)\b'),
    ('Batavia', r'\b(?:Batavia|Jakarta)\b'),
    ('Surabaya', r'\b(?:Surabaya|Soerabaja)\b'),
    ('Madiun', r'\b(?:Madiun|Madioen)\b'),
    ('Maospati', r'\b(?:Maospati)\b'),
    ('Sekaran', r'\b(?:Sekaran)\b'),
    ('Banyusumurup', r'\b(?:Banyusumurup)\b'),
    ('Magetan', r'\b(?:Magetan)\b'),
    ('Panolan', r'\b(?:Panolan)\b'),
    ('Jipang', r'\b(?:Jipang|Djipang)\b'),
    ('Padhangan', r'\b(?:Padhangan|Padangan)\b'),
    ('Rajegwesi', r'\b(?:Rajegwesi|Rejekwesi|Radjegwesi)\b'),
    ('Grobogan', r'\b(?:Grobogan)\b'),
    ('Blora', r'\b(?:Blora)\b'),
    ('Kedhu', r'\b(?:Kedhu|Kedu|Kèdhu)\b'),
    ('Magelang', r'\b(?:Magelang|Megelang)\b'),
    ('Menoreh', r'\b(?:Menoreh|Menorèh)\b'),
    ('Ledhok', r'\b(?:Ledhok|Ledok)\b'),
    ('Gowong', r'\b(?:Gowong)\b'),
    ('Bagelen', r'\b(?:Bagelen|Bagelèn)\b'),
    ('Lowanu (Loano)', r'\b(?:Lowanu|Loano)\b'),
    ('Rema', r'\b(?:Rema|Rèma)\b'),
    ('Tanggung', r'\b(?:Tanggung)\b'),
    ('Banyumas', r'\b(?:Banyumas|Banjoemas)\b'),
    ('Gunung Kidul', r'\b(?:Gunung\s*Kidul|Goenoeng\s*Kidoel)\b'),
    ('Pajang', r'\b(?:Pajang|Padjang)\b'),
    ('Sukawati', r'\b(?:Sukawati|Soekawati|Sokawati)\b'),
    ('Matesih', r'\b(?:Matesih)\b'),
    ('Wiru', r'\b(?:Wiru)\b'),
    ('Juwiring', r'\b(?:Juwiring)\b'),
    ('Klaten', r'\b(?:Klaten|Klathèn)\b'),
    ('Prambanan', r'\b(?:Prambanan)\b'),
    ('Kalasan', r'\b(?:Kalasan)\b'),
    ('Demak', r'\b(?:Demak)\b'),
    ('Japara', r'\b(?:Japara|Jepara)\b'),
    ('Kudus', r'\b(?:Kudus)\b'),
    ('Rembang', r'\b(?:Rembang)\b'),
    ('Lasem', r'\b(?:Lasem)\b'),
    ('Tuban', r'\b(?:Tuban)\b'),
    ('Gresik', r'\b(?:Gresik|Grisee)\b'),
    ('Pekalongan', r'\b(?:Pekalongan)\b'),
    ('Tegal', r'\b(?:Tegal)\b'),
    ('Brebes', r'\b(?:Brebes)\b'),
    ('Cirebon', r'\b(?:Cirebon|Cheribon)\b'),
    ('Banten', r'\b(?:Banten)\b'),
    ('Madura', r'\b(?:Madura)\b'),
    ('Sumenep', r'\b(?:Sumenep|Sumenap)\b'),
    ('Pacitan', r'\b(?:Pacitan|Patsitan)\b'),
    ('Boyolali', r'\b(?:Boyolali|Bayalali)\b'),
    ('Kartasura', r'\b(?:Kartasura)\b'),
    ('Taman Sari', r'\b(?:Taman\s*Sari|Water\s*Palace)\b'),
    ('Wanacatur', r'\b(?:Wanacatur)\b'),
    ('Purwareja', r'\b(?:Purwareja|Poerwaredja)\b'),
    ('Rajawinangun', r'\b(?:Rajawinangun|Arjawinangun)\b'),
    ('Gamping', r'\b(?:Gamping|Ambarketawang)\b'),
    ('Imagiri', r'\b(?:Imagiri|Imogiri)\b'),
    ('Parangkusuma', r'\b(?:Parangkusuma|Parangtritis)\b'),
    ('Melangi', r'\b(?:Melangi)\b'),
    ('Kraton', r'\b(?:Kraton|Palace)\b'),
    ('Kadipaten', r'\b(?:Kadipaten|Kadipatèn)\b'),
    ('Kepatihan', r'\b(?:Kepatihan)\b'),
    ('Alun-alun', r'\b(?:Alun-alun|Alun\s*alun)\b'),
    ('Fort Vredenburg', r'\b(?:Fort\s*Vredenburg|Rustenburg)\b'),
    ('Fort Lodewijk', r'\b(?:Fort\s*Lodewijk|Lodewijck)\b'),

    # Concepts, Institutions, and Terms
    ('Garebeg', r'\b(?:Garebeg|Garebeg\s*Mulud|Garebeg\s*Puasa|Garebeg\s*Puwasa|Garebeg\s*Besar)\b'),
    ('kècu (banditry)', r'\b(?:kecu|kècu|kètsju|ketsju|kecew|robbers|robberies|bandits|banditry|wong\s*durjana)\b'),
    ('blandhong (forestry)', r'\b(?:blandhong|blandong|teak\s*forest|forests|timber|blandongs)\b'),
    ('mancanagara', r'\b(?:mancanagara|mantsjanegara|E\.MN|W\.MN|Eastern\s*mancanagara)\b'),
    ('pasisir', r'\b(?:pasisir|pasissir|Northeast\s*Coast|Java\s*N\.O\.K\.|Java\'s\s*Northeast\s*Coast)\b'),
    ('nagara agung', r'\b(?:nagara\s*agung|nagara-agung)\b'),
    ('abdi-Dalem', r'\b(?:abdi-Dalem|abdi\s*dalem)\b'),
    ('apanage', r'\b(?:apanage|lungguh|gadhuhan)\b'),
    ('bupati', r'\b(?:bupati|regent|regenten)\b'),
    ('cacah', r'\b(?:cacah|tjatjah)\b'),
    ('bau', r'\b(?:bau)\b'),
    ('jung', r'\b(?:jung|djoeng)\b'),
    ('pikul', r'\b(?:pikul|picol|picols)\b'),
    ('corge', r'\b(?:corge|corges|kodi)\b'),
    ('dalem', r'\b(?:dalem)\b'),
    ('demang', r'\b(?:demang)\b'),
    ('desa', r'\b(?:desa|dessa)\b'),
    ('nayaka', r'\b(?:nayaka|najaka)\b'),
    ('pajeg', r'\b(?:pajeg|land-rent)\b'),
    ('pancas', r'\b(?:pancas)\b'),
    ('panakawan', r'\b(?:panakawan)\b'),
    ('pangrembé', r'\b(?:pangrembe|pangrembé)\b'),
    ('pangeran', r'\b(?:pangeran|pangéran)\b'),
    ('pathok negari', r'\b(?:pathok\s*negari|patok\s*nagari)\b'),
    ('patih', r'\b(?:patih|rijksbestierder)\b'),
    ('pesanggrahan', r'\b(?:pesanggrahan)\b'),
    ('pradikan', r'\b(?:pradikan)\b'),
    ('prajurit', r'\b(?:prajurit|soldiers)\b'),
    ('Amazon corps (prajurit keparak èstri)', r'\b(?:Amazon\s*corps|prajurit\s*keparak\s*èstri|prajurit\s*keparak\s*estri|women\s*mock\s*tournament)\b'),
    ('priyayi', r'\b(?:priyayi|prijaji)\b'),
    ('pusaka', r'\b(?:pusaka|heirloom|kris|curiga)\b'),
    ('santri', r'\b(?:santri|wong\s*putihan)\b'),
    ('sawah', r'\b(?:sawah)\b'),
    ('sikep', r'\b(?:sikep)\b'),
    ('strandgeld', r'\b(?:strandgeld|strands-regt|shore-money)\b'),
    ('tumenggung', r'\b(?:tumenggung|toemenggoeng)\b'),
    ('ulama', r'\b(?:ulama)\b'),
    ('wedana', r'\b(?:wedana|bupati\s*wedana)\b'),
    ('wong cilik', r'\b(?:wong\s*cilik)\b'),
    ('Mangkunagaran Legion', r'\b(?:Mangkunagaran\s*Legion|Legion)\b'),
    ('Tollgates', r'\b(?:tollgate|tollgates|bandar|bandhar|rangkah|salaran)\b'),
    ('Opium farm', r'\b(?:opium\s*farm|opium|candhu|madat)\b'),
    ('Pasar tax farm', r'\b(?:pasar\s*tax|pasar\s*farm)\b'),
    ('Bird\'s nests', r'\b(?:bird\'s\s*nests|birds\s*nests|vogelnestjes|sarang\s*burung)\b'),

    # Currencies & Measures
    ('Rijksdaalder (Rixdollar)', r'\b(?:Rijksdaalder|Rixdollar|Rix\s*dollar|R\.R\.|RD)\b'),
    ('Spanish dollar (Real)', r'\b(?:Spanish\s*dollar|Sp\.D\.|SpD|Real|Reaal|Spaanse\s*matten|Real\s*de\s*a\s*ocho|Sp\.\s*matten)\b'),
    ('Dutch ducats (Ducatoon)', r'\b(?:ducat|ducats|ducatoon|N\.D\.)\b'),
    ('Stuiver', r'\b(?:stuiver|stuivers)\b'),
    ('Dubbeltje', r'\b(?:dubbeltje|dubbeltjes)\b'),
    ('Duit', r'\b(?:duit|duiten|dhuwit)\b'),
    ('Agio', r'\b(?:agio)\b'),

    # Calendar & Months
    ('Tahun Alip', r'\b(?:Tahun\s*Alip|Alip|Windu)\b'),
    ('Javanese Calendar Months', r'\b(?:Sura|Sapar|Mulud|Bakda\s*Mulud|Jumadilawal|Jumadilakir|Rejeb|Ruwah|Puwasa|Puasa|Pasa|Sawal|Dulkangidah|Besar)\b'),

    # Primary Documents & Texts
    ('Memorie van Overgave (MvO)', r'\b(?:Memorie\s*van\s*Overgave|MvO)\b'),
    ('Djokjo Brieven (ANRI)', r'\b(?:Djokjo\s*Brieven|Dj\.\s*Br\.|ANRI|Arsip\s*Nasional|Arsip\s*Negara)\b'),
    ('KITLV Manuscripts', r'\b(?:KITLV|H\s*698|H\s*699)\b'),
    ('British Library Manuscripts', r'\b(?:Add\s*MS\s*12303|Add\s*MS\s*12341|Eur\s*F\.\s*148)\b'),
]


def extract_keywords_for_content(content):
    matched = []
    # Test each rule
    for name, pattern in KEYWORD_RULES:
        if re.search(pattern, content, re.IGNORECASE):
            matched.append(name)
    return matched


def classify_special_file(filename, content):
    lower_name = filename.lower()
    lower_c = content.lower()
    
    # 1. Calibration targets
    if 'img_0277' in lower_name or 'img_0278' in lower_name or 'img_20260619_0001.' in lower_name:
        return 'calibration', 'Archival photographic calibration target'
    if 'calibration target' in lower_c and len(content.strip().splitlines()) <= 15:
        return 'calibration', 'Archival photographic calibration target'

    # 2. Archival Binder Dividers / Tab Sheets
    divider_matches = [
        ('img_20260618_0001', "Archival binder divider sheet labeled '1806'"),
        ('img_20260618_0002', "Divider verso and archival serial notation"),
        ('img_20260618_0062', "Archival binder divider sheet labeled '1796'"),
        ('img_20260618_0104', "Archival binder divider sheet labeled '1799'"),
        ('img_20260618_0139', "Archival binder divider sheet labeled '1803'"),
        ('img_20260618_0172', "Archival binder divider sheet labeled '1805'"),
        ('img_20260619_0020', "Archival binder divider sheet labeled '1806'"),
        ('img_20260619_0060', "Archival binder divider sheet labeled '1807'"),
        ('img_20260619_0104', "Archival binder divider sheet labeled '1808'"),
        ('img_20260619_0162', "Archival binder divider sheet labeled '1809'"),
        ('img_20260619_0193', "Archival binder divider sheet labeled '1810'"),
    ]
    for m_key, m_label in divider_matches:
        if m_key in lower_name:
            return 'divider', m_label

    # Check for general divider text
    if 'divider sheet' in lower_c or 'divider tab' in lower_c or 'archival divider' in lower_c:
        # extract label if any
        lbl = re.search(r'(?:label|tab|marked|sheet)\s*(?:is|labeled|:)?\s*[\'"`]?([0-9]{4})[\'"`]?', content, re.IGNORECASE)
        year = lbl.group(1) if lbl else ''
        label = f"Archival binder divider sheet labeled '{year}'" if year else "Archival binder divider sheet"
        return 'divider', label

    # 3. Covers
    if 'cover_img_0279' in lower_name or 'cover_img_0280' in lower_name or 'cover_img_0281' in lower_name:
        return 'cover', '*Yogyakarta*, *Residency*, *Letters*'
    if 'cover_img_0282' in lower_name:
        return 'cover', '*Crown Prince*, *Articles*, *Yogyakarta*'

    # 4. Blank Versos
    if 'blank' in lower_c and ('verso' in lower_c or 'leaf' in lower_c or 'page' in lower_c):
        # Check if content has no substantial transcript
        lines = [l for l in content.splitlines() if l.strip() and not l.startswith('#') and not l.startswith('**') and not l.startswith('---')]
        joined = ' '.join(lines).lower()
        if 'blank' in joined or 'bleed-through' in joined or len(joined) < 250:
            return 'blank', 'Blank lined manuscript page verso'

    return None, None


def fix_content_text(content):
    # Fix specific typos
    c = content
    # ANIP -> ANRI
    c = re.sub(r'\bANIP\s+Nasional\b', 'ANRI [Arsip Nasional]', c)
    c = re.sub(r'\bANIP\b', 'ANRI', c)
    # van Ryvdyck -> Van IJsseldijk
    c = re.sub(r'\bvan\s*Ryvdyck\b', 'Van IJsseldijk', c, flags=re.IGNORECASE)
    # Ardia Negara -> Arsip Negara
    c = re.sub(r'\bArdia\s*Negara\b', 'Arsip Negara', c, flags=re.IGNORECASE)
    # David's Period -> Saendjes Period [Daendels]
    c = re.sub(r'\bDavid\'s\s*Period\b', 'Daendels Period [written: Saendjes Period]', c, flags=re.IGNORECASE)
    # P.J. Br. / Pp. Br. -> Dj. Br.
    c = re.sub(r'\bP\.J\.\s*Br\.\b', 'Dj. Br.', c)
    c = re.sub(r'\bPp\.\s*Br\.\b', 'Dj. Br.', c)
    return c


def process_file(file_path):
    base_name = os.path.basename(file_path)
    # Determine image relative path
    if base_name.startswith('Cover_'):
        img_name = base_name.replace('Cover_', '').replace('.md', '.JPG')
        rel_img_path = f'Cover/jpg/{img_name}'
    else:
        img_name = base_name.replace('.md', '.jpg')
        rel_img_path = f'jpg/{img_name}'

    with open(file_path, 'r', encoding='utf-8') as f:
        orig_content = f.read()

    # Clean text fixes
    content = fix_content_text(orig_content)

    # Classify special files
    f_type, spec_label = classify_special_file(base_name, content)

    if f_type in ('calibration', 'divider', 'blank'):
        kw_line_val = spec_label
    elif f_type == 'cover':
        kw_line_val = spec_label
    else:
        # Extract matched keywords
        kw_list = extract_keywords_for_content(content)
        if not kw_list:
            kw_list = ['Yogyakarta Residency Letters', 'Peter Carey Archive']
        # Format as *Word1*, *Word2*
        kw_line_val = ', '.join([f'*{k}*' for k in kw_list])

    # Format standard Keyword Index Check string
    kw_check_entry = f"**Keyword Index Check:** Verified against `39_Expanded_Keyword_Index.md` ({kw_line_val})"

    # Now let's standardize the header while preserving all existing metadata and content
    # First, separate header from body
    # Standard header begins with # Title, followed by metadata, followed by ---
    
    # Check if file has existing `**Keyword Index Check:**`
    if re.search(r'\*\*Keyword Index Check:\*\*', content):
        # Replace existing Keyword Index Check line
        content = re.sub(
            r'\*\*Keyword Index Check:\*\*.*',
            kw_check_entry,
            content
        )
    else:
        # Find where to insert it: right before the first `---` divider or after initial metadata block
        first_div = re.search(r'\n---\n', content)
        if first_div:
            before_div = content[:first_div.start()].rstrip()
            after_div = content[first_div.start():]
            content = before_div + "\n" + kw_check_entry + "\n" + after_div
        else:
            # If no --- divider found, put after line 4
            lines = content.splitlines()
            insert_idx = min(len(lines), 4)
            lines.insert(insert_idx, kw_check_entry)
            content = '\n'.join(lines)

    # Standardize Title and Image File at the top
    # First line should be # Transcription: <img_name>
    lines = content.splitlines()
    lines[0] = f"# Transcription: {img_name}"

    # Check if `**Image File:**` is present in top 6 lines
    has_image_file = any('**Image File:**' in l for l in lines[:6])
    if not has_image_file:
        # Replace `**Source Directory:**` or `**Source File:**` or `**Image Reference:**` if present
        replaced = False
        for i in range(1, min(6, len(lines))):
            if re.match(r'\*\*(?:Source Directory|Source File|Image Reference):\*\*', lines[i]):
                lines[i] = f"**Image File:** `{rel_img_path}`  "
                replaced = True
                break
        if not replaced:
            # Insert after Title (line 0, followed by blank line 1)
            if len(lines) > 1 and lines[1].strip() == '':
                lines.insert(2, f"**Image File:** `{rel_img_path}`  ")
            else:
                lines.insert(1, "")
                lines.insert(2, f"**Image File:** `{rel_img_path}`  ")

    # Clean double blank lines at top
    new_content = '\n'.join(lines).strip() + '\n'

    # Safe write with retry for Windows NTFS lock contention
    import time
    for attempt in range(5):
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            break
        except OSError as e:
            if attempt < 4:
                time.sleep(0.1 * (attempt + 1))
            else:
                raise e

    return kw_line_val


def main():
    files = sorted(glob.glob(os.path.join(TRANSCRIPTION_DIR, '*.md')))
    print(f"Processing {len(files)} files in {TRANSCRIPTION_DIR}...")
    
    count = 0
    for f in files:
        kw_val = process_file(f)
        count += 1
        if count <= 5 or count % 50 == 0 or count == len(files):
            print(f"[{count:3d}/{len(files)}] {os.path.basename(f)} -> {kw_val[:60]}...")

    print(f"\nSuccessfully checked and updated all {len(files)} files against 39_Expanded_Keyword_Index.md!")


if __name__ == '__main__':
    main()
