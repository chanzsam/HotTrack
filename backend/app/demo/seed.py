import random
import uuid
import math
from datetime import datetime, timezone, timedelta

from sqlalchemy.orm import Session

from app.models.video import Video, VideoSnapshot, Platform


YOUTUBE_CATEGORIES = {
    "1": "Film & Animation",
    "2": "Autos & Vehicles",
    "10": "Music",
    "15": "Pets & Animals",
    "17": "Sports",
    "19": "Travel & Events",
    "20": "Gaming",
    "22": "People & Blogs",
    "23": "Comedy",
    "24": "Entertainment",
    "25": "News & Politics",
    "26": "How-to & Style",
    "27": "Education",
    "28": "Science & Technology",
    "29": "Non-profits & Activism",
}

YOUTUBE_TITLE_TEMPLATES = [
    "{adj} {noun} - You Won't Believe What Happens Next",
    "Top {n} {noun} That Will {verb} Your Mind",
    "I {verb_ed} {noun} for {n} Days and This Happened",
    "The {adj} {noun} Nobody Is Talking About",
    "Why {noun} Is {verb_ing} the Internet in {year}",
    "{n} {adj} {noun} You Need to See Before You Die",
    "How I Made ${money} With {noun} in Just {n} Days",
    "This {noun} {verb_s} Everything We Know About {noun2}",
    "{noun}: The {adj} Truth They Don't Want You to Know",
    "I Tried {noun} for {n} Days - Honest Review",
    "The {adj} Way to {verb} {noun} in {year}",
    "What Happens When You {verb} {noun} for {n} Hours",
    "{n} {noun} Hacks That Actually Work",
    "I {verb_ed} the World's {adj} {noun}",
    "Is {noun} Worth the Hype? Full Breakdown",
    "How to {verb} {noun} Like a Pro in {n} Minutes",
    "The Science of Why {noun} {verb_s} So {adj}",
    "I Spent ${money} on {noun} - Was It Worth It?",
    "{noun} vs {noun2}: Which One Actually {verb_s}?",
    "The {adj} History of {noun} - Full Documentary",
    "Building {noun} From Scratch - {n} Day Challenge",
    "Every {noun} Ranked From Worst to Best",
    "What {n} Hours of {noun} Did to My Brain",
    "The Secret Behind {noun} That {noun2} Don't Want You to Know",
    "I Survived {n} Days of Only {noun}",
    "How {noun} {verb_ed} My Life Forever",
    "The Most {adj} {noun} Ever Recorded",
    "Why Everyone Is {verb_ing} About {noun} Right Now",
    "I Found the {adj} {noun} at {noun2}",
    "Can You {verb} {noun} Without {noun2}?",
    "The {adj} Reason {noun} Is Going Viral",
    "Day in the Life of a {noun} - {adj} Edition",
    "I {verb_ed} {n} {noun} and Here's What Happened",
    "The Ultimate Guide to {noun} in {year}",
    "What {noun} Looks Like in Real Life",
    "{n} Things About {noun} That Will {verb} You",
    "How {noun} Actually {verb_s} - Deep Dive",
    "I Tried the {adj} {noun} Challenge",
    "The {adj} Future of {noun} Explained",
    "Reacting to the Most {adj} {noun} on the Internet",
]

