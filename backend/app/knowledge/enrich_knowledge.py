import json
from pathlib import Path

KNOWLEDGE_PATH = Path("backend/app/knowledge/reference_ranges.json")

with open(KNOWLEDGE_PATH, "r", encoding="utf-8") as f:
    knowledge = json.load(f)

# Comprehensive symptoms and display names dictionary
METADATA = {
    "hemoglobin": {
        "display_name": "Hemoglobin (Hb)",
        "extra_aliases": ["haemoglobin", "haemoglob", "hemoglob", "haemoglobin (hb)", "hb (haemoglobin)", "haemoglobin blood"],
        "low_symptoms": [
            "Persistent fatigue, weakness, or lethargy",
            "Shortness of breath with minimal exertion or stair climbing",
            "Pale or yellowish skin, lips, or nail beds",
            "Cold hands and feet",
            "Dizziness, lightheadedness, or feeling faint",
            "Fast or irregular heartbeat (palpitations)",
            "Frequent headaches"
        ],
        "high_symptoms": [
            "Flushed or reddened facial complexion",
            "Dizziness, vertigo, or lightheadedness",
            "Headaches and blurred vision",
            "Pruritus (itching), particularly after a warm shower or bath",
            "Feeling of fullness in the head or ears",
            "Fatigue from sluggish circulation (hyperviscosity)"
        ]
    },
    "rbc": {
        "display_name": "Red Blood Cell Count (RBC)",
        "extra_aliases": ["rbc", "red cell count", "total rbc", "erythrocyte count"],
        "low_symptoms": [
            "Generalized weakness and physical fatigue",
            "Shortness of breath on exertion",
            "Pale skin or conjunctiva",
            "Cold sensitivity in fingers and toes",
            "Tachycardia (racing heart) during daily activities"
        ],
        "high_symptoms": [
            "Headaches and visual disturbances",
            "Dizziness or ringing in ears (tinnitus)",
            "Skin itching, particularly following hot baths",
            "Reddish or purplish tint to skin and gums",
            "Joint pain or swelling in toes/fingers"
        ]
    },
    "wbc": {
        "display_name": "Total Leukocyte Count (WBC)",
        "extra_aliases": ["total leuco", "total leucocyte", "total leucocyte count", "total leucocytes", "leucocyte count", "leukocyte count", "total wbc", "tlc"],
        "low_symptoms": [
            "Recurrent or persistent low-grade fevers",
            "Frequent infections (colds, sinus, respiratory, or urinary)",
            "Mouth ulcers or swollen, tender gums",
            "Sore throat that lingers",
            "Chills, night sweats, and slow healing of minor skin wounds"
        ],
        "high_symptoms": [
            "High fever, shaking chills, and systemic sweating",
            "Generalized body aches, malaise, and exhaustion",
            "Localized heat, redness, swelling, or pain (infection sites)",
            "Cough, sore throat, or chest congestion",
            "Unexplained weight loss or night drenching sweats"
        ]
    },
    "platelets": {
        "display_name": "Platelet Count",
        "extra_aliases": ["plt", "platelets count", "total platelet count", "thrombocyte count"],
        "low_symptoms": [
            "Easy or spontaneous bruising without obvious trauma",
            "Petechiae (tiny pinpoint red or purple spots on legs/arms)",
            "Frequent or prolonged nosebleeds (epistaxis)",
            "Bleeding gums after gentle brushing",
            "Prolonged bleeding from minor cuts or dental work",
            "Unusually heavy or prolonged menstrual bleeding"
        ],
        "high_symptoms": [
            "Persistent dull headaches",
            "Dizziness, lightheadedness, or feeling unsteady",
            "Numbness, tingling, or burning in hands and feet",
            "Transient vision changes or blurry spots",
            "Localized redness, warmth, or throbbing in calves/arms"
        ]
    },
    "hematocrit": {
        "display_name": "Packed Cell Volume (PCV / Hematocrit)",
        "extra_aliases": ["pcv", "hct", "packed cell volume", "haematocrit"],
        "low_symptoms": [
            "Chronic fatigue, lack of stamina, and poor concentration",
            "Shortness of breath during normal daily tasks",
            "Pale appearance of skin, tongue, and inner eyelids",
            "Dizziness when standing up abruptly"
        ],
        "high_symptoms": [
            "Headaches, facial flushing, and mental sluggishness",
            "Generalized generalized itching after warm bathing",
            "Dizziness, vertigo, and visual blurring",
            "Elevated blood pressure or pounding sensation in temples"
        ]
    },
    "mcv": {
        "display_name": "Mean Corpuscular Volume (MCV)",
        "extra_aliases": ["mean cell volume", "m.c.v."],
        "low_symptoms": [
            "Symptoms of microcytic anemia: fatigue, brittle nails, pallor, cold intolerance"
        ],
        "high_symptoms": [
            "Symptoms of macrocytic anemia: numbness or pins-and-needles in toes/fingers, brain fog, fatigue"
        ]
    },
    "mch": {
        "display_name": "Mean Corpuscular Hemoglobin (MCH)",
        "extra_aliases": ["m.c.h."],
        "low_symptoms": ["Fatigue, pallor, cold extremities, shortness of breath on exertion"],
        "high_symptoms": ["Tiredness, tingling in extremities, mental fog, balance changes"]
    },
    "mchc": {
        "display_name": "Mean Corpuscular Hemoglobin Concentration (MCHC)",
        "extra_aliases": ["m.c.h.c."],
        "low_symptoms": ["Chronic fatigue, paleness, dizziness, reduced exercise tolerance"],
        "high_symptoms": ["Fatigue, jaundice (yellowish skin/eyes), dark-colored urine, gallstone discomfort"]
    },
    "rdw": {
        "display_name": "Red Cell Distribution Width (RDW)",
        "extra_aliases": ["rdw-cv", "rdw cv", "rdw-sd", "rdw sd"],
        "low_symptoms": ["Rarely clinically symptomatic on its own; reflects uniform red blood cell sizing"],
        "high_symptoms": ["Fatigue, breathlessness on exertion, pale skin, weakness (reflects mixed red cell sizes)"]
    },
    "neutrophils": {
        "display_name": "Neutrophils (%)",
        "extra_aliases": ["neutrophil", "neut", "polymorphs", "segs", "segmented neutrophils", "neutrophils percent"],
        "low_symptoms": [
            "Frequent recurrent infections (oral thrush, boils, skin infections)",
            "Fever without an obvious source",
            "Painful mouth sores and tender gums",
            "General feeling of malaise and chills"
        ],
        "high_symptoms": [
            "Acute fever, chills, and shaking",
            "Localized inflammatory pain (swollen throat, skin abscess, cough with phlegm)",
            "Fatigue, body aches, and sweats"
        ]
    },
    "lymphocytes": {
        "display_name": "Lymphocytes (%)",
        "extra_aliases": ["lymphocyte", "lymph", "lymphs", "lymphocyte percent"],
        "low_symptoms": [
            "Frequent respiratory or viral infections",
            "Prolonged recovery from simple illnesses",
            "General fatigue and muscle weakness"
        ],
        "high_symptoms": [
            "Swollen lymph nodes in neck, armpits, or groin",
            "Low-grade fever, sore throat, or body aches (recent viral illness)",
            "Fatigue, mild night sweats, and loss of appetite"
        ]
    },
    "eosinophils": {
        "display_name": "Eosinophils (%)",
        "extra_aliases": ["eosinophil", "eos", "eosinophil percent"],
        "low_symptoms": [
            "Typically asymptomatic; may accompany acute bacterial stress or steroid use"
        ],
        "high_symptoms": [
            "Allergic symptoms: hives, skin itching, eczema, or rash",
            "Nasal congestion, sneezing, runny nose, or watery eyes",
            "Wheezing, shortness of breath, or asthma flares",
            "Digestive discomfort, abdominal cramps, or bloating"
        ]
    },
    "monocytes": {
        "display_name": "Monocytes (%)",
        "extra_aliases": ["monocyte", "mono", "monocyte percent"],
        "low_symptoms": [
            "Increased vulnerability to fungal or bacterial infections, fatigue"
        ],
        "high_symptoms": [
            "Fatigue, joint aches, and low-grade recurrent fever",
            "Chronic inflammation symptoms: malaise, swollen lymph nodes",
            "Night sweats and unexplained weight loss"
        ]
    },
    "basophils": {
        "display_name": "Basophils (%)",
        "extra_aliases": ["basophil", "baso", "basophil percent"],
        "low_symptoms": [
            "Generally produces no noticeable direct symptoms"
        ],
        "high_symptoms": [
            "Intense skin itching (pruritus), hives, or flushing",
            "Nasal allergies, runny nose, or asthma symptoms",
            "Fatigue, night sweats, or unexplained weight changes"
        ]
    },
    "fasting_glucose": {
        "display_name": "Fasting Blood Glucose",
        "extra_aliases": ["fbs", "fasting blood sugar", "fasting glucose", "glucose fasting", "blood sugar fasting"],
        "low_symptoms": [
            "Shakiness, trembling, or sudden tremors in hands",
            "Cold, clammy sweating and pale skin",
            "Heart palpitations or rapid pulse",
            "Intense sudden hunger, dizziness, and confusion",
            "Anxiety, irritability, or lightheadedness"
        ],
        "high_symptoms": [
            "Polydipsia (constant, unquenchable thirst)",
            "Polyuria (frequent urination, especially at night)",
            "Blurred or fluctuating vision",
            "Dry mouth and itchy skin",
            "Fatigue, sluggishness, and slow wound healing",
            "Unexplained weight loss despite normal appetite"
        ]
    },
    "hba1c": {
        "display_name": "Glycated Hemoglobin (HbA1c)",
        "extra_aliases": ["glycated hemoglobin", "glycosylated hemoglobin", "a1c"],
        "low_symptoms": [
            "Shakiness, cold sweat, hunger pangs, dizziness (episodes of hypoglycemia)"
        ],
        "high_symptoms": [
            "Excessive thirst, frequent urination, dry mouth",
            "Chronic fatigue, lethargy, and poor energy levels",
            "Blurred vision, numbness or tingling in feet/toes",
            "Recurrent infections or skin boils"
        ]
    },
    "creatinine": {
        "display_name": "Serum Creatinine",
        "extra_aliases": ["sr creatinine", "s creatinine", "creatinine serum", "blood creatinine"],
        "low_symptoms": [
            "Muscle weakness, reduced muscle mass, fatigue"
        ],
        "high_symptoms": [
            "Puffiness or swelling (edema) in ankles, feet, or around eyes",
            "Fatigue, brain fog, and low energy",
            "Decreased urine output, foamy urine, or darker urine",
            "Nausea, metallic taste in mouth, or loss of appetite",
            "Shortness of breath or itching skin"
        ]
    },
    "blood_urea_nitrogen": {
        "display_name": "Blood Urea Nitrogen (BUN)",
        "extra_aliases": ["bun", "urea", "blood urea", "serum urea"],
        "low_symptoms": ["Often asymptomatic; may accompany low-protein diets or overhydration"],
        "high_symptoms": [
            "Dehydration symptoms: dry mouth, thirst, fatigue",
            "Nausea, reduced appetite, and lethargy",
            "Puffiness in lower legs and face"
        ]
    },
    "egfr": {
        "display_name": "Estimated GFR (eGFR)",
        "extra_aliases": ["gfr", "estimated glomerular filtration rate"],
        "low_symptoms": [
            "Fluid retention, swelling in legs or face, fatigue",
            "Changes in urination frequency or foamy appearance",
            "Nausea, metallic taste, itchy dry skin"
        ],
        "high_symptoms": [
            "Generally healthy normal or hyperfiltration (pregnancy, early diabetes)"
        ]
    },
    "sodium": {
        "display_name": "Serum Sodium",
        "extra_aliases": ["na", "serum na", "sodium na"],
        "low_symptoms": [
            "Nausea, vomiting, headache, and confusion",
            "Muscle cramps, spasms, or profound weakness",
            "Restlessness, drowsiness, and unsteady balance"
        ],
        "high_symptoms": [
            "Extreme thirst and intense dry mouth",
            "Restlessness, agitation, or confusion",
            "Muscle twitching or stiffness",
            "Lethargy and weakness"
        ]
    },
    "potassium": {
        "display_name": "Serum Potassium",
        "extra_aliases": ["k", "serum k", "potassium k"],
        "low_symptoms": [
            "Muscle weakness, twitching, or painful calf cramps",
            "Constipation, bloating, or abdominal cramping",
            "Heart palpitations, fluttering, or irregular rhythm",
            "Extreme fatigue and tingling sensations"
        ],
        "high_symptoms": [
            "Palpitations, slow heart rate, or chest discomfort",
            "Muscle weakness or feeling heavy in the limbs",
            "Numbness, tingling in fingers and lips",
            "Nausea, shortness of breath, and dizziness"
        ]
    },
    "calcium": {
        "display_name": "Serum Calcium",
        "extra_aliases": ["total calcium", "serum ca", "ca"],
        "low_symptoms": [
            "Muscle cramps, spasms, or twitches in face and hands",
            "Numbness and tingling around mouth and fingertips",
            "Dry skin, brittle nails, and muscle aching"
        ],
        "high_symptoms": [
            "Excessive thirst, frequent urination, and constipation",
            "Bone or joint pain, abdominal cramps, and nausea",
            "Lethargy, confusion, memory fog, and fatigue"
        ]
    },
    "total_cholesterol": {
        "display_name": "Total Cholesterol",
        "extra_aliases": ["cholesterol", "sr cholesterol", "serum cholesterol"],
        "low_symptoms": ["Usually asymptomatic; very low levels may correlate with malnutrition or hyperthyroidism"],
        "high_symptoms": [
            "Usually asymptomatic in early stages (silent risk factor)",
            "Yellowish deposits around eyes (xanthelasma) in severe chronic elevations",
            "Chest pressure, shortness of breath during exertion (if coronary arteries involved)"
        ]
    },
    "hdl_cholesterol": {
        "display_name": "HDL Cholesterol (Good)",
        "extra_aliases": ["hdl", "high density lipoprotein", "hdl-c"],
        "low_symptoms": [
            "Silent risk factor; no direct physical symptoms but increases cardiovascular risk"
        ],
        "high_symptoms": [
            "Favorable cardiovascular marker; generally asymptomatic and protective"
        ]
    },
    "ldl_cholesterol": {
        "display_name": "LDL Cholesterol (Bad)",
        "extra_aliases": ["ldl", "low density lipoprotein", "ldl-c"],
        "low_symptoms": ["Generally asymptomatic and cardioprotective"],
        "high_symptoms": [
            "Typically silent without noticeable day-to-day symptoms",
            "Contributes to plaque buildup in arteries over time"
        ]
    },
    "triglycerides": {
        "display_name": "Triglycerides",
        "extra_aliases": ["tg", "serum triglycerides", "triglyceride"],
        "low_symptoms": ["Asymptomatic; associated with low-fat diet or hyperthyroidism"],
        "high_symptoms": [
            "Usually asymptomatic; severe elevations (>500 mg/dL) can trigger severe abdominal pain (pancreatitis)",
            "Fatigue, sluggishness, and fatty deposits on skin (eruptive xanthomas)"
        ]
    },
    "alt": {
        "display_name": "Alanine Aminotransferase (ALT / SGPT)",
        "extra_aliases": ["sgpt", "alt (sgpt)", "alanine transaminase", "sgpt alt"],
        "low_symptoms": ["Normal physiological finding; no adverse symptoms"],
        "high_symptoms": [
            "Persistent fatigue, weakness, and loss of appetite",
            "Nausea, mild abdominal bloating, or upper right quadrant discomfort",
            "Jaundice (yellowish tint to eyes or skin)",
            "Dark tea-colored urine and pale stools"
        ]
    },
    "ast": {
        "display_name": "Aspartate Aminotransferase (AST / SGOT)",
        "extra_aliases": ["sgot", "ast (sgot)", "aspartate transaminase", "sgot ast"],
        "low_symptoms": ["Normal finding; no clinical symptoms"],
        "high_symptoms": [
            "Fatigue, generalized malaise, nausea",
            "Discomfort under the right ribcage",
            "Dark urine, yellowing of eyes/skin, easy bruising"
        ]
    },
    "total_bilirubin": {
        "display_name": "Total Bilirubin",
        "extra_aliases": ["bilirubin", "bilirubin total", "sr bilirubin", "serum bilirubin"],
        "low_symptoms": ["Typically benign; no symptoms"],
        "high_symptoms": [
            "Jaundice: distinct yellowing of the sclera (white of eyes) and skin",
            "Dark, tea-colored urine",
            "Pale, clay-colored bowel movements",
            "Pruritus (generalized skin itching)",
            "Nausea, loss of appetite, and upper right abdominal tenderness"
        ]
    },
    "tsh": {
        "display_name": "Thyroid Stimulating Hormone (TSH)",
        "extra_aliases": ["thyroid stimulating hormone", "ultrasensitive tsh"],
        "low_symptoms": [
            "Hyperthyroidism symptoms: unintended weight loss despite increased appetite",
            "Heat intolerance, excessive sweating, and warm moist skin",
            "Rapid or pounding heart rate (palpitations)",
            "Nervousness, anxiety, hand tremors, and insomnia",
            "Frequent bowel movements or diarrhea"
        ],
        "high_symptoms": [
            "Hypothyroidism symptoms: persistent fatigue, sluggishness, and brain fog",
            "Unexplained weight gain or difficulty losing weight",
            "Cold intolerance, feeling chilled when others are comfortable",
            "Dry skin, hair thinning, and brittle nails",
            "Constipation, muscle aches, and puffy face"
        ]
    },
    "crp": {
        "display_name": "C-Reactive Protein (CRP)",
        "extra_aliases": ["c reactive protein", "hs-crp", "hscrp"],
        "low_symptoms": ["Optimal baseline level; indicates absence of significant systemic inflammation"],
        "high_symptoms": [
            "Fever, night chills, and generalized fatigue",
            "Muscle and joint stiffness, aching, or swelling",
            "Localized warmth, pain, or redness at an injury or infection site"
        ]
    },
    "esr": {
        "display_name": "Erythrocyte Sedimentation Rate (ESR)",
        "extra_aliases": ["sed rate", "erythrocyte sed rate"],
        "low_symptoms": ["Generally normal and indicates absence of acute inflammatory activity"],
        "high_symptoms": [
            "Persistent fatigue, low-grade fever, and malaise",
            "Joint pain, morning stiffness, or headache",
            "Unexplained weight loss and generalized body aches"
        ]
    },
    "vitamin_d": {
        "display_name": "Vitamin D (25-OH)",
        "extra_aliases": ["25-oh vitamin d", "vit d", "vitamin d total", "25 hydroxy vitamin d"],
        "low_symptoms": [
            "Dull bone pain, lower back discomfort, and muscle weakness",
            "Frequent colds, respiratory infections, or slow healing",
            "Chronic fatigue, low mood, and morning muscle stiffness"
        ],
        "high_symptoms": [
            "Nausea, vomiting, poor appetite, and constipation",
            "Frequent urination, excessive thirst, and dehydration",
            "Muscle weakness, joint aches, and confusion"
        ]
    },
    "vitamin_b12": {
        "display_name": "Vitamin B12",
        "extra_aliases": ["vit b12", "cyanocobalamin", "serum cobalamin"],
        "low_symptoms": [
            "Numbness, tingling, or 'pins and needles' in hands and feet",
            "Chronic fatigue, weakness, and lightheadedness",
            "Brain fog, memory lapses, and mood fluctuations",
            "Sore, smooth, or bright red tongue (glossitis)",
            "Unsteadiness or difficulty walking in dark"
        ],
        "high_symptoms": [
            "Usually asymptomatic (water-soluble vitamin excreted in urine); may accompany liver inflammation"
        ]
    },
    "ferritin": {
        "display_name": "Serum Ferritin",
        "extra_aliases": ["sr ferritin", "ferritin serum"],
        "low_symptoms": [
            "Deep fatigue, exhaustion, and shortness of breath with simple tasks",
            "Pale skin, cold hands, brittle spoon-shaped nails, and hair shedding",
            "Restless legs syndrome (urge to move legs at night)",
            "Brain fog and poor exercise endurance"
        ],
        "high_symptoms": [
            "Joint pain (especially in knuckles and knees)",
            "Abdominal pain, fatigue, and weakness",
            "Unexplained darkening or bronze tint to the skin"
        ]
    },
    "uric_acid": {
        "display_name": "Serum Uric Acid",
        "extra_aliases": ["sr uric acid", "serum urate", "urate"],
        "low_symptoms": ["Usually benign and produces no symptoms"],
        "high_symptoms": [
            "Sudden, severe, throbbing joint pain (typically big toe, ankle, or knee)",
            "Intense redness, swelling, and extreme sensitivity to touch in affected joint",
            "Flank or lower back pain (if uric acid kidney stones develop)"
        ]
    }
}

