import re

COMMON_WEAK_KEYWORDS = {
    "just", "like", "good", "pretty", "really", "yes", "well", "one",
    "dont", "didnt", "im", "ive", "know", "got", "get", "make", "made",
    "say", "said", "want", "going", "still", "much", "many", "also",
    "let", "lets", "time", "love", "people", "person", "persons",
    "man", "men", "woman", "women", "thank", "thanks", "used",
    "better", "does", "did", "come", "go", "thing", "things",
    "stuff", "yeah", "okay", "ok", "lol", "haha", "cnn",
    "away", "thought", "buffoon"
}

PROFILES = {
    "general": {
        "fallback_label": "General Reactions & Miscellaneous Comments",
        "profile_hints": set(),
        "rules": []
    },

    "politics_news": {
        "fallback_label": "General Political Discussion",
        "profile_hints": {
            "trump", "obama", "president", "donald", "white house",
            "russia", "putin", "democrat", "democrats", "republican", "republicans",
            "election", "voting", "senate", "congress", "government", "policy",
            "state", "court", "media", "news", "press", "administration"
        },
        "rules": [
            {
                "label": "Trump, Obama & Presidency",
                "terms": {"trump", "obama", "president", "donald", "white house", "administration"},
                "min_hits": 2
            },
            {
                "label": "Russia, Putin & Geopolitics",
                "terms": {"russia", "russian", "putin", "kremlin", "moscow", "ukraine"},
                "min_hits": 1
            },
            {
                "label": "US Party Politics & Elections",
                "terms": {"democrat", "democrats", "republican", "republicans", "election", "voting", "party", "senate", "congress"},
                "min_hits": 2
            },
            {
                "label": "Government, Law & Public Policy",
                "terms": {"government", "policy", "state", "law", "court", "constitution", "federal"},
                "min_hits": 2
            },
            {
                "label": "Media, Journalism & News Credibility",
                "terms": {"media", "news", "press", "journalism", "coverage", "fake news"},
                "min_hits": 2
            }
        ]
    },

    "public_safety": {
        "fallback_label": "General Public Safety Discussion",
        "profile_hints": {
            "gun", "guns", "nra", "weapon", "weapons", "shooting",
            "mass shooting", "columbine", "sandy hook", "newtown",
            "aurora", "police", "crime", "criminal", "violence",
            "terror", "terrorism", "isis", "attack", "bomb"
        },
        "rules": [
            {
                "label": "Guns, Mass Shootings & Public Safety",
                "terms": {"gun", "guns", "nra", "weapon", "weapons", "shooting", "mass shooting", "columbine", "sandy hook", "newtown", "aurora"},
                "min_hits": 2
            },
            {
                "label": "Policing, Crime & Justice",
                "terms": {"police", "cop", "crime", "criminal", "justice", "court", "arrest", "prison"},
                "min_hits": 2
            },
            {
                "label": "Terrorism, Violence & Security",
                "terms": {"terror", "terrorism", "isis", "attack", "bomb", "violence", "security", "war"},
                "min_hits": 2
            }
        ]
    },

    "health_medical": {
        "fallback_label": "General Health Discussion",
        "profile_hints": {
            "health", "care", "insurance", "obamacare", "medical",
            "doctor", "hospital", "disease", "vaccine", "virus",
            "patients", "treatment", "mental health"
        },
        "rules": [
            {
                "label": "Healthcare Policy & Insurance",
                "terms": {"health", "care", "insurance", "obamacare", "medical", "affordable care"},
                "min_hits": 2
            },
            {
                "label": "Disease, Treatment & Public Health",
                "terms": {"doctor", "hospital", "disease", "vaccine", "virus", "patients", "treatment", "mental health"},
                "min_hits": 2
            }
        ]
    },

    "business_finance": {
        "fallback_label": "General Business & Economic Discussion",
        "profile_hints": {
            "tax", "taxes", "economy", "economic", "money", "market",
            "stock", "bank", "finance", "trade", "budget", "inflation",
            "jobs", "salary", "wages", "employment", "company", "office"
        },
        "rules": [
            {
                "label": "Taxes, Economy & Public Finance",
                "terms": {"tax", "taxes", "economy", "economic", "budget", "inflation", "revenue", "money"},
                "min_hits": 2
            },
            {
                "label": "Jobs, Labor & Workplace Issues",
                "terms": {"jobs", "employment", "workers", "wages", "salary", "company", "office"},
                "min_hits": 2
            },
            {
                "label": "Markets, Banking & Finance",
                "terms": {"market", "stock", "bank", "finance", "trade", "investment", "dollar"},
                "min_hits": 2
            }
        ]
    },

    "technology": {
        "fallback_label": "General Technology Discussion",
        "profile_hints": {
            "ai", "model", "machine learning", "algorithm", "software",
            "app", "application", "platform", "update", "version",
            "device", "phone", "iphone", "android", "samsung", "laptop",
            "battery", "data", "privacy", "security", "hack", "password",
            "cloud", "server", "api", "bug", "feature"
        },
        "rules": [
            {
                "label": "AI, Models & Automation",
                "terms": {"ai", "model", "machine learning", "algorithm", "automation", "chatgpt"},
                "min_hits": 2
            },
            {
                "label": "Software, Platforms & Apps",
                "terms": {"software", "app", "application", "platform", "update", "version", "bug", "feature", "api"},
                "min_hits": 2
            },
            {
                "label": "Technology Products & Devices",
                "terms": {"device", "phone", "iphone", "android", "samsung", "laptop", "battery", "hardware"},
                "min_hits": 2
            },
            {
                "label": "Data, Privacy & Cybersecurity",
                "terms": {"data", "privacy", "security", "hack", "breach", "password", "cyber"},
                "min_hits": 2
            }
        ]
    },

    "customer_feedback": {
        "fallback_label": "General Customer Feedback",
        "profile_hints": {
            "support", "service", "customer", "complaint", "response",
            "order", "delivery", "shipping", "refund", "return",
            "package", "damaged", "quality", "broken", "issue", "problem",
            "experience", "review"
        },
        "rules": [
            {
                "label": "Customer Service, Support & Complaints",
                "terms": {"support", "service", "customer", "complaint", "response", "agent"},
                "min_hits": 2
            },
            {
                "label": "Orders, Delivery & Refunds",
                "terms": {"order", "delivery", "shipping", "refund", "return", "package", "arrived", "damaged"},
                "min_hits": 2
            },
            {
                "label": "Product Quality & User Experience",
                "terms": {"quality", "broken", "issue", "problem", "experience", "review", "defect", "works"},
                "min_hits": 2
            }
        ]
    },

    "sports": {
        "fallback_label": "General Sports Discussion",
        "profile_hints": {
            "team", "match", "game", "league", "tournament", "season",
            "player", "coach", "goal", "score", "win", "won", "lost",
            "football", "soccer", "basketball", "nba", "nfl", "mlb"
        },
        "rules": [
            {
                "label": "Teams, Matches & Competition",
                "terms": {"team", "match", "game", "league", "tournament", "season", "football", "soccer", "basketball"},
                "min_hits": 2
            },
            {
                "label": "Players, Coaching & Performance",
                "terms": {"player", "coach", "goal", "score", "win", "won", "lost", "performance", "training"},
                "min_hits": 2
            }
        ]
    },

    "education": {
        "fallback_label": "General Education Discussion",
        "profile_hints": {
            "school", "student", "teacher", "class", "university",
            "college", "exam", "education", "learning", "course",
            "curriculum", "grade", "homework"
        },
        "rules": [
            {
                "label": "Schools, Universities & Students",
                "terms": {"school", "student", "teacher", "class", "university", "college", "campus"},
                "min_hits": 2
            },
            {
                "label": "Exams, Learning & Curriculum",
                "terms": {"exam", "education", "learning", "course", "curriculum", "grade", "homework", "test"},
                "min_hits": 2
            }
        ]
    },

    "society_culture": {
        "fallback_label": "General Social & Cultural Discussion",
        "profile_hints": {
            "women", "gender", "hillary", "female",
            "god", "jesus", "religion", "church", "lord", "faith",
            "race", "racism", "racial", "black", "white", "justice",
            "muslim", "muslims", "israel", "syria", "middle east", "war"
        },
        "rules": [
            {
                "label": "Women, Gender & Society",
                "terms": {"women", "woman", "gender", "hillary", "female"},
                "min_hits": 1
            },
            {
                "label": "Religion, Faith & Public Discourse",
                "terms": {"god", "jesus", "religion", "church", "lord", "faith", "bible"},
                "min_hits": 2
            },
            {
                "label": "Race, Identity & Social Justice",
                "terms": {"race", "racism", "racial", "black", "white", "justice", "identity"},
                "min_hits": 2
            },
            {
                "label": "Middle East, War & Identity Politics",
                "terms": {"muslim", "muslims", "israel", "isis", "syria", "middle east", "war"},
                "min_hits": 2
            }
        ]
    },

    "media_entertainment": {
        "fallback_label": "General Media & Entertainment Discussion",
        "profile_hints": {
            "movie", "movies", "show", "music", "song", "actor",
            "celebrity", "netflix", "episode", "tv", "media", "press",
            "journalism", "coverage"
        },
        "rules": [
            {
                "label": "Media, Journalism & Coverage",
                "terms": {"media", "press", "journalism", "coverage", "news", "fox"},
                "min_hits": 2
            },
            {
                "label": "Movies, Shows & Entertainment",
                "terms": {"movie", "movies", "show", "music", "song", "actor", "celebrity", "netflix", "episode", "tv"},
                "min_hits": 2
            }
        ]
    }
}