TIKTOK_TITLE_TEMPLATES = [
    "Wait for the end... {emoji} #{tag1} #{tag2}",
    "POV: You just {verb_ed} #{tag1} #{tag2}",
    "This {noun} trend is EVERYWHERE {emoji} #{tag1} #{tag2}",
    "Making the {adj} {noun} at home {emoji} #{tag1} #{tag2}",
    "Day in my life as a {noun} {emoji} #{tag1}",
    "This {noun} is {adj_er} than most {noun2} {emoji} #{tag1}",
    "Get ready with me for {noun} {emoji} #{tag1} #{tag2}",
    "I can't believe this actually {verb_ed}! #{tag1} #{tag2}",
    "The {noun} you didn't see coming {emoji} #{tag1}",
    "Trying the most {adj} {noun} {emoji} #{tag1} #{tag2}",
    "My {noun} that changed everything {emoji} #{tag1}",
    "This {noun} hits different at {n}AM {emoji} #{tag1}",
    "How I went from {n} to {n2} {noun} {emoji} #{tag1} #{tag2}",
    "The most {adj} thing you'll watch today {emoji} #{tag1}",
    "Reacting to my first {noun} from {year} {emoji} #{tag1}",
    "This {noun} trick will {verb} your mind {emoji} #{tag1} #{tag2}",
    "I tried the {adj} {noun} challenge {emoji} #{tag1}",
    "Storytime: The {adj} thing happened at {noun} {emoji} #{tag1}",
    "This {noun} is living a {adj_er} life than me {emoji} #{tag1}",
    "The {noun} nobody is talking about {emoji} #{tag1} #{tag2}",
    "Unboxing the most {adj} {noun} I've ever bought {emoji} #{tag1}",
    "What I {noun} in a day as a {noun2} {emoji} #{tag1}",
    "This trend needs to {verb} immediately {emoji} #{tag1}",
    "The {adj} {noun} I've ever {verb_ed} {emoji} #{tag1} #{tag2}",
    "My {noun} tour - {adj} edition {emoji} #{tag1}",
    "This is why you should {verb} {noun} {emoji} #{tag1} #{tag2}",
    "The {noun} {noun2} recommend {emoji} #{tag1}",
    "I {verb_ed} to {noun} in {n} days - Here's what happened {emoji} #{tag1}",
    "The most {adj} {noun} of all time {emoji} #{tag1} #{tag2}",
    "This {noun} is living rent-free in my head {emoji} #{tag1}",
]

ADJECTIVES = [
    "incredible", "amazing", "shocking", "unbelievable", "insane", "brilliant",
    "mind-blowing", "epic", "ultimate", "extreme", "secret", "hidden",
    "rare", "forgotten", "dangerous", "beautiful", "terrifying", "hilarious",
    "genius", "controversial", "unexpected", "legendary", "mysterious",
    "bizarre", "revolutionary", "explosive", "jaw-dropping", "satisfying",
    "outrageous", "magical", "surreal", "absurd", "thrilling", "iconic",
    "phenomenal", "ridiculous", "stunning", "wild", "crazy", "massive",
]

NOUNS = [
    "AI", "drone", "robot", "hack", "recipe", "workout", "challenge", "prank",
    "transformation", "experiment", "survival", "adventure", "discovery",
    "mystery", "phenomenon", "illusion", "technique", "strategy", "method",
    "secret", "conspiracy", "breakthrough", "invention", "creation", "design",
    "machine", "instrument", "structure", "destination", "creature", "ritual",
    "tradition", "culture", "lifestyle", "business", "investment", "startup",
    "gadget", "app", "software", "game", "movie", "album", "performance",
    "meal", "dessert", "cocktail", "workout", "stunt", "trick", "skill",
]

NOUNS2 = [
    "experts", "scientists", "creators", "professionals", "beginners",
    "companies", "brands", "influencers", "athletes", "artists",
    "doctors", "engineers", "chefs", "gamers", "musicians",
    "parents", "students", "entrepreneurs", "designers", "developers",
]

VERBS = [
    "change", "blow", "transform", "revolutionize", "destroy", "reveal",
    "unlock", "master", "crack", "solve", "survive", "conquer", "dominate",
    "redefine", "shatter", "ignite", "elevate", "supercharge", "disrupt",
    "reimagine", "decode", "outsmart", "overcome", "accelerate", "maximize",
]

YOUTUBE_CHANNELS = [
    "TechVision", "EpicWorld", "DailyDose", "ScienceHub", "AdventureTime",
    "CookMaster", "GameZone", "MusicVibes", "NatureWonders", "HistoryBuff",
    "FitnessPro", "TravelDiary", "ComedyCentral", "NewsNow", "ArtStudio",
    "MrBeast", "Marques Brownlee", "Veritasium", "Kurzgesagt", "Dude Perfect",
    "Mark Rober", "Linus Tech Tips", "Babish Culinary", "Yes Theory",
    "Peter McKinnon", "Ali Abdaal", "Fireship", "Two Minute Papers",
    "Corridor Crew", "Try Guys", "Good Mythical Morning", "SmarterEveryDay",
    "Tom Scott", "Vsauce", "The Try Guys", "Bon Appétit", "WIRED",
    "Vox", "Business Insider", "The Infographics Show", "Kraig Adams",
    "Sorelle Amore", "Lost LeBlanc", "Indigo Traveller", "Bald and Bankrupt",
    "Karl Watson", "Attaché", "Abroad in Japan", "Only in Japan",
]