# Add dedicated absolute leukocyte parameters
ABSOLUTE_PARAMS = {
    "absolute_eosinophil_count": {
        "display_name": "Absolute Eosinophil Count (AEC)",
        "aliases": [
            "absolute eosinophil count", "absolute eosinophils", "absolute ec",
            "abs eosinophils", "abs eosinophil", "abs eos", "aec", "aec count"
        ],
        "category": "Complete Blood Count (CBC)",
        "unit": "/cumm",
        "default_range": [20.0, 500.0],
        "description": "The absolute number of eosinophils per microliter of blood, reflecting specialized immune activity against allergens and parasites.",
        "low_explanation": "Your absolute eosinophil count is low. This is commonly seen with acute bacterial stress, elevated corticosteroid levels, or vigorous exercise, and is rarely a cause for concern on its own.",
        "high_explanation": "Your absolute eosinophil count is elevated (eosinophilia). Common causes include allergic conditions (asthma, eczema, hay fever), parasitic infections, drug reactions, or inflammatory diseases.",
        "questions_for_doctor": [
            "Could seasonal allergies, eczema, or asthma explain this elevated eosinophil count?",
            "Are any recent medications or dietary changes contributing to this?"
        ],
        "low_symptoms": [
            "Rarely produces any noticeable physical symptoms"
        ],
        "high_symptoms": [
            "Allergic symptoms: hives, skin itching, eczema, or rash",
            "Wheezing, shortness of breath, or asthma symptoms",
            "Nasal congestion, sneezing, runny nose, or watery eyes",
            "Abdominal cramps or digestive sensitivity"
        ]
    },
    "absolute_monocyte_count": {
        "display_name": "Absolute Monocyte Count (AMC)",
        "aliases": [
            "absolute monocyte count", "absolute monocytes", "absolute m",
            "abs monocytes", "abs monocyte", "abs mono", "amc", "amc count"
        ],
        "category": "Complete Blood Count (CBC)",
        "unit": "/cumm",
        "default_range": [200.0, 950.0],
        "description": "The absolute count of circulating monocytes, large phagocytic immune cells that clear pathogens and cellular debris.",
        "low_explanation": "Your absolute monocyte count is below reference interval (monocytopenia). This may be seen with temporary bone marrow suppression or severe acute infections.",
        "high_explanation": "Your absolute monocyte count is elevated (monocytosis). This frequently indicates recovery from an infection, chronic inflammatory disease, or autoimmune activity.",
        "questions_for_doctor": [
            "Does this reflect recovery from a recent bacterial or viral illness?",
            "Should we monitor this on a follow-up CBC panel?"
        ],
        "low_symptoms": [
            "Increased susceptibility to bacterial or fungal infections, fatigue"
        ],
        "high_symptoms": [
            "Fatigue, joint stiffness, and low-grade lingering fever",
            "Swollen lymph nodes in neck or armpits",
            "Night sweats and muscle aches"
        ]
    },
    "absolute_neutrophil_count": {
        "display_name": "Absolute Neutrophil Count (ANC)",
        "aliases": [
            "absolute neutrophil count", "absolute neutrophils", "absolute n",
            "abs neutrophils", "abs neutrophil", "abs neut", "anc", "anc count"
        ],
        "category": "Complete Blood Count (CBC)",
        "unit": "/cumm",
        "default_range": [2000.0, 7500.0],
        "description": "The exact count of circulating neutrophils, the first-responder white blood cells defending against bacterial infections.",
        "low_explanation": "Your absolute neutrophil count is below reference interval (neutropenia). A lower ANC means reduced protection against bacterial infections. Causes include viral infections, autoimmune conditions, or certain medications.",
        "high_explanation": "Your absolute neutrophil count is elevated (neutrophilia). This is a hallmark response to bacterial infection, acute physical inflammation, stress, or tissue healing.",
        "questions_for_doctor": [
            "Could a recent infection, injury, or stress be responsible for this neutrophil elevation?",
            "Do I need any precautions or retesting for my white blood cell levels?"
        ],
        "low_symptoms": [
            "Vulnerability to bacterial infections (skin boils, sore throat, dental pain)",
            "Unexplained fever, chills, and painful mouth sores",
            "Slow healing of minor cuts"
        ],
        "high_symptoms": [
            "Acute fever, chills, and body aches",
            "Localized heat, swelling, redness, or pain",
            "Sweating, fatigue, and productive cough"
        ]
    },
    "absolute_lymphocyte_count": {
        "display_name": "Absolute Lymphocyte Count (ALC)",
        "aliases": [
            "absolute lymphocyte count", "absolute lymphocytes", "absolute l",
            "abs lymphocytes", "abs lymphocyte", "abs lymph", "alc", "alc count"
        ],
        "category": "Complete Blood Count (CBC)",
        "unit": "/cumm",
        "default_range": [1000.0, 4000.0],
        "description": "The total number of circulating lymphocytes (T cells, B cells, and NK cells), vital for viral defense and immunological memory.",
        "low_explanation": "Your absolute lymphocyte count is below reference range (lymphocytopenia). This can occur during acute infections, corticosteroid therapy, or immune disorders.",
        "high_explanation": "Your absolute lymphocyte count is elevated (lymphocytosis). Elevated lymphocytes are most commonly a natural immune response to a viral infection (such as mono, flu, or COVID).",
        "questions_for_doctor": [
            "Does this elevated lymphocyte count indicate a recent or active viral infection?",
            "When should I repeat this test to check if levels have normalized?"
        ],
        "low_symptoms": [
            "Frequent colds, respiratory infections, or prolonged recovery times",
            "General fatigue and muscle weakness"
        ],
        "high_symptoms": [
            "Swollen, tender lymph nodes in neck or armpits",
            "Low-grade fever, sore throat, or body aches",
            "Fatigue and mild night sweats"
        ]
    },
    "absolute_basophil_count": {
        "display_name": "Absolute Basophil Count (ABC)",
        "aliases": [
            "absolute basophil count", "absolute basophils", "absolute b",
            "abs basophils", "abs basophil", "abs baso", "abc", "abc count"
        ],
        "category": "Complete Blood Count (CBC)",
        "unit": "/cumm",
        "default_range": [0.0, 100.0],
        "description": "The absolute count of circulating basophils, which release histamine during allergic reactions and inflammatory responses.",
        "low_explanation": "Your absolute basophil count is within the standard low or zero range, which is completely normal physiologically.",
        "high_explanation": "Your absolute basophil count is elevated (basophilia). This can be seen in chronic allergic conditions, inflammatory bowel conditions, or certain marrow conditions.",
        "questions_for_doctor": [
            "Could ongoing allergic reactions explain this basophil finding?",
            "Should this be evaluated in tandem with other white cell subsets?"
        ],
        "low_symptoms": [
            "Produces no noticeable symptoms; clinically normal"
        ],
        "high_symptoms": [
            "Skin itching (pruritus), hives, or flushing",
            "Allergic symptoms: runny nose, watery eyes, wheezing",
            "Fatigue or feeling warm"
        ]
    }
}

