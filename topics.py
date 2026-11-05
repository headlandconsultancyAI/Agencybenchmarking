"""Topic model and firm list for the peer agency LinkedIn board.

Edit freely. Each theme is a list of match terms:
  - terms match whole words, case-insensitive ("ai" catches "AI", not "said")
  - a trailing * matches any ending ("appoint*" catches appointed, appointment)
  - "a|b" is shorthand for two alternatives
  - spaces make a phrase ("private equity")
Keep terms specific. A term that matches a third of the corpus flattens the signal.
"""

# The firms on the board. Anything else in a scrape (reposted individuals,
# trade press, sub-pages) is dropped. CONSUMER firms get their own filter.
CORPORATE = [
    "APCO", "Blurred", "Brands2Life", "Brunswick Group", "Burson", "Cavendish",
    "Citypress", "Edelman", "Edmonds Elder", "FGS Global", "FTI Consulting",
    "Fight or Flight", "FleishmanHillard", "Freuds Group", "Grayling",
    "Hanbury Strategy", "Hanover Communications", "Hawthorn Advisors", "Headland",
    "Kekst CNC", "Lansons | Team Farner", "Lexington", "MHP Group",
    "Montfort Communications", "Nepean", "Portland", "Prosek Partners",
    "SEC Newgate UK", "Sodali & Co", "Teneo", "Weber Shandwick",
]
CONSUMER = ["The Romans", "Ready10", "Hope&Glory PR"]
HOME_FIRM = "Headland"   # highlighted on the board

# Broad themes for the "Trending" view. A post can carry several.
THEMES = {
    "AI and technology": ["ai", "artificial intelligence", "generative ai", "genai", "llm*", "chatgpt",
                          "openai", "agentic", "machine learning", "cyber*", "digital transformation"],
    "GEO and AI search": ["geo", "generative engine optimi*", "ai search", "ai overviews", "answer engine*",
                          "llm visibility", "ai visibility", "ai citations"],
    "Geopolitics and trade": ["geopolitic*", "geoeconomic*", "tariff*", "trade war", "sanctions", "export controls",
                              "china", "ukraine", "russia", "nato", "middle east", "iran", "gaza"],
    "UK politics and policy": ["westminster", "whitehall", "parliament", "mps", "labour", "conservatives",
                               "reform uk", "chancellor", "budget", "party conference", "devolution",
                               "downing street", "burnham", "starmer", "spending review"],
    "US politics": ["trump", "white house", "congress", "republicans", "democrats", "midterm*", "capitol hill"],
    "Brussels and the EU": ["brussels", "european commission", "european parliament", "eu presidency", "eu policy"],
    "Deals and capital markets": ["ipo*", "m&a", "merger*", "takeover*", "private equity", "capital markets",
                                  "private markets", "private credit", "listing*", "ftse", "investor relations",
                                  "restructuring", "earnings", "results season", "dealmaking"],
    "Governance and shareholders": ["corporate governance", "agm*", "proxy season", "shareholder*", "activis*",
                                    "stewardship", "remuneration", "board*room"],
    "Crisis and reputation risk": ["crisis", "crises", "disinformation", "misinformation", "issues management",
                                   "reputational risk", "reputation risk", "litigation", "cyber attack*"],
    "Climate, energy and ESG": ["climate", "net zero", "sustainab*", "esg", "energy transition", "cop30", "cop31",
                                "decarboni*", "renewable*", "nature positive", "biodiversity"],
    "Health and life sciences": ["healthcare", "health system*", "public health", "health tech", "healthtech", "nhs", "pharma*",
                                 "life sciences", "biotech", "patient*", "medical", "medicine*", "clinical"],
    "Trust and opinion research": ["trust barometer", "polling", "poll", "survey*", "public opinion", "barometer"],
    "Media and journalism": ["journalis*", "newsroom*", "editor*", "media relations", "broadcast*", "reporter*",
                             "press office", "media landscape"],
    "Talent and careers": ["intern", "interns", "internship*", "graduates", "graduate scheme*", "graduate programme*", "apprentic*", "trainee*", "we're hiring", "we are hiring",
                           "now hiring", "early careers", "join our team", "vacanc*"],
    "People moves": ["appoint*", "joins us", "joins as", "joined as", "welcome to the team", "delighted to welcome",
                     "pleased to welcome", "excited to welcome", "as a partner", "as managing director", "as head of", "promoted", "promotion*",
                     "new partner*", "new hire*"],
    "Awards and rankings": ["award*", "shortlist*", "highly commended", "ranking*", "best places to work",
                            "agency of the year", "consultancy of the year"],
    "Client wins": ["new client*", "client win*", "appointed by", "retained by", "we've won", "we have won"],
    "Diversity and social impact": ["diversity", "inclusion", "inclusive", "dei", "social mobility", "charity",
                                    "charities", "volunteer*", "pride month", "international women's day",
                                    "black history month"],
    "Sport": ["football", "golf*", "cricket", "tennis", "rugby", "world cup", "olympic*", "nfl", "formula 1",
              "marathon", "premier league"],
}

# New media themes. Same matching rules. These drive the "New media" view,
# where keyword hits are only candidates until reviewed in data/curation.json.
NEW_MEDIA = {
    "Influencers and creators": ["influencer*", "creator economy", "creator", "creators", "ugc",
                                 "user-generated", "micro-influencer*", "creator marketing", "creator-led"],
    "Social media marketing": ["social media", "socials", "paid social", "organic social", "social-first",
                               "social listening", "social strateg*", "social content", "community management",
                               "tiktok", "instagram", "reels", "threads", "bluesky", "whatsapp", "discord",
                               "youtube", "twitch", "snapchat", "twitter", "algorithm*", "short-form video",
                               "vertical video", "meme*", "viral", "going viral", "dark social"],
    "Podcasts": ["podcast*", "apple podcasts", "spotify"],
    "Email newsletters": ["newsletter*", "beehiiv", "mailing list"],
    "Reddit": ["reddit", "subreddit*"],
    "Substack": ["substack"],
}