def normalize_representation(rep):
    if isinstance(rep, list):
        return [str(x).strip().lower() for x in rep if str(x).strip()]

    if isinstance(rep, str):
        cleaned = rep.strip("[]")
        parts = [x.strip().strip("'").strip('"').lower() for x in cleaned.split(",")]
        return [x for x in parts if x]

    return []


def normalize_docs(rep_docs):
    if isinstance(rep_docs, list):
        return " ".join(str(x).lower() for x in rep_docs if str(x).strip())

    if isinstance(rep_docs, str):
        return rep_docs.lower()

    return ""


def tokenize_text(text):
    return re.findall(r"[a-z]+", text.lower())


def has_phrase(text, phrase):
    return re.search(r"\b" + re.escape(phrase.lower()) + r"\b", text.lower()) is not None


def clean_keywords(rep):
    words = normalize_representation(rep)

    cleaned = []
    seen = set()

    for w in words:
        w = w.replace("_", " ").strip().lower()

        if not w:
            continue
        if len(w) <= 2:
            continue
        if w in COMMON_WEAK_KEYWORDS:
            continue
        if w in seen:
            continue

        seen.add(w)
        cleaned.append(w)

    return cleaned


def count_term_hits(words, docs_text, terms):
    word_set = set(words)
    doc_token_set = set(tokenize_text(docs_text))
    hits = 0

    for term in terms:
        term = term.lower().strip()

        if not term:
            continue

        if " " in term:
            if term in word_set or has_phrase(docs_text, term):
                hits += 1
        else:
            if term in word_set or term in doc_token_set:
                hits += 1

    return hits