TIKTOK_CHANNELS = [
    "dance_queen", "chef_mike", "tech_savvy", "comedy_king", "travel_lisa",
    "fitness_jay", "beauty_guru", "pet_lover", "diy_master", "foodie_anna",
    "gamer_pro", "singer_star", "artist_soul", "science_nerd", "fashion_icon",
    "khaby.lame", "charlidamelio", "bellapoarch", "addisonre", "zachking",
    "spencerx", "lorengray", "riyaz.14", "avani", "jamescharles",
    "bretmanrock", "nikitadragun", "emmachamberlain", "dixiedamelio",
    "noahbeck", "brycehall", "taylerholder", "joshrichards", "griffinjohnson",
    "couple_goals", "life_hacks_daily", "cook_with_me", "fit_life",
    "style_insider", "book_tok", "plant_parent", "diy_crafts",
]

TIKTOK_HASHTAGS = [
    "fyp", "viral", "trending", "foryou", "foryoupage", "duet", "stitch",
    "mindblown", "lifehack", "dance", "trend", "cooking", "foodtok",
    "dayinmylife", "catsoftiktok", "grwm", "experiment", "transition",
    "satisfying", "cringe", "beauty", "fitness", "storytime", "petsoftiktok",
    "hack", "unboxing", "whatieatinaday", "rant", "prank", "apartmenttour",
    "travel", "skincare", "coding", "movies", "sound", "greenscreen",
    "replytocomment", "learnontiktok", "smallbusiness", "booktok",
    "cleantok", "techtok", "gaming", "funny", "comedy", "relationship",
    "motivation", "selfcare", "morningroutine", "glowup", "outfit",
]

EMOJIS = [
    "🤯", "😱", "😂", "🔥", "✨", "💪", "🍜", "✈️", "☀️", "📈",
    "😌", "😬", "💄", "🐕", "💎", "🥗", "🛑", "😈", "🏠", "🇯🇵",
    "🧴", "💻", "🎬", "🎶", "🚀", "🎯", "💡", "🏆", "👑", "⚡",
    "🌟", "🎨", "🎵", "🍕", "🏋️", "🌍", "📸", "🎮", "🧠", "❤️",
]


def _power_law_sample(min_val, max_val, alpha=1.5):
    log_min = math.log(min_val)
    log_max = math.log(max_val)
    u = random.random()
    if random.random() < 0.15:
        log_val = log_min + (log_max - log_min) * (u ** 0.3)
    else:
        log_val = log_min + (log_max - log_min) * (u ** (1.0 / alpha))
    return min(int(math.exp(log_val)), max_val)


IRREGULAR_VERBS = {
    "change": "changed", "blow": "blew", "transform": "transformed",
    "revolutionize": "revolutionized", "destroy": "destroyed", "reveal": "revealed",
    "unlock": "unlocked", "master": "mastered", "crack": "cracked",
    "solve": "solved", "survive": "survived", "conquer": "conquered",
    "dominate": "dominated", "redefine": "redefined", "shatter": "shattered",
    "ignite": "ignited", "elevate": "elevated", "supercharge": "supercharged",
    "disrupt": "disrupted", "reimagine": "reimagined", "decode": "decoded",
    "outsmart": "outsmarted", "overcome": "overcame", "accelerate": "accelerated",
    "maximize": "maximized",
}