# Merge metadata into knowledge
for key, meta in METADATA.items():
    if key in knowledge:
        knowledge[key]["display_name"] = meta["display_name"]
        knowledge[key]["low_symptoms"] = meta["low_symptoms"]
        knowledge[key]["high_symptoms"] = meta["high_symptoms"]
        for extra in meta.get("extra_aliases", []):
            if extra not in knowledge[key]["aliases"]:
                knowledge[key]["aliases"].append(extra)

# Add new absolute params
for key, data in ABSOLUTE_PARAMS.items():
    knowledge[key] = data

# For any parameter without a display_name, generate one
for key, item in knowledge.items():
    if "display_name" not in item:
        item["display_name"] = key.replace("_", " ").title()
    if "low_symptoms" not in item:
        item["low_symptoms"] = [f"Symptoms associated with low {item['display_name']}; discuss with your doctor."]
    if "high_symptoms" not in item:
        item["high_symptoms"] = [f"Symptoms associated with elevated {item['display_name']}; discuss with your doctor."]

with open(KNOWLEDGE_PATH, "w", encoding="utf-8") as f:
    json.dump(knowledge, f, indent=2, ensure_ascii=False)

print(f"Successfully enriched reference_ranges.json with {len(knowledge)} canonical parameters, display names, and symptoms!")