def detect_best_profile(words, docs_text):
    best_profile = "general"
    best_score = 0

    for profile_name, config in PROFILES.items():
        if profile_name == "general":
            continue

        score = count_term_hits(words, docs_text, config["profile_hints"])

        if score > best_score:
            best_score = score
            best_profile = profile_name

    # لا نعتمد profile متخصصًا إلا إذا وجدنا إشارتين على الأقل
    if best_score < 2:
        return "general"

    return best_profile


def infer_label_from_profile(profile_name, words, docs_text):
    config = PROFILES[profile_name]

    for rule in config["rules"]:
        hits = count_term_hits(words, docs_text, rule["terms"])
        if hits >= rule["min_hits"]:
            return rule["label"]

    return config["fallback_label"]


def prepare_topic_display(topic_info):
    data = topic_info.copy()

    display_names = []
    cleaned_keywords_col = []
    detected_profiles = []

    for _, row in data.iterrows():
        topic_id = int(row["Topic"])

        if topic_id == -1:
            display_names.append("Noise / Unassigned Comments")
            cleaned_keywords_col.append([])
            detected_profiles.append("noise")
            continue

        cleaned_keywords = clean_keywords(row.get("Representation", []))
        docs_text = normalize_docs(row.get("Representative_Docs", []))

        profile_name = detect_best_profile(cleaned_keywords, docs_text)
        label = infer_label_from_profile(profile_name, cleaned_keywords, docs_text)

        display_names.append(label)
        cleaned_keywords_col.append(cleaned_keywords)
        detected_profiles.append(profile_name)

    data["DetectedProfile"] = detected_profiles
    data["CustomName"] = display_names
    data["CleanKeywords"] = cleaned_keywords_col
    return data