ADJ_COMPARATIVE = {
    "incredible": "more incredible", "amazing": "more amazing",
    "shocking": "more shocking", "unbelievable": "more unbelievable",
    "insane": "more insane", "brilliant": "more brilliant",
    "mind-blowing": "more mind-blowing", "epic": "more epic",
    "ultimate": "more ultimate", "extreme": "more extreme",
    "secret": "more secret", "hidden": "more hidden",
    "rare": "rarer", "forgotten": "more forgotten",
    "dangerous": "more dangerous", "beautiful": "more beautiful",
    "terrifying": "more terrifying", "hilarious": "more hilarious",
    "genius": "more genius", "controversial": "more controversial",
    "unexpected": "more unexpected", "legendary": "more legendary",
    "mysterious": "more mysterious", "bizarre": "more bizarre",
    "revolutionary": "more revolutionary", "explosive": "more explosive",
    "jaw-dropping": "more jaw-dropping", "satisfying": "more satisfying",
    "outrageous": "more outrageous", "magical": "more magical",
    "surreal": "more surreal", "absurd": "more absurd",
    "thrilling": "more thrilling", "iconic": "more iconic",
    "phenomenal": "more phenomenal", "ridiculous": "more ridiculous",
    "stunning": "more stunning", "wild": "wilder",
    "crazy": "crazier", "massive": "more massive",
}


def _generate_youtube_title():
    template = random.choice(YOUTUBE_TITLE_TEMPLATES)
    verb = random.choice(VERBS)
    adj = random.choice(ADJECTIVES)
    return template.format(
        adj=adj,
        adj_er=ADJ_COMPARATIVE.get(adj, "more " + adj),
        noun=random.choice(NOUNS),
        noun2=random.choice(NOUNS2),
        verb=verb,
        verb_s=verb + "s",
        verb_ed=IRREGULAR_VERBS.get(verb, verb + "ed"),
        verb_ing=verb.rstrip("e") + "ing" if verb.endswith("e") and verb not in ("change", "solve", "survive", "elevate", "maximize", "accelerate", "ignite", "decode") else verb + "ing",
        n=random.choice([3, 5, 7, 10, 15, 24, 30, 50, 100]),
        year=random.choice([2024, 2025, 2026]),
        money=random.choice(["1,000", "5,000", "10,000", "50,000", "100K", "1M"]),
    )


def _generate_tiktok_title():
    template = random.choice(TIKTOK_TITLE_TEMPLATES)
    verb = random.choice(VERBS)
    adj = random.choice(ADJECTIVES)
    tag1 = random.choice(TIKTOK_HASHTAGS)
    tag2 = random.choice([t for t in TIKTOK_HASHTAGS if t != tag1])
    return template.format(
        adj=adj,
        adj_er=ADJ_COMPARATIVE.get(adj, "more " + adj),
        noun=random.choice(NOUNS),
        noun2=random.choice(NOUNS),
        verb=verb,
        verb_ed=IRREGULAR_VERBS.get(verb, verb + "ed"),
        emoji=random.choice(EMOJIS),
        tag1=tag1,
        tag2=tag2,
        n=random.choice([0, 1, 10, 100, 500, 1000]),
        n2=random.choice(["10K", "100K", "1M", "5M"]),
        year=random.choice([2020, 2021, 2022, 2023]),
    )


def _generate_youtube_description(title):
    templates = [
        f"In this video, we dive deep into {title.lower()}. Don't forget to like and subscribe for more content like this!",
        f"Today we're exploring {title.lower()}. Let me know in the comments what you think!",
        f"Is {title.lower()} really worth it? Watch to find out! Hit that bell icon so you never miss an upload.",
        f"Join me on this incredible journey as I discover {title.lower()}. Share this with someone who needs to see it!",
        f"Breaking down everything you need to know about {title.lower()}. Subscribe and turn on notifications!",
        f"What happens when you try {title.lower()}? The results will surprise you. Drop a comment below!",
        f"I spent weeks researching {title.lower()} so you don't have to. Here are my findings!",
        f"The truth about {title.lower()} finally revealed. Watch until the end for a surprise!",
    ]
    return random.choice(templates)


def _generate_tiktok_description(title):
    templates = [
        f"{title} #fyp #viral",
        f"{title} follow for more!",
        f"{title} part {random.randint(1, 5)}",
        f"{title} link in bio",
        f"{title} duet this!",
        f"{title} save for later",
    ]
    return random.choice(templates)


def _generate_youtube_tags(title, category_name):
    words = [w.lower() for w in title.split() if len(w) > 3][:5]
    category_tag = category_name.lower().replace(" & ", " ").replace(" ", "")
    common_tags = ["viral", "trending", "2025", "must watch", "amazing"]
    selected_common = random.sample(common_tags, k=random.randint(1, 3))
    all_tags = words + [category_tag] + selected_common
    random.shuffle(all_tags)
    return ",".join(all_tags[:8])


