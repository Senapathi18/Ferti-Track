# populate_villages.py
# Run this ONCE: python populate_villages.py
# Adds all AP districts, mandals and villages to your database

import sqlite3
import os

DB_PATH = "data/shop.db"
os.makedirs("data", exist_ok=True)

AP_DATA = {
    "Ananthapuramu": {
        "Ananthapuramu": [
            "Ananthapuramu","Aravapalli","Atmakur","Beluguppa","Chapadu",
            "Chilakaladona","Chinnapothula","Chippagiri","Dakshina Kallur",
            "Gollamadugu","Gurunathapuram","Hampasagara","Hanumanthunipadu",
            "Hussainapuram","Indukurpet","Irlapadu","Jilledupalli","Kanaganapalle",
            "Kanjamallapuram","Kanuparthi","Kodipalli","Kothavalasa","Kotukallu",
            "Krishnapur","Lakkireddipalle","Lepakshi","Lingsugur","Maddipatla",
            "Mandapampadu","Mangampeta","Nallacheruvu","Nayudupeta","Peddur",
            "Pennekondapalem","Reddypalli","Rekulakunta","Setturu","Shapur",
            "Singampalli","Somandepalli","Talupula","Thimmapuram","Thurimella",
            "Upparapalli","Veldurthi","Vemula","Yellanur","Yemmiganur",
            "Amadagur","Bommanahal","Brahmasamudram","Bukkapatnam",
            "Challavaripalle","Chilamathur","Chinnakotla","Devarapalle",
            "Dindukurthi","Gajulapalem","Gandlapenta","Gollapalle","Gorantla",
            "Gudibanda","Gudipalle","Inakolu","Jangalapalle","Kallur",
            "Kalyandurgam","Kamalapuram","Karakambadi","Kethanapalem",
            "Kodikonda","Kogilavaripalle","Kotlapalle","Krishnapuram",
            "Kuppam","Mudigubba","Mulagallu","Nambula Pulakunta","Nannepalle",
            "Narpala","Nayanapalle","Nimmagadda","Obuladevaracheruvu","Parigi",
            "Peddapappur","Penukonda","Puttaparthi","Ramagiri","Rayadurgam",
            "Roddam","Rolla","Singanamala","Tadimarri","Thanakal",
            "Uravakonda","Vajrakarur","Yadiki"
        ],
        "Dharmavaram": [
            "Dharmavaram","Airavanipalli","Akulamadu","Alagavemula","Amarapuram",
            "Anaparthi","Anjaneyapuram","Atmakur","Baireddipalle","Bathalavaripalle",
            "Brahmasamudram","Bukkapatnam","Challavaripalle","Chinnakotla",
            "Chintakommadinne","Dindukurthi","Gajulapalem","Gandlapenta",
            "Gollapalle","Gorantla","Gudibanda","Gudipalle","Inakolu",
            "Jangalapalle","Kalyandurgam","Kamalapuram","Karakambadi",
            "Kethanapalem","Kodikonda","Kogilavaripalle","Kothavalasa",
            "Kotlapalle","Krishnapuram","Kuppam","Madhavaram","Mudigubba",
            "Mulagallu","Nallacheruvu","Nambula Pulakunta","Nannepalle",
            "Narpala","Nayanapalle","Nimmagadda","Parigi","Peddapappur",
            "Penukonda","Ramagiri","Rayadurgam","Roddam","Rolla","Setturu",
            "Singanamala","Somandepalli","Tadimarri","Tanakal","Thimmasamudram",
            "Veldurthi","Vidapanakal","Yellanur"
        ],
        "Hindupur": [
            "Hindupur","Agali","Amarapuram","Bangarupeta","Brahmasamudram",
            "Chakicherla","Chilamathur","Dantalamarri","Doddasomanahalli",
            "Gollapalle","Gopalpet","Gudibanda","Hampasagara","Hebbur",
            "Hirehal","Horpet","Hulikal","Kadiri","Kallur","Kamalapuram",
            "Kanugolu","Karakambadi","Kasapuram","Kodikonda","Kothavalasa",
            "Krishnapuram","Kuppam","Lepakshi","Madakasira","Makkasamudram",
            "Nallamada","Nambula Pulakunta","Nannepalle","Narpala","Nayanapalle",
            "Nimmagadda","Parigi","Peddapappur","Penukonda","Ramagiri",
            "Rayadurgam","Roddam","Rolla","Setturu","Singanamala","Somandepalli",
            "Tadimarri","Talupula","Thanakal","Uravakonda","Vajrakarur","Yadiki","Yellanur"
        ],
        "Kadiri": [
            "Kadiri","Agali","Aravapalli","Atlur","Atmakur","Bathalavaripalle",
            "Bommanahal","Challavaripalle","Chilamathur","Chitravati",
            "Devarapalle","Gandlapenta","Garbham","Gollapalle","Gorantla",
            "Gudibanda","Hampasagara","Inakolu","Jalasangvi","Jangalapalle",
            "Kallur","Kamalapuram","Karakambadi","Karuvela","Kethanapalem",
            "Kodikonda","Kothavalasa","Krishnapuram","Kuppam","Lepakshi",
            "Madakasira","Makkasamudram","Mudigubba","Mulagallu","Nallacheruvu",
            "Nambula Pulakunta","Nannepalle","Narpala","Nayanapalle","Nimmagadda",
            "Obuladevaracheruvu","Parigi","Peddapappur","Penukonda","Ramagiri",
            "Rayadurgam","Roddam","Rolla","Setturu","Singanamala","Somandepalli",
            "Tadimarri","Talupula","Thanakal","Uravakonda","Vajrakarur","Yadiki","Yellanur"
        ],
        "Madakasira": [
            "Madakasira","Akulamadu","Amarapuram","Anaparthi","Anjaneyapuram",
            "Baireddipalle","Bathalavaripalle","Challavaripalle","Chinnakotla",
            "Chintakommadinne","Dindukurthi","Gajulapalem","Gandlapenta",
            "Gollapalle","Gorantla","Gudibanda","Gudipalle","Hindupur",
            "Inakolu","Jangalapalle","Kalyandurgam","Kamalapuram","Karakambadi",
            "Kethanapalem","Kodikonda","Kogilavaripalle","Kothavalasa","Kotlapalle",
            "Krishnapuram","Kuppam","Madhavaram","Makkasamudram","Mudigubba",
            "Mulagallu","Nallacheruvu","Nambula Pulakunta","Nannepalle","Narpala",
            "Nayanapalle","Nimmagadda","Parigi","Peddapappur","Penukonda",
            "Ramagiri","Roddam","Rolla","Setturu","Singanamala","Somandepalli"
        ],
        "Penukonda": [
            "Penukonda","Agali","Amarapuram","Anaparthi","Anjaneyapuram",
            "Atmakur","Baireddipalle","Bathalavaripalle","Bukkapatnam",
            "Challavaripalle","Chilamathur","Chinnakotla","Devarapalle",
            "Dindukurthi","Gajulapalem","Gandlapenta","Gollapalle","Gorantla",
            "Gudibanda","Gudipalle","Hindupur","Inakolu","Jangalapalle",
            "Kadiri","Kallur","Kamalapuram","Karakambadi","Kethanapalem",
            "Kodikonda","Kogilavaripalle","Kothavalasa","Kotlapalle","Krishnapuram",
            "Kuppam","Lepakshi","Madakasira","Makkasamudram","Mudigubba",
            "Mulagallu","Nallacheruvu","Nambula Pulakunta","Nannepalle","Narpala",
            "Nayanapalle","Nimmagadda","Parigi","Peddapappur","Puttaparthi",
            "Ramagiri","Roddam","Rolla","Setturu","Singanamala","Somandepalli",
            "Tadimarri","Talupula","Thanakal","Uravakonda","Vajrakarur","Yadiki","Yellanur"
        ],
        "Tadimarri": [
            "Tadimarri","Amadagur","Atmakur","Beluguppa","Bommanahal",
            "Challavaripalle","Chilamathur","Chinnakotla","Devarapalle",
            "Gajulapalem","Gandlapenta","Gollapalle","Gorantla","Gudibanda",
            "Gudipalle","Inakolu","Jangalapalle","Kallur","Kamalapuram",
            "Karakambadi","Kethanapalem","Kodikonda","Kogilavaripalle",
            "Kothavalasa","Kotlapalle","Krishnapuram","Kuppam","Lepakshi",
            "Mudigubba","Mulagallu","Nallacheruvu","Nambula Pulakunta",
            "Nannepalle","Narpala","Nayanapalle","Nimmagadda","Parigi",
            "Peddapappur","Penukonda","Ramagiri","Roddam","Rolla","Setturu",
            "Singanamala","Somandepalli","Talupula","Thanakal","Uravakonda",
            "Vajrakarur","Yadiki","Yellanur"
        ],
        "Uravakonda": [
            "Uravakonda","Amadagur","Atmakur","Beluguppa","Bommanahal",
            "Challavaripalle","Chilamathur","Devarapalle","Gajulapalem",
            "Gandlapenta","Gollapalle","Gorantla","Gudibanda","Gudipalle",
            "Inakolu","Jangalapalle","Kallur","Kamalapuram","Karakambadi",
            "Kethanapalem","Kodikonda","Kogilavaripalle","Kothavalasa",
            "Kotlapalle","Krishnapuram","Kuppam","Mudigubba","Mulagallu",
            "Nallacheruvu","Nambula Pulakunta","Nannepalle","Narpala",
            "Nayanapalle","Nimmagadda","Parigi","Peddapappur","Ramagiri",
            "Roddam","Rolla","Setturu","Singanamala","Somandepalli",
            "Talupula","Thanakal","Vajrakarur","Yadiki","Yellanur"
        ],
        "Atmakur": [
            "Atmakur","Amadagur","Beluguppa","Bommanahal","Challavaripalle",
            "Chilamathur","Gajulapalem","Gandlapenta","Gollapalle","Gorantla",
            "Gudibanda","Inakolu","Jangalapalle","Kallur","Kamalapuram",
            "Kethanapalem","Kodikonda","Kothavalasa","Krishnapuram","Kuppam",
            "Nallacheruvu","Nambula Pulakunta","Nannepalle","Narpala",
            "Obuladevaracheruvu","Parigi","Pamidi","Putlur","Ramagiri",
            "Rapthadu","Roddam","Rolla","Setturu","Singanamala","Somandepalli",
            "Talupula","Thanakal","Uravakonda","Vajrakarur","Yadiki"
        ],
    },
    "Chittoor": {
        "Chittoor": [
            "Chittoor","Amanagallu","Arlagadda","Atmakur","Avalapadu",
            "Badvel","Baireddipalle","Banaganapalle","Bangarupalyam",
            "Bathalapalli","Bellamkonda","Bhairapur","Brahmasamudram",
            "Chandragiri","Dakkili","Gangineni","Gangivari Palle","Ganguru",
            "Gudipala","Irala","Kalikiri","Kalyandurgam","Kandukur",
            "Kuppam","Madanapalle","Nagari","Naidupeta","Nindra",
            "Obulavaripalle","Palamaner","Pakala","Penumur","Punganur",
            "Puthalapattu","Puttur","Ramasamudram","Renigunta","Sadum",
            "Santhipuram","Srikalahasti","Tada","Thamballapalle",
            "Vedurukuppam","Venkatagirikota","Yadamarri","Yerpedu"
        ],
        "Tirupati": [
            "Tirupati","Alipiri","Avilala","Chandragiri","Dargamitta",
            "Gangavaram","Kapila Theertham","Korlagunta","Krishnapuram",
            "Mangalam","Nagari","Naidupeta","Nindra","Pakala",
            "Papanaidupet","Pedda Tippa Samudram","Puttur","Ramasamudram",
            "Renigunta","Sadum","Santhipuram","Srikalahasti","Tada",
            "Thamballapalle","Tiruchanur","Tirumala","Vedurukuppam",
            "Venkatagirikota","Yerpedu"
        ],
        "Madanapalle": [
            "Madanapalle","Arlagadda","Bangarupalyam","Bathalapalli",
            "Bhairapur","Brahmasamudram","Dakkili","Gangineni","Ganguru",
            "Gudipala","Irala","Kalikiri","Kalyandurgam","Kandukur",
            "Kuppam","Nagari","Nindra","Obulavaripalle","Palamaner",
            "Pakala","Penumur","Punganur","Puthalapattu","Puttur",
            "Ramasamudram","Sadum","Santhipuram","Thamballapalle",
            "Vedurukuppam","Venkatagirikota","Yadamarri","Yerpedu"
        ],
        "Kuppam": [
            "Kuppam","Bangarupalyam","Bathalapalli","Bhairapur","Dakkili",
            "Gangineni","Ganguru","Gudipala","Irala","Kalikiri",
            "Kalyandurgam","Kandukur","Madanapalle","Nagari","Nindra",
            "Obulavaripalle","Palamaner","Pakala","Penumur","Punganur",
            "Puthalapattu","Puttur","Ramasamudram","Sadum","Santhipuram",
            "Thamballapalle","Vedurukuppam","Venkatagirikota","Yadamarri"
        ],
        "Srikalahasti": [
            "Srikalahasti","Amanagallu","Amudalavalasa","Chandragiri",
            "Dargamitta","Gangavaram","Gudipala","Irala","Kalahasti",
            "Kalikiri","Kandukur","Nagari","Naidupeta","Nindra","Pakala",
            "Penumur","Puttur","Ramasamudram","Renigunta","Sadum",
            "Santhipuram","Tada","Tiruchanur","Tirumala","Vedurukuppam",
            "Venkatagirikota","Yerpedu"
        ],
        "Punganur": [
            "Punganur","Obulavaripalle","Somala","Rompicherla","Kalikiri",
            "Bangarupalyam","Bathalapalli","Bhairapur","Dakkili","Gangineni",
            "Gudipala","Irala","Kalyandurgam","Kandukur","Kuppam",
            "Madanapalle","Nagari","Nindra","Palamaner","Pakala",
            "Penumur","Puthalapattu","Puttur","Ramasamudram","Sadum",
            "Santhipuram","Thamballapalle","Vedurukuppam","Yadamarri"
        ],
        "Palamaner": [
            "Palamaner","Gangadhara Nellore","Irala","Kalakada","Sodam",
            "Bangarupalyam","Bathalapalli","Bhairapur","Dakkili","Gangineni",
            "Ganguru","Gudipala","Kalikiri","Kalyandurgam","Kandukur",
            "Kuppam","Madanapalle","Nagari","Nindra","Obulavaripalle",
            "Pakala","Penumur","Punganur","Puthalapattu","Puttur",
            "Ramasamudram","Sadum","Santhipuram","Thamballapalle",
            "Vedurukuppam","Venkatagirikota","Yadamarri","Yerpedu"
        ],
    },
    "Guntur": {
        "Guntur": [
            "Guntur","Amaravati","Arundelpet","Ashok Nagar","Atmakur",
            "Autonagar","Bethapudi","Brodipet","Etukuru","Gorantla",
            "Ippatam","Kakani","Koritepadu","Krishnayapalem","Lakshmipuram",
            "Mangalagiri","Narasaraopet","Narsala","Nidamanuru","Pedakakani",
            "Pedanandipadu","Ponnur","Prathipadu","Seetharampuram",
            "Tadepalle","Tenali","Thullur","Tudali","Undavalli","Vatticherukuru"
        ],
        "Tenali": [
            "Tenali","Bapatla","Cherukupalle","Chirala","Duggirala",
            "Edlapadu","Gorantla","Ipur","Karlapalem","Kollipara",
            "Krishnayapalem","Lakshmipuram","Muppalla","Nidamanuru",
            "Ponnur","Prathipadu","Repalle","Sattenapalle","Seetharampuram",
            "Tadepalle","Thullur","Vemuru","Vinukonda"
        ],
        "Narasaraopet": [
            "Narasaraopet","Chilakaluripet","Dachepalle","Durgi","Edlapadu",
            "Gurazala","Ipur","Macherla","Narsala","Nekarikallu",
            "Phirangipuram","Piduguralla","Prathipadu","Rentachintala",
            "Sattenapalle","Veldurthi","Vinukonda","Yapaladinne"
        ],
        "Mangalagiri": [
            "Mangalagiri","Amaravati","Bethapudi","Etukuru","Gorantla",
            "Ippatam","Kakani","Koritepadu","Krishnayapalem","Lakshmipuram",
            "Nidamanuru","Pedakakani","Pedanandipadu","Ponnur","Prathipadu",
            "Seetharampuram","Tadepalle","Thullur","Undavalli","Vatticherukuru"
        ],
        "Sattenapalle": [
            "Sattenapalle","Cherukupalle","Chilakaluripet","Dachepalle",
            "Duggirala","Edlapadu","Gurazala","Ipur","Karlapalem",
            "Kollipara","Macherla","Nekarikallu","Phirangipuram","Piduguralla",
            "Prathipadu","Repalle","Tenali","Veldurthi","Vinukonda"
        ],
        "Chilakaluripet": [
            "Chilakaluripet","Dachepalle","Durgi","Edlapadu","Gurazala",
            "Ipur","Macherla","Narasaraopet","Narsala","Nekarikallu",
            "Phirangipuram","Piduguralla","Prathipadu","Rentachintala",
            "Sattenapalle","Veldurthi","Vinukonda","Yapaladinne"
        ],
        "Bapatla": [
            "Bapatla","Cherukupalle","Chirala","Duggirala","Inkollu",
            "Karlapalem","Karamchedu","Kollipara","Martur","Nagaram",
            "Nidubrolu","Parchur","Repalle","Santanuthalapadu",
            "Singarayakonda","Tripuranthakam","Vemuru","Vetapalem"
        ],
    },
    "Krishna": {
        "Vijayawada": [
            "Vijayawada","Ajit Singh Nagar","Auto Nagar","Benz Circle",
            "Bhavani Puram","Brodipet","Canal Road","Chuttugunta",
            "Eluru Road","Governorpet","Gudavalli","Ibrahimpatnam",
            "Jakkampudi","Kandrika","Kankipadu","Krishnalanka","Labbipet",
            "Machavaram","Moghalrajpuram","MG Road","Musunuru","Mylavaram",
            "Nandigama","Nunna","Penamaluru","Poranki","Rajiv Nagar",
            "Satyanarayanapuram","Siddhartha Nagar","Suryaraopet",
            "Tadepalle","Tiruvuru","Tummalapalle","Uyyuru","Vuyyuru","Yerrakuppa"
        ],
        "Machilipatnam": [
            "Machilipatnam","Avanigadda","Bantumilli","Challapalli",
            "Chatrai","Ghantasala","Gudivada","Hanuman Junction",
            "Ibrahimpatnam","Koduru","Kruthivennu","Mopidevi","Movva",
            "Nagayalanka","Nandigama","Pamarru","Pedana","Penamaluru",
            "Tiruvuru","Vuyyuru","Yenikepadu"
        ],
        "Gudivada": [
            "Gudivada","Bantumilli","Chatrai","Gannavaram","Hanuman Junction",
            "Ibrahimpatnam","Kaikaluru","Kankipadu","Koduru","Kruthivennu",
            "Movva","Musunuru","Mylavaram","Nandigama","Pamarru","Penamaluru",
            "Tiruvuru","Vuyyuru"
        ],
        "Nandigama": [
            "Nandigama","Avanigadda","Bantumilli","Chatrai","Gampalagudem",
            "Gannavaram","Gudivada","Ibrahimpatnam","Jaggayyapeta","Kaikaluru",
            "Kankipadu","Koduru","Kruthivennu","Movva","Musunuru","Mylavaram",
            "Pamarru","Penamaluru","Tiruvuru","Vatsavai","Vuyyuru"
        ],
        "Avanigadda": [
            "Avanigadda","Bantumilli","Challapalli","Chatrai","Ghantasala",
            "Koduru","Kruthivennu","Mopidevi","Movva","Nagayalanka",
            "Pamarru","Pedana","Penamaluru","Tiruvuru","Vuyyuru"
        ],
        "Jaggayyapeta": [
            "Jaggayyapeta","Bantumilli","Chatrai","Gampalagudem","Gannavaram",
            "Gudivada","Ibrahimpatnam","Kaikaluru","Kankipadu","Koduru",
            "Kruthivennu","Movva","Musunuru","Mylavaram","Nandigama",
            "Pamarru","Penamaluru","Tiruvuru","Vatsavai","Vuyyuru"
        ],
    },
    "Kurnool": {
        "Kurnool": [
            "Kurnool","Adoni","Alur","Aspari","Atmakur","Banaganapalle",
            "Betamcherla","C Belagal","Chagalamarri","Devanakonda","Dhone",
            "Dornipadu","Gospadu","Gudur","Halaharvi","Kodumur","Kosigi",
            "Krishnagiri","Maddikera","Mahanandi","Mantralayam","Nandavaram",
            "Nandikotkur","Nandyal","Orvakal","Pattikonda","Peapalle",
            "Rudravaram","Sanjamala","Sirvel","Tuggali","Uyyalawada",
            "Veldurthi","Yemmiganur"
        ],
        "Nandyal": [
            "Nandyal","Allagadda","Aspari","Atmakur","Banaganapalle",
            "Betamcherla","Chagalamarri","Dhone","Gospadu","Gudur",
            "Halaharvi","Kodumur","Kosigi","Krishnagiri","Maddikera",
            "Mahanandi","Mantralayam","Nandavaram","Nandikotkur","Orvakal",
            "Pattikonda","Peapalle","Rudravaram","Sanjamala","Sirvel",
            "Srisailam","Tuggali","Uyyalawada","Veldurthi","Yemmiganur"
        ],
        "Adoni": [
            "Adoni","Alur","Aspari","Atmakur","Banaganapalle","Betamcherla",
            "C Belagal","Chagalamarri","Devanakonda","Dhone","Dornipadu",
            "Gospadu","Gudur","Halaharvi","Kodumur","Kosigi","Krishnagiri",
            "Maddikera","Mahanandi","Mantralayam","Nandavaram","Nandikotkur",
            "Nandyal","Orvakal","Pattikonda","Peapalle","Rudravaram",
            "Sanjamala","Sirvel","Tuggali","Uyyalawada","Veldurthi","Yemmiganur"
        ],
        "Dhone": [
            "Dhone","Adoni","Alur","Aspari","Atmakur","Banaganapalle",
            "Betamcherla","C Belagal","Chagalamarri","Devanakonda","Dornipadu",
            "Gospadu","Gudur","Halaharvi","Kodumur","Kosigi","Krishnagiri",
            "Maddikera","Mahanandi","Mantralayam","Nandavaram","Nandikotkur",
            "Nandyal","Orvakal","Pattikonda","Peapalle","Rudravaram",
            "Sanjamala","Sirvel","Tuggali","Uyyalawada","Veldurthi","Yemmiganur"
        ],
        "Yemmiganur": [
            "Yemmiganur","Adoni","Alur","Aspari","Atmakur","Banaganapalle",
            "Betamcherla","C Belagal","Chagalamarri","Devanakonda","Dhone",
            "Dornipadu","Gospadu","Gudur","Halaharvi","Kodumur","Kosigi",
            "Krishnagiri","Maddikera","Mahanandi","Mantralayam","Nandavaram",
            "Nandikotkur","Nandyal","Orvakal","Pattikonda","Peapalle",
            "Rudravaram","Sanjamala","Sirvel","Tuggali","Uyyalawada","Veldurthi"
        ],
        "Atmakur": [
            "Atmakur","Adoni","Alur","Aspari","Banaganapalle","Betamcherla",
            "C Belagal","Chagalamarri","Devanakonda","Dhone","Dornipadu",
            "Gospadu","Gudur","Halaharvi","Kodumur","Kosigi","Krishnagiri",
            "Maddikera","Mahanandi","Mantralayam","Nandavaram","Nandikotkur",
            "Nandyal","Orvakal","Pattikonda","Peapalle","Rudravaram",
            "Sanjamala","Sirvel","Tuggali","Uyyalawada","Veldurthi","Yemmiganur"
        ],
    },
    "Prakasam": {
        "Ongole": [
            "Ongole","Addanki","Balaji Nagar","Chimakurthi","Chirala",
            "Darsi","Giddalur","Hanumanthunipadu","Inkollu","Kandukur",
            "Kanigiri","Korisapadu","Kondapi","Kurichedu","Markapuram",
            "Martur","Muppala","Mundlamuru","Naguluppalapad","Nereducherla",
            "Parchur","Podili","Santanuthalapadu","Singarayakonda",
            "Tangutur","Tripuranthakam","Ulavapadu","Vetapalem","Zarugumalli"
        ],
        "Chirala": [
            "Chirala","Addanki","Chimakurthi","Darsi","Giddalur",
            "Hanumanthunipadu","Inkollu","Kandukur","Kanigiri","Korisapadu",
            "Kondapi","Kurichedu","Markapuram","Martur","Muppala",
            "Mundlamuru","Naguluppalapad","Nereducherla","Parchur","Podili",
            "Santanuthalapadu","Singarayakonda","Tangutur","Tripuranthakam",
            "Ulavapadu","Vetapalem","Zarugumalli"
        ],
        "Markapuram": [
            "Markapuram","Addanki","Chimakurthi","Darsi","Giddalur",
            "Hanumanthunipadu","Inkollu","Kandukur","Kanigiri","Korisapadu",
            "Kondapi","Kurichedu","Martur","Muppala","Mundlamuru",
            "Naguluppalapad","Nereducherla","Parchur","Podili",
            "Santanuthalapadu","Singarayakonda","Tangutur","Tripuranthakam",
            "Ulavapadu","Vetapalem","Zarugumalli"
        ],
        "Kandukur": [
            "Kandukur","Addanki","Chimakurthi","Chirala","Darsi",
            "Giddalur","Hanumanthunipadu","Inkollu","Kanigiri","Korisapadu",
            "Kondapi","Kurichedu","Markapuram","Martur","Muppala",
            "Mundlamuru","Naguluppalapad","Nereducherla","Parchur","Podili",
            "Santanuthalapadu","Singarayakonda","Tangutur","Tripuranthakam",
            "Ulavapadu","Vetapalem","Zarugumalli"
        ],
        "Darsi": [
            "Darsi","Addanki","Chimakurthi","Chirala","Giddalur",
            "Hanumanthunipadu","Inkollu","Kandukur","Kanigiri","Korisapadu",
            "Kondapi","Kurichedu","Markapuram","Martur","Muppala",
            "Mundlamuru","Naguluppalapad","Nereducherla","Parchur","Podili",
            "Santanuthalapadu","Singarayakonda","Tangutur","Tripuranthakam",
            "Ulavapadu","Vetapalem","Zarugumalli"
        ],
    },
    "Visakhapatnam": {
        "Visakhapatnam": [
            "Visakhapatnam","Akkayyapalem","Arilova","Asilmetta","Bheemunipatnam",
            "Chaitanyapuri","Chinagadili","Daba Gardens","Duvvada","Endada",
            "Gajuwaka","Gambheeram","Gopalapatnam","Hanumanthawaka","Isukathota",
            "Jagadamba","Kommadi","Kondakarla","Maharanipeta","Malkapuram",
            "Marripalem","Mindi","MVP Colony","NAD Junction","Narasimha Nagar",
            "Pedagantyada","Pedawaltair","Pendurthi","PM Palem","Rushikonda",
            "Sagar Nagar","Seethammadara","Sheela Nagar","Steel Plant",
            "Sujatha Nagar","Ukkunagaram","Venkojipalem","Waltair","Yarada"
        ],
        "Bheemunipatnam": [
            "Bheemunipatnam","Anandapuram","Bowluvada","Butchayyapeta",
            "Cheedikada","Chodavaram","Duvvada","Gambheeram","Kommadi",
            "Kondakarla","Madugula","Munagapaka","Nakkapalle","Narsipatnam",
            "Paravada","Pendurthi","Rambilli","Rolugunta","S Rayavaram",
            "Sabbavaram","Yelamanchili"
        ],
        "Narsipatnam": [
            "Narsipatnam","Anandapuram","Atchutapuram","Bheemunipatnam",
            "Chodavaram","Cheedikada","Duvvada","Gambheeram","Kasimkota",
            "Kommadi","Kondakarla","Madugula","Makavarapalem","Munagapaka",
            "Nakkapalle","Paravada","Pendurthi","Rambilli","Rolugunta",
            "S Rayavaram","Sabbavaram","Yelamanchili"
        ],
        "Paderu": [
            "Paderu","Ananthagiri","Araku","Araku Valley","Bowluvada",
            "Butchayyapeta","Cheedikada","Chintapalle","Dumbriguda",
            "G Madugula","Gudem","Hukumpeta","Koyyuru","Lambasingi",
            "Munchingiputtu","Munugapaka","Narsipatnam","Nathavaram",
            "Ravikamatham","Rolugunta","S Kota","Sabbavaram","Saravakota",
            "Seethampeta","Yellamanchili"
        ],
        "Atchutapuram": [
            "Atchutapuram","Anandapuram","Bheemunipatnam","Chodavaram",
            "Cheedikada","Duvvada","Gambheeram","Kasimkota","Kommadi",
            "Kondakarla","Madugula","Makavarapalem","Munagapaka","Nakkapalle",
            "Narsipatnam","Paravada","Pendurthi","Rambilli","Rolugunta",
            "S Rayavaram","Sabbavaram","Yelamanchili"
        ],
    },
    "East Godavari": {
        "Kakinada": [
            "Kakinada","Bommuru","Gandhinagar","Jagannaickpur","Kakinada Port",
            "Kotipalli","Peddapuram","Ramanayyapeta","Samalkota","Suryaraopet",
            "Gollaprolu","Prathipadu","Rowthulapudi","U Kothapalli","Yeleswaram"
        ],
        "Rajamahendravaram": [
            "Rajamahendravaram","Biccavolu","Dowleswaram","Gokavaram",
            "Kadiyam","Korukonda","Kovvur","Lalacheruvu","Nidadavole",
            "Pattiseema","Polavaram","Rajanagaram","Tadepalligudem",
            "Venkatanarasimharajuvaripalem"
        ],
        "Peddapuram": [
            "Peddapuram","Anaparthy","Gollaprolu","Kakinada","Prathipadu",
            "Ramachandrapuram","Rayavaram","Rowthulapudi","Samalkota",
            "Sankhavaram","Tuni","U Kothapalli","Yeleswaram"
        ],
        "Tuni": [
            "Tuni","Anaparthy","Gollaprolu","Kakinada","Peddapuram",
            "Prathipadu","Ramachandrapuram","Rayavaram","Rowthulapudi",
            "Samalkota","Sankhavaram","Thondangi","U Kothapalli","Yeleswaram"
        ],
        "Mandapeta": [
            "Mandapeta","Ainavilli","Alamuru","Allavaram","Ambajipeta",
            "Anaparthy","Biccavolu","Gollaprolu","Kakinada","Kothapeta",
            "Malkipuram","Peddapuram","Prathipadu","Ramachandrapuram",
            "Samalkota","Tallarevu","Tuni"
        ],
        "Ramachandrapuram": [
            "Ramachandrapuram","Ainavilli","Alamuru","Allavaram","Ambajipeta",
            "Anaparthy","Biccavolu","Gollaprolu","Kakinada","Kajuluru",
            "Kothapeta","Malkipuram","Peddapuram","Samalkota","Sitanagaram",
            "Tallarevu","Tuni","U Kothapalli"
        ],
        "Amalapuram": [
            "Amalapuram","Allavaram","Avidi","I Polavaram","Katrenikona",
            "Mamidikududru","Malikipuram","Mummidivaram","Ravulapalem",
            "Razole","Sakhinetipalle","Uppalaguptam"
        ],
    },
    "West Godavari": {
        "Eluru": [
            "Eluru","Akiveedu","Attili","Bhimavaram","Buttayagudem",
            "Chintalapudi","Denduluru","Dwaraka Tirumala","Ganapavaram",
            "Gopalapuram","Irrinki","Jangareddygudem","Kamavarapu Kota",
            "Kovvali","Lingapalem","Nallajerla","Narsapur","Palakoderu",
            "Palla","Pedavegi","Penugonda","Pentapadu","Polavaram",
            "Tadepalligudem","Tanuku","Undi","Unguturu","Veeravasaram"
        ],
        "Bhimavaram": [
            "Bhimavaram","Achanta","Akiveedu","Attili","Bantumilli",
            "Chintalapudi","Denduluru","Dwaraka Tirumala","Ganapavaram",
            "Gopalapuram","Iragavaram","Jangareddygudem","Kamavarapu Kota",
            "Kovvali","Lalpur","Lingapalem","Nallajerla","Narsapur",
            "Palakoderu","Palla","Pedavegi","Penugonda","Pentapadu",
            "Polavaram","Tadepalligudem","Tanuku","Undi","Unguturu","Tumuluru"
        ],
        "Tadepalligudem": [
            "Tadepalligudem","Akiveedu","Attili","Bhimavaram","Buttayagudem",
            "Chintalapudi","Denduluru","Dwaraka Tirumala","Ganapavaram",
            "Gopalapuram","Jangareddygudem","Kamavarapu Kota","Kovvali",
            "Lalpur","Lingapalem","Nallajerla","Narsapur","Palakoderu",
            "Palla","Pedavegi","Penugonda","Pentapadu","Polavaram",
            "Tanuku","Undi","Unguturu","Veeravasaram","Tumuluru"
        ],
        "Jangareddygudem": [
            "Jangareddygudem","Akiveedu","Buttayagudem","Chintalapudi",
            "Denduluru","Dwaraka Tirumala","Ganapavaram","Gopalapuram",
            "Kamavarapu Kota","Kovvali","Lingapalem","Nallajerla","Narsapur",
            "Palakoderu","Pedavegi","Penugonda","Pentapadu","Polavaram",
            "Tadepalligudem","Tanuku","Undi","Unguturu","Veeravasaram"
        ],
        "Narsapur": [
            "Narsapur","Achanta","Akiveedu","Attili","Bhimavaram",
            "Chintalapudi","Denduluru","Dwaraka Tirumala","Ganapavaram",
            "Gopalapuram","Iragavaram","Jangareddygudem","Kamavarapu Kota",
            "Kovvali","Lalpur","Lingapalem","Nallajerla","Palakoderu",
            "Palla","Pedavegi","Penugonda","Pentapadu","Polavaram",
            "Tadepalligudem","Tanuku","Undi","Unguturu","Veeravasaram"
        ],
        "Tanuku": [
            "Tanuku","Achanta","Akiveedu","Attili","Bhimavaram",
            "Chintalapudi","Denduluru","Dwaraka Tirumala","Ganapavaram",
            "Gopalapuram","Iragavaram","Jangareddygudem","Kamavarapu Kota",
            "Kovvali","Lalpur","Lingapalem","Nallajerla","Narsapur",
            "Palakoderu","Palla","Pedavegi","Penugonda","Pentapadu",
            "Polavaram","Tadepalligudem","Undi","Unguturu","Tumuluru","Veeravasaram"
        ],
    },
    "YSR Kadapa": {
        "Kadapa": [
            "Kadapa","Badvel","B Koduru","Chakrayapet","Chapadu","Chitvel",
            "Duvvur","Galiveedu","Jammalamadugu","Kalasapadu","Kamalapuram",
            "Khajipet","Lingala","Mydukur","Muddanur","Obulampalle",
            "Penagalur","Proddatur","Pullampet","Rajampet","Ramapuram",
            "Rayachoti","Sambepalle","Sidhout","Simhadripuram","T Sundupalle",
            "Thondur","Vemula","Vempalli","Yerraguntla"
        ],
        "Proddatur": [
            "Proddatur","Badvel","Chakrayapet","Chapadu","Chitvel","Duvvur",
            "Galiveedu","Jammalamadugu","Kalasapadu","Kamalapuram","Khajipet",
            "Lingala","Mydukur","Muddanur","Obulampalle","Penagalur",
            "Pullampet","Rajampet","Ramapuram","Rayachoti","Sambepalle",
            "Sidhout","Simhadripuram","T Sundupalle","Thondur","Vemula","Yerraguntla"
        ],
        "Rajampet": [
            "Rajampet","Badvel","B Koduru","Chakrayapet","Chapadu","Chitvel",
            "Duvvur","Galiveedu","Jammalamadugu","Kalasapadu","Kamalapuram",
            "Khajipet","Lingala","Mydukur","Muddanur","Obulampalle",
            "Penagalur","Proddatur","Pullampet","Ramapuram","Rayachoti",
            "Sambepalle","Sidhout","Simhadripuram","T Sundupalle","Thondur","Vemula"
        ],
        "Rayachoti": [
            "Rayachoti","Badvel","B Koduru","Chakrayapet","Chapadu","Chitvel",
            "Duvvur","Galiveedu","Jammalamadugu","Kalasapadu","Kamalapuram",
            "Khajipet","Lingala","Mydukur","Muddanur","Obulampalle",
            "Penagalur","Proddatur","Pullampet","Rajampet","Ramapuram",
            "Sambepalle","Sidhout","Simhadripuram","T Sundupalle","Thondur","Vemula"
        ],
        "Jammalamadugu": [
            "Jammalamadugu","Badvel","B Koduru","Chakrayapet","Chapadu",
            "Chitvel","Duvvur","Galiveedu","Kalasapadu","Kamalapuram",
            "Khajipet","Lingala","Mydukur","Muddanur","Obulampalle",
            "Penagalur","Proddatur","Pullampet","Rajampet","Ramapuram",
            "Rayachoti","Sambepalle","Sidhout","Simhadripuram","T Sundupalle",
            "Thondur","Vemula","Yerraguntla"
        ],
    },
    "Srikakulam": {
        "Srikakulam": [
            "Srikakulam","Amadalavalasa","Burja","Etcherla","Gara",
            "Hiramandalam","Ichapuram","Jalumuru","Kanchili","Kaviti",
            "Kotabommali","Kothuru","Laveru","Mandasa","Meliaputti",
            "Narasannapeta","Palakonda","Pathapatnam","Polaki","Rajam",
            "Ranastalam","Saravakota","Sarubujjili","Sompeta","Tekkali","Vangara"
        ],
        "Tekkali": [
            "Tekkali","Amadalavalasa","Burja","Etcherla","Gara","Hiramandalam",
            "Ichapuram","Jalumuru","Kanchili","Kaviti","Kotabommali","Kothuru",
            "Laveru","Mandasa","Meliaputti","Narasannapeta","Palakonda",
            "Pathapatnam","Polaki","Rajam","Ranastalam","Saravakota",
            "Sarubujjili","Sompeta","Vangara"
        ],
        "Palakonda": [
            "Palakonda","Amadalavalasa","Burja","Etcherla","Gara","Hiramandalam",
            "Ichapuram","Jalumuru","Kanchili","Kaviti","Kotabommali","Kothuru",
            "Laveru","Mandasa","Meliaputti","Narasannapeta","Pathapatnam",
            "Polaki","Rajam","Ranastalam","Saravakota","Sarubujjili",
            "Sompeta","Tekkali","Vangara"
        ],
        "Narasannapeta": [
            "Narasannapeta","Amadalavalasa","Burja","Etcherla","Gara",
            "Hiramandalam","Ichapuram","Jalumuru","Kanchili","Kaviti",
            "Kotabommali","Kothuru","Laveru","Mandasa","Meliaputti",
            "Palakonda","Pathapatnam","Polaki","Rajam","Ranastalam",
            "Saravakota","Sarubujjili","Sompeta","Tekkali","Vangara"
        ],
    },
    "Vizianagaram": {
        "Vizianagaram": [
            "Vizianagaram","Badangi","Balijipeta","Bheemunipatnam","Bobbili",
            "Cheepurupalli","Dattirajeru","Gajapathinagaram","Gantyada",
            "Garugubilli","Jami","Komarada","Kurupam","Lakkavarapukota",
            "Makkuva","Mentada","Merakamudidam","Nellimarla","Pachipenta",
            "Palavalasa","Parvathipuram","Poosapatirega","Pusapatirega",
            "Rajam","Ramabhadrapuram","Salur","Srungavarapukota",
            "Vepada","Zindapenta"
        ],
        "Bobbili": [
            "Bobbili","Badangi","Balijipeta","Cheepurupalli","Dattirajeru",
            "Gajapathinagaram","Gantyada","Garugubilli","Jami","Komarada",
            "Kurupam","Lakkavarapukota","Makkuva","Mentada","Merakamudidam",
            "Nellimarla","Pachipenta","Palavalasa","Parvathipuram",
            "Poosapatirega","Rajam","Ramabhadrapuram","Salur",
            "Srungavarapukota","Vepada","Vizianagaram","Zindapenta"
        ],
        "Salur": [
            "Salur","Badangi","Balijipeta","Bobbili","Cheepurupalli",
            "Dattirajeru","Gajapathinagaram","Gantyada","Garugubilli",
            "Jami","Komarada","Kurupam","Lakkavarapukota","Makkuva",
            "Mentada","Merakamudidam","Nellimarla","Pachipenta","Palavalasa",
            "Parvathipuram","Poosapatirega","Rajam","Ramabhadrapuram",
            "Srungavarapukota","Vepada","Vizianagaram","Zindapenta"
        ],
        "Parvathipuram": [
            "Parvathipuram","Badangi","Balijipeta","Bobbili","Cheepurupalli",
            "Dattirajeru","Gajapathinagaram","Gantyada","Garugubilli",
            "Jami","Komarada","Kurupam","Lakkavarapukota","Makkuva",
            "Mentada","Merakamudidam","Nellimarla","Pachipenta","Palavalasa",
            "Poosapatirega","Rajam","Ramabhadrapuram","Salur",
            "Srungavarapukota","Vepada","Vizianagaram","Zindapenta"
        ],
    },
    "Sri Potti Sriramulu Nellore": {
        "Nellore": [
            "Nellore","Allur","Ananthasagaram","Atmakur","Bogole",
            "Buchireddipalem","Chejerla","Chillakur","Dakkili","Duttalur",
            "Gudluru","Indukurpet","Jaladanki","Kavali","Kodavalur",
            "Kovur","Manubolu","Muthukur","Naidupeta","Ojili",
            "Podalakur","Rapur","Seetharamapuram","Sullurpeta","Tada",
            "Udayagiri","Venkatachalam","Vidavalur","Vinjamur"
        ],
        "Gudur": [
            "Gudur","Allur","Atmakur","Bogole","Buchireddipalem","Chejerla",
            "Chillakur","Dakkili","Duttalur","Gudluru","Indukurpet",
            "Jaladanki","Kavali","Kodavalur","Kovur","Manubolu","Muthukur",
            "Naidupeta","Ojili","Podalakur","Rapur","Seetharamapuram",
            "Sullurpeta","Tada","Udayagiri","Venkatachalam","Vidavalur","Vinjamur"
        ],
        "Kavali": [
            "Kavali","Allur","Atmakur","Bogole","Buchireddipalem","Chejerla",
            "Chillakur","Dakkili","Duttalur","Gudluru","Gudur","Indukurpet",
            "Jaladanki","Kodavalur","Kovur","Manubolu","Muthukur","Naidupeta",
            "Ojili","Podalakur","Rapur","Seetharamapuram","Sullurpeta",
            "Tada","Udayagiri","Venkatachalam","Vidavalur","Vinjamur"
        ],
        "Naidupeta": [
            "Naidupeta","Allur","Atmakur","Bogole","Buchireddipalem","Chejerla",
            "Chillakur","Dakkili","Duttalur","Gudluru","Gudur","Indukurpet",
            "Jaladanki","Kavali","Kodavalur","Kovur","Manubolu","Muthukur",
            "Ojili","Podalakur","Rapur","Seetharamapuram","Sullurpeta",
            "Tada","Udayagiri","Venkatachalam","Vidavalur","Vinjamur"
        ],
    },
}

