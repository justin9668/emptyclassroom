import os
from dotenv import load_dotenv

if os.getenv("RAILWAY_ENV") is None:
    load_dotenv()

REDIS_URL = os.getenv('REDIS_URL')
API_URL = os.getenv('API_URL')

REDIS_TIMEOUT = 5  # seconds
CACHE_KEY = 'classrooms:availability'
CACHE_EXPIRY = 24 * 60 * 60  # 24 hours
MIN_GAP_MINUTES = 28  # requires 30 minutes actual gap (28 + 2 minute buffer)
REFRESH_COOLDOWN_MINUTES = 30

BUILDINGS = {
    "CAS": {"code": "CAS", "name": "College of Arts & Sciences", "business_start_hour": 7, "business_end_hour": 23},
    "CGS": {"code": "CGS", "name": "College of General Studies", "business_start_hour": 7, "business_end_hour": 21.5},
}

CLASSROOMS = {
    "342": {"id": "342", "name": "116", "building_code": "CAS"},
    "344": {"id": "344", "name": "201", "building_code": "CAS"},
    "345": {"id": "345", "name": "203", "building_code": "CAS"},
    "346": {"id": "346", "name": "208", "building_code": "CAS"},
    "349": {"id": "349", "name": "211", "building_code": "CAS"},
    "350": {"id": "350", "name": "212", "building_code": "CAS"},
    "351": {"id": "351", "name": "213", "building_code": "CAS"},
    "352": {"id": "352", "name": "214", "building_code": "CAS"},
    "353": {"id": "353", "name": "216", "building_code": "CAS"},
    "354": {"id": "354", "name": "218", "building_code": "CAS"},
    "355": {"id": "355", "name": "220", "building_code": "CAS"},
    "357": {"id": "357", "name": "222", "building_code": "CAS"},
    "358": {"id": "358", "name": "223", "building_code": "CAS"},
    "359": {"id": "359", "name": "224", "building_code": "CAS"},
    "360": {"id": "360", "name": "225", "building_code": "CAS"},
    "361": {"id": "361", "name": "226", "building_code": "CAS"},
    "362": {"id": "362", "name": "227", "building_code": "CAS"},
    "363": {"id": "363", "name": "228", "building_code": "CAS"},
    "364": {"id": "364", "name": "229", "building_code": "CAS"},
    "365": {"id": "365", "name": "233", "building_code": "CAS"},
    "366": {"id": "366", "name": "235", "building_code": "CAS"},
    "367": {"id": "367", "name": "237", "building_code": "CAS"},
    "372": {"id": "372", "name": "313", "building_code": "CAS"},
    "374": {"id": "374", "name": "315", "building_code": "CAS"},
    "382": {"id": "382", "name": "324", "building_code": "CAS"},
    "384": {"id": "384", "name": "326", "building_code": "CAS"},
    "406": {"id": "406", "name": "114A", "building_code": "CAS"},
    "407": {"id": "407", "name": "114B", "building_code": "CAS"},
    "409": {"id": "409", "name": "204A", "building_code": "CAS"},
    "411": {"id": "411", "name": "522", "building_code": "CAS"},
    "417": {"id": "417", "name": "204B", "building_code": "CAS"},
    "434": {"id": "434", "name": "B06A", "building_code": "CAS"},
    "435": {"id": "435", "name": "B06B", "building_code": "CAS"},
    "439": {"id": "439", "name": "B12", "building_code": "CAS"},
    "443": {"id": "443", "name": "B20", "building_code": "CAS"},
    "450": {"id": "450", "name": "B36", "building_code": "CAS"},
    "461": {"id": "461", "name": "Tsai", "building_code": "CAS"},
    "719": {"id": "719", "name": "129", "building_code": "CGS"},
    "723": {"id": "723", "name": "311", "building_code": "CGS"},
    "724": {"id": "724", "name": "313", "building_code": "CGS"},
    "725": {"id": "725", "name": "315", "building_code": "CGS"},
    "726": {"id": "726", "name": "321", "building_code": "CGS"},
    "727": {"id": "727", "name": "323", "building_code": "CGS"},
    "735": {"id": "735", "name": "421", "building_code": "CGS"},
    "736": {"id": "736", "name": "423", "building_code": "CGS"},
    "738": {"id": "738", "name": "505", "building_code": "CGS"},
    "741": {"id": "741", "name": "511", "building_code": "CGS"},
    "742": {"id": "742", "name": "515", "building_code": "CGS"},
    "743": {"id": "743", "name": "521", "building_code": "CGS"},
    "744": {"id": "744", "name": "523", "building_code": "CGS"},
    "745": {"id": "745", "name": "525", "building_code": "CGS"},
    "746": {"id": "746", "name": "527", "building_code": "CGS"},
    "780": {"id": "780", "name": "111A", "building_code": "CGS"},
    "781": {"id": "781", "name": "111B", "building_code": "CGS"},
    "782": {"id": "782", "name": "117A", "building_code": "CGS"},
    "783": {"id": "783", "name": "117B", "building_code": "CGS"},
    "1056": {"id": "1056", "name": "113", "building_code": "CGS"},
    "1058": {"id": "1058", "name": "115", "building_code": "CGS"},
    "1060": {"id": "1060", "name": "121", "building_code": "CGS"},
    "1062": {"id": "1062", "name": "123", "building_code": "CGS"},
    "4330": {"id": "4330", "name": "B18", "building_code": "CAS"},
    "4520": {"id": "4520", "name": "312", "building_code": "CAS"},
    "4521": {"id": "4521", "name": "314", "building_code": "CAS"},
    "4522": {"id": "4522", "name": "316", "building_code": "CAS"},
    "4523": {"id": "4523", "name": "318", "building_code": "CAS"},
    "4524": {"id": "4524", "name": "320", "building_code": "CAS"},
    "4525": {"id": "4525", "name": "310", "building_code": "CAS"},
    "5802": {"id": "5802", "name": "B25A", "building_code": "CAS"},
    "5803": {"id": "5803", "name": "B25B", "building_code": "CAS"},
    "5804": {"id": "5804", "name": "B27", "building_code": "CAS"},
    "5805": {"id": "5805", "name": "323A", "building_code": "CAS"},
    "5806": {"id": "5806", "name": "323B", "building_code": "CAS"},
    "5807": {"id": "5807", "name": "325", "building_code": "CAS"},
    "5808": {"id": "5808", "name": "322", "building_code": "CAS"},
    "5809": {"id": "5809", "name": "424", "building_code": "CAS"},
    "5810": {"id": "5810", "name": "426", "building_code": "CAS"},
    "5812": {"id": "5812", "name": "427", "building_code": "CAS"}
}