def _generate_tiktok_tags(title):
    num_tags = random.randint(2, 5)
    base_tags = [w.strip("#") for w in title.split() if w.startswith("#")]
    extra = random.sample(TIKTOK_HASHTAGS, k=min(num_tags, len(TIKTOK_HASHTAGS)))
    all_tags = list(set(base_tags + extra))
    random.shuffle(all_tags)
    return ",".join(all_tags[:8])


def _generate_youtube_duration():
    minutes = random.randint(3, 45)
    seconds = random.randint(0, 59)
    return f"PT{minutes}M{seconds:02d}S"


def _generate_tiktok_duration():
    return str(random.randint(7, 180))


REAL_YOUTUBE_VIDEO_IDS = [
    "dQw4w9WgXcQ", "9bZkp7q19f0", "kJQP7kiw5Fk", "RgKAFK5djSk", "JGwWNGJdvx8",
    "OPf0YbXqDm0", "CevxZvSJLk8", "fJ9rUzIMcZQ", "hT_nvWreIhg", "e-ORhEE9VVg",
    "YQHsXMglC9A", "lp-EO5I60KA", "0KSOMA3QBU0", "kXYiU_JCYtU", "HP-MbfHFUqs",
    "pRpeEdMmmQ0", "QH2-TGUlwu4", "pU9S6HkGi7Y", "60ItHLz5WEA", "nfs8NYg7yQM",
    "Q8mD2hsxrhQ", "L_jWHffIx5E", "hLQl3WQQoQ0", "08OF3RdoMnI", "JRfuAukYTKg",
    "QIbc0Pm2E2E", "7PCkvCPvDXk", "XqZsoesa55w", "8Uee_mcxvrw", "BBJa32lCaaY",
    "rfscVS0vtbw", "mJgBOIpeYlI", "W6NZfCO5SIk", "Oe421EPjeBE", "rfscVS0vtbw",
    "b9eMGE7QtTk", "HluANRwPyNo", "xGytD1k0yT0", "XsX3ATc3FbA", "oHg5SJYRHA0",
    "jNQXAC9IVRw", "FTQbiNvZqaY", "jofNR_WkoCE", "9jK-NcRmVcw", "Yk8jV7r6VMk",
    "z3U0udLH974", "2Vv-BfVoq4g", "kXYiU_JCYtU", "b1WWpKEPdTg", "t4H_Zoh7G5A",
]

REAL_TIKTOK_THUMBNAILS = [
    "https://picsum.photos/seed/tiktok1/480/360",
    "https://picsum.photos/seed/tiktok2/480/360",
    "https://picsum.photos/seed/tiktok3/480/360",
    "https://picsum.photos/seed/tiktok4/480/360",
    "https://picsum.photos/seed/tiktok5/480/360",
    "https://picsum.photos/seed/tiktok6/480/360",
    "https://picsum.photos/seed/tiktok7/480/360",
    "https://picsum.photos/seed/tiktok8/480/360",
    "https://picsum.photos/seed/tiktok9/480/360",
    "https://picsum.photos/seed/tiktok10/480/360",
    "https://picsum.photos/seed/tiktok11/480/360",
    "https://picsum.photos/seed/tiktok12/480/360",
    "https://picsum.photos/seed/tiktok13/480/360",
    "https://picsum.photos/seed/tiktok14/480/360",
    "https://picsum.photos/seed/tiktok15/480/360",
    "https://picsum.photos/seed/tiktok16/480/360",
    "https://picsum.photos/seed/tiktok17/480/360",
    "https://picsum.photos/seed/tiktok18/480/360",
    "https://picsum.photos/seed/tiktok19/480/360",
    "https://picsum.photos/seed/tiktok20/480/360",
    "https://picsum.photos/seed/tiktok21/480/360",
    "https://picsum.photos/seed/tiktok22/480/360",
    "https://picsum.photos/seed/tiktok23/480/360",
    "https://picsum.photos/seed/tiktok24/480/360",
    "https://picsum.photos/seed/tiktok25/480/360",
    "https://picsum.photos/seed/tiktok26/480/360",
    "https://picsum.photos/seed/tiktok27/480/360",
    "https://picsum.photos/seed/tiktok28/480/360",
    "https://picsum.photos/seed/tiktok29/480/360",
    "https://picsum.photos/seed/tiktok30/480/360",
    "https://picsum.photos/seed/tiktok31/480/360",
    "https://picsum.photos/seed/tiktok32/480/360",
    "https://picsum.photos/seed/tiktok33/480/360",
    "https://picsum.photos/seed/tiktok34/480/360",
    "https://picsum.photos/seed/tiktok35/480/360",
    "https://picsum.photos/seed/tiktok36/480/360",
    "https://picsum.photos/seed/tiktok37/480/360",
    "https://picsum.photos/seed/tiktok38/480/360",
    "https://picsum.photos/seed/tiktok39/480/360",
    "https://picsum.photos/seed/tiktok40/480/360",
    "https://picsum.photos/seed/tiktok41/480/360",
    "https://picsum.photos/seed/tiktok42/480/360",
    "https://picsum.photos/seed/tiktok43/480/360",
    "https://picsum.photos/seed/tiktok44/480/360",
    "https://picsum.photos/seed/tiktok45/480/360",
    "https://picsum.photos/seed/tiktok46/480/360",
    "https://picsum.photos/seed/tiktok47/480/360",
    "https://picsum.photos/seed/tiktok48/480/360",
    "https://picsum.photos/seed/tiktok49/480/360",
    "https://picsum.photos/seed/tiktok50/480/360",
]