# Populate database
conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON")
conn.execute("""
    CREATE TABLE IF NOT EXISTS ap_villages (
        village_id INTEGER PRIMARY KEY AUTOINCREMENT,
        district   TEXT NOT NULL,
        mandal     TEXT NOT NULL,
        village    TEXT NOT NULL
    )
""")
conn.execute("""
    CREATE INDEX IF NOT EXISTS idx_villages_search
    ON ap_villages (district, mandal, village)
""")

# Clear old data and repopulate
conn.execute("DELETE FROM ap_villages")

rows = []
for district, mandals in AP_DATA.items():
    for mandal, villages in mandals.items():
        for village in villages:
            rows.append((district, mandal, village))

conn.executemany(
    "INSERT INTO ap_villages (district, mandal, village) VALUES (?, ?, ?)",
    rows
)
conn.commit()

total = conn.execute("SELECT COUNT(*) FROM ap_villages").fetchone()[0]
districts = conn.execute(
    "SELECT COUNT(DISTINCT district) FROM ap_villages").fetchone()[0]
mandals = conn.execute(
    "SELECT COUNT(DISTINCT mandal) FROM ap_villages").fetchone()[0]
conn.close()

print(f"✅ Database populated!")
print(f"   Districts : {districts}")
print(f"   Mandals   : {mandals}")
print(f"   Villages  : {total}")
print("\nYour app can now search all AP villages instantly!")