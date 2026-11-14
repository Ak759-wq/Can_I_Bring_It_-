"""Verbatim text snapshots of official pages that block automated fetches from
some networks (bot protection or geo-blocking). Text was copied from each
official page on 14 Nov 2026. During ingest, a live fetch is always tried
first; these are used only when the live fetch fails, so every answer is still
traceable to the official URL.
"""

SNAPSHOTS = {
    "https://u.ae/en/information-and-services/visiting-and-exploring-the-uae/Tourist-services-and-information/Customs-clearance": (
        "Passengers with more than AED 60,000 in cash or an equivalent amount in other currencies, financial instruments, "
        "precious metals or valuable stones, must declare at the customs. Find out which items are exempt from customs duty, "
        "and which are banned or restricted.\n\n"
        "Money declaration. Passengers travelling out of or entering the UAE with more than AED 60,000 in cash or an amount "
        "equivalent to this in other currencies, financial instruments, precious metals or valuable stones, must declare it to "
        "Federal Authority for Identity, Citizenship, Customs & Ports Security (ICP) as per the Rulebook. You can declare the "
        "money through the official website or the Afseh app available on Google Play and App Store. For passengers under the "
        "age of 18, the amount in their possession will be added to the permitted limit of their parent/guardian or accompanier."
    ),
    "https://www.dubaicustoms.gov.ae/en/eServices/ServicesForIndividuals/ViewCustomsProcedure/Pages/DeclaringMoneyProcedure.aspx": (
        "Cash declaration procedure: All passengers arriving in the country must declare cash or other bearer monetary "
        "instruments in their possession in an aggregate amount exceeding AED 60,000 or its equivalent in foreign currencies "
        "and travelers cheques, by filling out the designated declaration form in accordance with the cash declaration "
        "regulation in force in the UAE. Passengers under the age of 18 years old shall not be allowed to bring in cash "
        "exceeding the aforementioned permissible limit and any excess cash in their possession shall be added to the allowed "
        "limit of their parent/guardian should they be accompanied minors."
    ),
    "https://www.cbic.gov.in/resources/htdocs-cbec/Customs_Clearance_of_Passengers_at_a_Glance_2.pdf": (
        "The Duty-Free Allowances available to various categories of passengers are as under: "
        "1. Indian resident or a tourist of Indian origin or a foreigner with a valid visa, other than tourist visa, excluding "
        "infants, arriving through any mode other than land: Rs. 75,000. "
        "2. Tourists of foreign origin, excluding infants, arriving through any mode other than land: Rs. 25,000. "
        "3. All passengers arriving through land: NIL. "
        "4. Indian resident or a tourist of Indian origin who has been residing abroad for over one year, arriving through any "
        "mode other than land: Jewelry: Female - upto weight of 40 grams. Passenger other than a female – upto weight of 20 grams. "
        "5. All passengers arriving through any mode other than land: Alcohol liquor or wine: 2 litres."
    ),
    "https://www.cbic.gov.in/resources/htdocs-cbec/frequently_asked_questions_faqs.pdf": (
        "Q1. Who can avail the benefits of Baggage? The benefits of baggage under the Customs Baggage Rules, 2026 may be availed "
        "by the following categories of passengers arriving in India: 1. Resident; 2. Tourist of Indian origin; 3. Foreigner "
        "with a valid visa, other than tourist visa; 4. Tourist of foreign origin; 5. Crew members.\n\n"
        "Q2. What are the duty-free entitlements available for passengers? Any passenger arriving in India, including an "
        "infant, is allowed duty-free clearance of used personal effects. In addition, passengers, excluding an infant are "
        "allowed duty free clearance of articles, excluding the articles of Annexure-I up to the value prescribed: Resident "
        "75,000; Tourist of Indian origin 75,000; Foreigner with a valid visa, other than tourist visa 75,000; arriving "
        "through any mode other than land."
    ),
    "https://www.cbic.gov.in/resources/htdocs-cbec/travellerguide_atithi.pdf": (
        "Used personal effects allowed duty-free. Additional duty-free allowance: ₹75,000 – Residents, tourists of Indian "
        "origin, foreigners with valid visa (other than tourist visa); ₹25,000 – Tourists of foreign origin; ₹2,500 – Crew "
        "members; No allowance for passengers arriving via land borders. One new laptop/notepad duty-free (18+). "
        "A resident/tourist of Indian origin stayed abroad for >1 year may bring: Females: Up to 40 gm duty-free; Others: Up "
        "to 20 gm duty-free. Red Channel: for passengers carrying dutiable goods, high-value items, currency beyond limits, "
        "pets, or items requiring declaration."
    ),
    "https://www.abf.gov.au/entering-and-leaving-australia/duty-free": (
        "You can bring most personal items into Australia in your accompanied baggage, free from duty and tax. This includes "
        "items such as clothing, footwear, articles for personal hygiene and grooming (excluding fur and perfume concentrates). "
        "Duty free concessions do not apply to commercial goods. If you are aged 18 years or over, you can bring up to AUD900 "
        "worth of general goods into Australia duty free. If you are under 18 years of age the limit is AUD450. If you are a "
        "crew member, the limit is AUD450."
    ),
}
