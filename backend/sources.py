"""Allow-list of official sources the RAG index is built from.

Every chunk the model may answer from comes from one of these pages.
`countries` decides which routes a page is relevant to. "ANY" means it applies
to every route (aviation safety rules such as batteries and liquids).
"""

SOURCES = [
    # ---- Aviation safety (applies to every route) ----
    {"name": "FAA – Batteries Carried by Airline Passengers", "url": "https://www.faa.gov/hazmat/packsafe/resources/airline-passengers-batteries", "countries": ["ANY", "USA"]},
    {"name": "IATA – Lithium Battery Guidance for Passengers", "url": "https://www.iata.org/contentassets/6fea26dd84d24b26a7a1fd5788561d6e/passenger-lithium-battery.pdf", "countries": ["ANY"]},
    {"name": "TSA – Liquids, Aerosols and Gels Rule", "url": "https://www.tsa.gov/travel/security-screening/liquids-aerosols-gels-rule", "countries": ["ANY", "USA"]},
    {"name": "GOV.UK – Hand luggage restrictions", "url": "https://www.gov.uk/hand-luggage-restrictions/print", "countries": ["ANY", "UK"]},

    # ---- UAE ----
    {"name": "Dubai Customs – Passenger Customs Guide", "url": "https://www.dubaicustoms.gov.ae/en/OpenData/Publications/PassengerCustomsGuide.pdf", "countries": ["UAE"]},
    {"name": "Dubai Customs – Declaring Money Procedure", "url": "https://www.dubaicustoms.gov.ae/en/eServices/ServicesForIndividuals/ViewCustomsProcedure/Pages/DeclaringMoneyProcedure.aspx", "countries": ["UAE"]},
    {"name": "u.ae – Customs clearance (UAE Government Portal)", "url": "https://u.ae/en/information-and-services/visiting-and-exploring-the-uae/Tourist-services-and-information/Customs-clearance", "countries": ["UAE"]},

    # ---- Japan ----
    {"name": "Japan Customs – Duty-Free Allowance (FAQ 7105)", "url": "https://www.customs.go.jp/english/c-answer_e/keitaibetsuso/7105_e.htm", "countries": ["Japan"]},
    {"name": "Japan Customs – Passenger Customs Procedures", "url": "https://www.customs.go.jp/english/summary/passenger.htm", "countries": ["Japan"]},

    # ---- India ----
    {"name": "CBIC – Customs Clearance of Passengers at a Glance", "url": "https://www.cbic.gov.in/resources/htdocs-cbec/Customs_Clearance_of_Passengers_at_a_Glance_2.pdf", "countries": ["India"]},
    {"name": "CBIC – Baggage FAQs (Customs Baggage Rules, 2026)", "url": "https://www.cbic.gov.in/resources/htdocs-cbec/frequently_asked_questions_faqs.pdf", "countries": ["India"]},
    {"name": "CBIC – Guide for International Travellers", "url": "https://www.cbic.gov.in/resources/htdocs-cbec/travellerguide_atithi.pdf", "countries": ["India"]},

    # ---- UK ----
    {"name": "GOV.UK – Bringing goods into the UK (arrivals from outside the EU)", "url": "https://www.gov.uk/duty-free-goods/print", "countries": ["UK"]},
    {"name": "GOV.UK – Taking cash in and out of Great Britain", "url": "https://www.gov.uk/bringing-cash-into-uk/print", "countries": ["UK"]},

    # ---- USA ----
    {"name": "CBP – Prohibited and Restricted Items", "url": "https://www.cbp.gov/travel/us-citizens/know-before-you-go/prohibited-and-restricted-items", "countries": ["USA"]},

    # ---- Singapore ----
    {"name": "Singapore Customs – Duty-Free Concession and GST Import Relief", "url": "https://www.customs.gov.sg/at-customs/arriving-in-singapore/duty-free-concession-gst-relief", "countries": ["Singapore"]},

    # ---- Australia ----
    {"name": "ABF – Duty free", "url": "https://www.abf.gov.au/entering-and-leaving-australia/duty-free", "countries": ["Australia"]},

    # ---- Germany ----
    {"name": "Zoll – Travellers' allowances (entering from non-EU)", "url": "https://www.zoll.de/EN/Private-individuals/Travel/Entering-Germany/Duties-and-taxes/Travellers-allowances/travellers-allowances.html", "countries": ["Germany"]},
    {"name": "Zoll – Restrictions when entering Germany", "url": "https://www.zoll.de/EN/Private-individuals/Travel/Entering-Germany/Restrictions/restrictions_node.html", "countries": ["Germany"]},

    # ---- Canada ----
    {"name": "CBSA – Declaring goods, cash and allowances when entering Canada", "url": "https://www.cbsa-asfc.gc.ca/travel-voyage/declare-eng.html", "countries": ["Canada"]},

    # ---- Singapore prohibited goods (CAAS AIP, official) ----
    {"name": "CAAS Singapore AIP GEN 1.3 – Customs: prohibited goods and allowances", "url": "https://aim-sg.caas.gov.sg/aim-content/uploads/aip/03-SEP-2026/AIP-1/2026-09-03-000000/html/eAIP/SG-GEN-1.3-en-GB.html", "countries": ["Singapore"]},
]

ALLOWED_DOMAINS = sorted({s["url"].split("/")[2].removeprefix("www.") for s in SOURCES})