def _generate_youtube_thumbnail(video_id):
    real_id = random.choice(REAL_YOUTUBE_VIDEO_IDS)
    return f"https://i.ytimg.com/vi/{real_id}/hqdefault.jpg"


def _generate_tiktok_thumbnail(video_id):
    return random.choice(REAL_TIKTOK_THUMBNAILS)


def generate_demo_data(db: Session) -> int:
    existing = db.query(Video).count()
    if existing > 0:
        return 0

    count = 0
    now = datetime.now(timezone.utc)

    yt_channels = random.sample(YOUTUBE_CHANNELS, k=min(30, len(YOUTUBE_CHANNELS)))
    for i in range(50):
        tier = random.random()
        if tier < 0.15:
            hours_ago = random.uniform(1, 48)
        elif tier < 0.35:
            hours_ago = random.uniform(12, 168)
        elif tier < 0.55:
            hours_ago = random.uniform(48, 720)
        elif tier < 0.75:
            hours_ago = random.uniform(720, 2160)
        elif tier < 0.90:
            hours_ago = random.uniform(2160, 8760)
        else:
            hours_ago = random.uniform(8760, 35000)
        published = now - timedelta(hours=hours_ago, minutes=random.randint(0, 59), seconds=random.randint(0, 59))
        views = _power_law_sample(50000, 800000000, alpha=1.5)
        like_ratio = random.uniform(0.015, 0.10)
        comment_ratio = random.uniform(0.001, 0.006)
        share_ratio = random.uniform(0.003, 0.025)
        likes = int(views * like_ratio)
        comments = int(views * comment_ratio)
        shares = int(views * share_ratio)

        cat_id = random.choice(list(YOUTUBE_CATEGORIES.keys()))
        cat_name = YOUTUBE_CATEGORIES[cat_id]
        title = _generate_youtube_title()
        channel = yt_channels[i % len(yt_channels)]
        real_yt_id = random.choice(REAL_YOUTUBE_VIDEO_IDS)

        video = Video(
            platform=Platform.YOUTUBE,
            video_id=f"yt_{real_yt_id}",
            title=title,
            description=_generate_youtube_description(title),
            channel_title=channel,
            channel_id=f"UC{uuid.uuid4().hex[:24]}",
            published_at=published,
            thumbnail_url=f"https://i.ytimg.com/vi/{real_yt_id}/hqdefault.jpg",
            video_url=f"https://www.youtube.com/watch?v={real_yt_id}",
            duration=_generate_youtube_duration(),
            category=cat_id,
            tags=_generate_youtube_tags(title, cat_name),
            view_count=views,
            like_count=likes,
            comment_count=comments,
            share_count=shares,
        )
        db.add(video)
        db.flush()

        snap1_views = int(views * random.uniform(0.5, 0.85))
        snap1_offset = min(random.uniform(2, 24), max(1, hours_ago - 1))
        snapshot1 = VideoSnapshot(
            video_id=video.id,
            platform=Platform.YOUTUBE,
            view_count=snap1_views,
            like_count=int(likes * random.uniform(0.5, 0.85)),
            comment_count=int(comments * random.uniform(0.5, 0.85)),
            snapshot_time=now - timedelta(hours=snap1_offset),
            view_growth_rate=random.uniform(5, 60),
            like_growth_rate=random.uniform(5, 60),
        )
        db.add(snapshot1)

        snapshot2 = VideoSnapshot(
            video_id=video.id,
            platform=Platform.YOUTUBE,
            view_count=views,
            like_count=likes,
            comment_count=comments,
            snapshot_time=now,
            view_growth_rate=((views - snap1_views) / max(snap1_views, 1)) * 100,
            like_growth_rate=random.uniform(1, 25),
        )
        db.add(snapshot2)
        count += 1

    tt_channels = random.sample(TIKTOK_CHANNELS, k=min(30, len(TIKTOK_CHANNELS)))
    for i in range(50):
        tier = random.random()
        if tier < 0.15:
            hours_ago = random.uniform(1, 48)
        elif tier < 0.35:
            hours_ago = random.uniform(12, 168)
        elif tier < 0.55:
            hours_ago = random.uniform(48, 720)
        elif tier < 0.75:
            hours_ago = random.uniform(720, 2160)
        elif tier < 0.90:
            hours_ago = random.uniform(2160, 8760)
        else:
            hours_ago = random.uniform(8760, 35000)
        published = now - timedelta(hours=hours_ago, minutes=random.randint(0, 59), seconds=random.randint(0, 59))
        views = _power_law_sample(10000, 300000000, alpha=1.5)
        like_ratio = random.uniform(0.03, 0.15)
        comment_ratio = random.uniform(0.002, 0.01)
        share_ratio = random.uniform(0.01, 0.08)
        likes = int(views * like_ratio)
        comments = int(views * comment_ratio)
        shares = int(views * share_ratio)

        title = _generate_tiktok_title()
        channel = tt_channels[i % len(tt_channels)]
        tt_vid_id = uuid.uuid4().hex[:19]

        video = Video(
            platform=Platform.TIKTOK,
            video_id=f"tt_{tt_vid_id}",
            title=title,
            description=_generate_tiktok_description(title),
            channel_title=channel,
            channel_id=str(random.randint(100000000, 999999999)),
            published_at=published,
            thumbnail_url=_generate_tiktok_thumbnail(tt_vid_id),
            video_url=f"https://www.tiktok.com/@{channel}/video/{random.randint(7000000000000000000, 7999999999999999999)}",
            duration=_generate_tiktok_duration(),
            category="",
            tags=_generate_tiktok_tags(title),
            view_count=views,
            like_count=likes,
            comment_count=comments,
            share_count=shares,
        )
        db.add(video)
        db.flush()

        snap1_views = int(views * random.uniform(0.4, 0.8))
        snap1_offset = min(random.uniform(1, 18), max(1, hours_ago - 1))
        snapshot1 = VideoSnapshot(
            video_id=video.id,
            platform=Platform.TIKTOK,
            view_count=snap1_views,
            like_count=int(likes * random.uniform(0.4, 0.8)),
            comment_count=int(comments * random.uniform(0.4, 0.8)),
            share_count=int(shares * random.uniform(0.4, 0.8)),
            snapshot_time=now - timedelta(hours=snap1_offset),
            view_growth_rate=random.uniform(10, 100),
            like_growth_rate=random.uniform(10, 100),
        )
        db.add(snapshot1)

        snapshot2 = VideoSnapshot(
            video_id=video.id,
            platform=Platform.TIKTOK,
            view_count=views,
            like_count=likes,
            comment_count=comments,
            share_count=shares,
            snapshot_time=now,
            view_growth_rate=((views - snap1_views) / max(snap1_views, 1)) * 100,
            like_growth_rate=random.uniform(2, 40),
        )
        db.add(snapshot2)
        count += 1

    db.commit()
    return count
