import re
import math
from typing import Optional
from collections import Counter

from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.models.video import Video, RevenueEstimate, Platform


TITLE_SEO_KEYWORDS = {
    "youtube": [
        "how to", "tutorial", "review", "best", "top", "vs", "guide", "tips",
        "tricks", "explained", "ultimate", "complete", "beginner", "advanced",
        "2024", "2025", "2026", "free", "easy", "simple", "step by step",
        "hack", "secret", "proven", "must know", "you need", "why",
    ],
    "tiktok": [
        "hack", "tips", "tricks", "how", "diy", "recipe", "tutorial",
        "challenge", "trend", "viral", "fyp", "foryou", "foryoupage",
        "duet", "stitch", "react", "try", "test", "rating", "rank",
        "unboxing", "haul", "transformation", "before after", "glow up",
    ],
}

EMOTION_WORDS = [
    "amazing", "incredible", "shocking", "unbelievable", "insane", "crazy",
    "mind blowing", "wow", "omg", "must see", "you wont believe", "secret",
    "hidden", "exposed", "revealed", "truth", "never knew", "game changer",
    "life changing", "genius", "brilliant", "terrifying", "hilarious",
]

CATEGORY_CPM = {
    "general": 1.0,
    "tech": 1.8,
    "finance": 2.5,
    "gaming": 1.2,
    "education": 1.5,
    "entertainment": 0.8,
    "music": 0.6,
    "beauty": 1.3,
    "fitness": 1.1,
    "food": 0.9,
    "travel": 1.4,
    "news": 1.6,
}

REGION_CPM = {
    "us": 1.5,
    "eu": 1.2,
    "asia": 0.8,
    "global": 1.0,
}

NICHE_DATABASE = {
    "youtube": [
        {
            "name": "AI 工具教程",
            "keywords": ["ai", "chatgpt", "人工智能", "工具", "ai工具", "ai教程"],
            "reason": "AI 工具爆发式增长，用户对实际操作教程需求强烈，搜索量持续攀升",
            "competition": "中",
            "growth_potential": "极高",
            "avg_cpm": 12.50,
        },
        {
            "name": "编程/开发教程",
            "keywords": ["编程", "代码", "开发", "python", "javascript", "web开发", "app开发"],
            "reason": "技术类内容 CPM 高，长尾流量稳定，变现能力强",
            "competition": "高",
            "growth_potential": "高",
            "avg_cpm": 15.00,
        },
        {
            "name": "个人理财/投资",
            "keywords": ["理财", "投资", "赚钱", "股票", "基金", "副业", "passive income"],
            "reason": "金融类内容 CPM 最高，观众购买力强，适合品牌合作",
            "competition": "高",
            "growth_potential": "中",
            "avg_cpm": 22.00,
        },
        {
            "name": "数码产品测评",
            "keywords": ["测评", "评测", "开箱", "数码", "手机", "电脑", "科技"],
            "reason": "测评内容购买意图强，带货转化率高，品牌合作机会多",
            "competition": "高",
            "growth_potential": "中",
            "avg_cpm": 14.00,
        },
        {
            "name": "健康/健身教程",
            "keywords": ["健身", "减肥", "健康", "瑜伽", "运动", "饮食", "减脂"],
            "reason": "健康意识持续提升，教程类内容粉丝粘性高，适合长期运营",
            "competition": "中",
            "growth_potential": "高",
            "avg_cpm": 8.00,
        },
        {
            "name": "美食制作/食谱",
            "keywords": ["美食", "食谱", "烹饪", "做菜", "烘焙", "料理", "cooking"],
            "reason": "美食内容观看完成率高，跨文化吸引力强，带货空间大",
            "competition": "中",
            "growth_potential": "高",
            "avg_cpm": 6.50,
        },
        {
            "name": "旅行 Vlog",
            "keywords": ["旅行", "旅游", "vlog", "出行", "攻略", "打卡", "travel"],
            "reason": "旅游复苏期，沉浸式内容观看时长增长，品牌合作机会多",
            "competition": "中",
            "growth_potential": "高",
            "avg_cpm": 9.00,
        },
        {
            "name": "游戏实况/攻略",
            "keywords": ["游戏", "gaming", "攻略", "实况", "直播", "电竞", "gameplay"],
            "reason": "游戏社区活跃度高，直播打赏+广告双重收入，粉丝忠诚度强",
            "competition": "高",
            "growth_potential": "中",
            "avg_cpm": 7.00,
        },
    ],
    "tiktok": [
        {
            "name": "生活小技巧",
            "keywords": ["技巧", "hack", "生活", "实用", "小妙招", "diy"],
            "reason": "实用型短视频在 TikTok 传播力最强，完播率高，容易上热门",
            "competition": "低",
            "growth_potential": "极高",
            "avg_cpm": 3.50,
        },
        {
            "name": "美食制作",
            "keywords": ["美食", "食谱", "做菜", "烘焙", "cooking", "recipe"],
            "reason": "美食内容观看完成率最高，视觉冲击力强，适合带货",
            "competition": "中",
            "growth_potential": "高",
            "avg_cpm": 4.00,
        },
        {
            "name": "穿搭/时尚",
            "keywords": ["穿搭", "时尚", "ootd", "服装", "搭配", "fashion"],
            "reason": "视觉冲击力强，品牌合作机会多，粉丝购买力强",
            "competition": "高",
            "growth_potential": "中",
            "avg_cpm": 5.00,
        },
        {
            "name": "搞笑/段子",
            "keywords": ["搞笑", "段子", "喜剧", "funny", "恶搞", "模仿"],
            "reason": "传播力最强，涨粉最快的赛道，互动率极高",
            "competition": "中",
            "growth_potential": "高",
            "avg_cpm": 2.50,
        },
        {
            "name": "健身/运动",
            "keywords": ["健身", "运动", "减肥", "瑜伽", "fitness", "workout"],
            "reason": "健康内容持续增长，粉丝粘性高，适合长期运营",
            "competition": "中",
            "growth_potential": "高",
            "avg_cpm": 4.50,
        },
        {
            "name": "宠物日常",
            "keywords": ["宠物", "猫", "狗", "pet", "可爱", "萌宠"],
            "reason": "宠物内容永远是流量密码，互动率极高，跨文化无障碍",
            "competition": "低",
            "growth_potential": "高",
            "avg_cpm": 2.00,
        },
        {
            "name": "美妆/护肤",
            "keywords": ["美妆", "护肤", "化妆", "beauty", "skincare", "makeup"],
            "reason": "美妆类带货能力最强，品牌合作最密集，CPM 较高",
            "competition": "高",
            "growth_potential": "中",
            "avg_cpm": 6.00,
        },
        {
            "name": "知识科普",
            "keywords": ["科普", "知识", "冷知识", "science", "facts", "did you know"],
            "reason": "知识类内容分享率高，容易获得推荐流量，粉丝质量高",
            "competition": "低",
            "growth_potential": "极高",
            "avg_cpm": 3.00,
        },
    ],
}


class AIAnalyzer:
    def __init__(self, db: Session):
        self.db = db

    def analyze_title(self, platform: str, title: str) -> dict:
        title_lower = title.lower().strip()
        title_len = len(title)

        keyword_list = TITLE_SEO_KEYWORDS.get(platform, TITLE_SEO_KEYWORDS["youtube"])
        matched_keywords = [kw for kw in keyword_list if kw in title_lower]
        keyword_density = min(100, round((len(matched_keywords) / max(len(keyword_list), 1)) * 100 * 10))

        if title_len < 20:
            length_score = 35
        elif title_len < 30:
            length_score = 55
        elif title_len < 45:
            length_score = 85
        elif title_len < 60:
            length_score = 95
        elif title_len < 75:
            length_score = 75
        else:
            length_score = 45

        has_emoji = bool(re.search(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U0001f900-\U0001f9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF]', title))
        has_question = bool(re.search(r'[?？]', title))
        has_exclaim = bool(re.search(r'[!！]', title))
        has_ellipsis = '...' in title or '…' in title
        has_brackets = bool(re.search(r'[\[【(（]', title))

        emotion_matched = [w for w in EMOTION_WORDS if w in title_lower]
        emotion_base = len(emotion_matched) * 20
        emotion_bonus = (has_emoji * 15) + (has_question * 12) + (has_exclaim * 10) + (has_ellipsis * 8) + (has_brackets * 5)
        emotion_score = min(100, emotion_base + emotion_bonus + 10)

        has_number = bool(re.search(r'\d', title))
        has_list_number = bool(re.search(r'(?:top\s*\d+|\d+\s*(?:best|tips|ways|reasons|things|tricks))', title_lower))
        has_year = bool(re.search(r'20[2-9]\d', title))
        number_score = 0
        if has_list_number:
            number_score = 90
        elif has_number and has_year:
            number_score = 80
        elif has_number:
            number_score = 70
        elif has_emoji:
            number_score = 40
        else:
            number_score = 20

        db_bonus = self._get_db_title_bonus(platform, title)

        seo_score = round(
            keyword_density * 0.30
            + length_score * 0.25
            + emotion_score * 0.20
            + number_score * 0.15
            + db_bonus * 0.10
        )
        seo_score = min(100, max(0, seo_score))

        ctr_prediction = round(seo_score * 0.06 + len(matched_keywords) * 0.5 + (5 if has_number else 0) + (3 if has_emoji else 0) + (2 if has_question else 0) + 1.5, 1)
        ctr_prediction = min(25.0, ctr_prediction)

        suggestions = []
        if title_len < 30:
            suggestions.append("标题较短，建议增加到 40-60 字符以提升 SEO 和搜索曝光")
        if title_len > 70:
            suggestions.append("标题过长，可能在搜索结果中被截断，建议精简到 60 字符以内")
        if not has_number:
            suggestions.append('添加数字可以显著提升点击率（如 "5 个技巧"、"2026 年" 等）')
        if not has_question and not has_exclaim:
            suggestions.append("使用疑问句或感叹号可以增加情感吸引力，提升 CTR")
        if not has_emoji and platform == "tiktok":
            suggestions.append("TikTok 标题中适当使用 Emoji 可以大幅提升视觉吸引力")
        if not matched_keywords:
            suggestions.append("标题缺少热门关键词，建议加入如 'how to'、'tutorial'、'best' 等搜索热词")
        if not has_brackets:
            suggestions.append("使用方括号【】突出关键信息可以提升点击率")
        if keyword_density < 30:
            suggestions.append("关键词密度较低，建议在标题中包含更多核心关键词")
        if db_bonus > 50:
            suggestions.append("你的标题与当前热门视频风格相似，有较好的流量潜力")
        elif db_bonus < 20 and db_bonus >= 0:
            suggestions.append("标题与当前热门趋势关联度较低，考虑加入热门话题关键词")

        return {
            "seo_score": seo_score,
            "ctr_prediction": ctr_prediction,
            "keyword_density": keyword_density,
            "length_score": length_score,
            "emotion_score": emotion_score,
            "number_score": number_score,
            "matched_keywords": matched_keywords,
            "suggestions": suggestions,
        }

    def _get_db_title_bonus(self, platform: str, title: str) -> float:
        try:
            p = Platform(platform) if platform else None
            query = self.db.query(Video)
            if p:
                query = query.filter(Video.platform == p)
            top_videos = query.order_by(desc(Video.view_count)).limit(50).all()

            if not top_videos:
                return 50.0

            title_words = set(re.findall(r'\w+', title.lower()))
            if not title_words:
                return 30.0

            similarity_scores = []
            for v in top_videos:
                v_words = set(re.findall(r'\w+', v.title.lower()))
                if v_words:
                    overlap = len(title_words & v_words)
                    total = len(title_words | v_words)
                    similarity = overlap / total if total > 0 else 0
                    view_bonus = min(1.0, v.view_count / 10000000) if v.view_count else 0
                    similarity_scores.append(similarity * 0.7 + view_bonus * 0.3)

            if similarity_scores:
                avg_similarity = sum(similarity_scores) / len(similarity_scores)
                return min(100, avg_similarity * 150)
            return 30.0
        except Exception:
            return 50.0

    def analyze_niche(self, keyword: str, platform: str) -> dict:
        niche_db = NICHE_DATABASE.get(platform, NICHE_DATABASE["youtube"])
        keyword_lower = keyword.lower().strip()
        keyword_words = set(re.findall(r'\w+', keyword_lower))

        scored_niches = []
        for niche in niche_db:
            niche_words = set()
            for kw in niche["keywords"]:
                niche_words.update(re.findall(r'\w+', kw.lower()))

            overlap = len(keyword_words & niche_words)
            total = len(keyword_words | niche_words)
            similarity = overlap / total if total > 0 else 0

            exact_match = any(kw in keyword_lower for kw in niche["keywords"])
            score = similarity * 60 + (30 if exact_match else 0) + (10 if niche["growth_potential"] in ["高", "极高"] else 0)

            scored_niches.append((score, niche))

        scored_niches.sort(key=lambda x: x[0], reverse=True)

        db_insights = self._get_db_niche_insights(keyword, platform)

        recommendations = []
        for i, (score, niche) in enumerate(scored_niches[:5]):
            rec = {
                "name": niche["name"],
                "reason": niche["reason"],
                "competition": niche["competition"],
                "growth_potential": niche["growth_potential"],
                "avg_cpm": niche["avg_cpm"],
                "relevance_score": round(score, 1),
            }
            if db_insights and i == 0:
                rec["reason"] += f"。数据库中已有 {db_insights.get('video_count', 0)} 条相关视频，平均播放量 {db_insights.get('avg_views', 0):,.0f}"
            recommendations.append(rec)

        return {"recommendations": recommendations}

    def _get_db_niche_insights(self, keyword: str, platform: str) -> Optional[dict]:
        try:
            p = Platform(platform) if platform else None
            query = self.db.query(Video)
            if p:
                query = query.filter(Video.platform == p)

            keyword_lower = f"%{keyword.lower()}%"
            related = query.filter(Video.title.ilike(keyword_lower)).all()

            if not related:
                return None

            total_views = sum(v.view_count or 0 for v in related)
            avg_views = total_views / len(related) if related else 0

            return {
                "video_count": len(related),
                "avg_views": avg_views,
                "total_views": total_views,
            }
        except Exception:
            return None

    def predict_trend(self, platform: str) -> dict:
        p = Platform(platform) if platform else None

        db_trends = self._extract_trends_from_db(p)

        if db_trends:
            return {"trends": db_trends}

        return {"trends": self._get_default_trends(platform)}

    def _extract_trends_from_db(self, platform: Optional[Platform]) -> list[dict]:
        try:
            query = self.db.query(Video)
            if platform:
                query = query.filter(Video.platform == platform)

            recent_videos = query.order_by(desc(Video.view_count)).limit(100).all()

            if len(recent_videos) < 5:
                return []

            word_counter = Counter()
            bigram_counter = Counter()

            for v in recent_videos:
                words = re.findall(r'[a-zA-Z\u4e00-\u9fff]{2,}', v.title.lower())
                word_counter.update(words)
                for i in range(len(words) - 1):
                    bigram_counter[f"{words[i]} {words[i+1]}"] += 1

            stop_words = {
                'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
                'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from',
                'and', 'or', 'but', 'not', 'this', 'that', 'it', 'its',
                'has', 'have', 'had', 'do', 'does', 'did', 'will', 'would',
                'can', 'could', 'should', 'may', 'might', 'must',
                'de', 'la', 'le', 'el', 'en', 'es', 'un', 'una', 'los',
                '的', '了', '在', '是', '我', '有', '和', '就', '不', '人',
                '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去',
                '你', '会', '着', '没有', '看', '好', '自己', '这',
                'he', 'she', 'we', 'they', 'my', 'your', 'his', 'her',
                'our', 'their', 'what', 'which', 'who', 'when', 'where',
                'how', 'why', 'all', 'each', 'every', 'both', 'few',
                'more', 'most', 'other', 'some', 'such', 'no', 'nor',
                'only', 'own', 'same', 'so', 'than', 'too', 'very',
                'just', 'because', 'as', 'until', 'while', 'about',
                'between', 'through', 'during', 'before', 'after',
                'above', 'below', 'up', 'down', 'out', 'off', 'over',
                'under', 'again', 'then', 'once', 'here', 'there',
                'if', 'into', 'am', 'been', 'being', 'did', 'doing',
                'get', 'got', 'make', 'made', 'take', 'took',
                'new', 'old', 'big', 'small', 'day', 'days', 'time',
                'year', 'years', 'world', 'way', 'thing', 'things',
                'part', 'parts', 'video', 'videos', 'watch',
            }

            top_words = [
                (w, c) for w, c in word_counter.most_common(30)
                if w not in stop_words and c >= 2
            ]

            top_bigrams = [
                (b, c) for b, c in bigram_counter.most_common(15)
                if c >= 2 and not all(w in stop_words for w in b.split())
            ]

            trends = []
            used_words = set()

            for bigram, count in top_bigrams[:3]:
                avg_views = self._get_avg_views_for_keyword(bigram, platform)
                confidence = min(95, 60 + count * 5 + int(avg_views / 100000))
                tags = self._generate_tags(bigram, recent_videos)
                trends.append({
                    "name": bigram.title(),
                    "reason": f"在近期热门视频中出现 {count} 次" + (f"，平均播放量 {avg_views:,.0f}" if avg_views > 0 else "") + "，增长势头明显",
                    "tags": tags,
                    "confidence": confidence,
                })
                used_words.update(bigram.split())

            for word, count in top_words[:5]:
                if word in used_words:
                    continue
                avg_views = self._get_avg_views_for_keyword(word, platform)
                confidence = min(90, 55 + count * 4 + int(avg_views / 100000))
                tags = self._generate_tags(word, recent_videos)
                trends.append({
                    "name": word.title(),
                    "reason": f"高频关键词，出现 {count} 次" + (f"，相关视频平均播放量 {avg_views:,.0f}" if avg_views > 0 else "") + "，持续受到关注",
                    "tags": tags,
                    "confidence": confidence,
                })
                used_words.add(word)
                if len(trends) >= 5:
                    break

            return trends[:5]
        except Exception:
            return []

    def _get_avg_views_for_keyword(self, keyword: str, platform: Optional[Platform]) -> float:
        try:
            query = self.db.query(Video)
            if platform:
                query = query.filter(Video.platform == platform)
            related = query.filter(Video.title.ilike(f"%{keyword}%")).all()
            if not related:
                return 0
            return sum(v.view_count or 0 for v in related) / len(related)
        except Exception:
            return 0

    def _generate_tags(self, keyword: str, videos: list) -> list[str]:
        tags = [keyword]
        related_words = Counter()
        kw_lower = keyword.lower()
        for v in videos:
            if kw_lower in v.title.lower():
                words = re.findall(r'[a-zA-Z\u4e00-\u9fff]{2,}', v.title.lower())
                for w in words:
                    if w != kw_lower and len(w) >= 2:
                        related_words[w] += 1

        for w, _ in related_words.most_common(3):
            if len(tags) < 4:
                tags.append(w)

        return tags[:4]

    def _get_default_trends(self, platform: str) -> list[dict]:
        if platform == "youtube":
            return [
                {"name": "AI 工具测评", "reason": "AI 工具爆发式增长，用户对实际体验和对比需求强烈", "tags": ["AI", "科技", "测评"], "confidence": 92},
                {"name": "短视频赚钱攻略", "reason": "经济环境下，副业和赚钱内容搜索量持续上升", "tags": ["赚钱", "副业", "教程"], "confidence": 87},
                {"name": "健康饮食/减脂", "reason": "健康意识提升，简单易做的健康食谱需求增长", "tags": ["健康", "饮食", "生活"], "confidence": 83},
                {"name": "旅行 Vlog", "reason": "旅游复苏，沉浸式旅行内容观看时长增长显著", "tags": ["旅行", "Vlog", "体验"], "confidence": 78},
                {"name": "宠物搞笑/日常", "reason": "宠物内容永远是流量密码，互动率极高", "tags": ["宠物", "搞笑", "日常"], "confidence": 75},
            ]
        else:
            return [
                {"name": "生活小技巧", "reason": "实用型短视频在 TikTok 传播力最强", "tags": ["生活", "技巧", "实用"], "confidence": 90},
                {"name": "美食制作", "reason": "美食内容观看完成率最高，适合带货", "tags": ["美食", "制作", "教程"], "confidence": 88},
                {"name": "穿搭/时尚", "reason": "视觉冲击力强，品牌合作机会多", "tags": ["穿搭", "时尚", "OOTD"], "confidence": 85},
                {"name": "搞笑/段子", "reason": "传播力最强，涨粉最快的赛道", "tags": ["搞笑", "段子", "娱乐"], "confidence": 82},
                {"name": "健身/运动", "reason": "健康内容持续增长，粉丝粘性高", "tags": ["健身", "运动", "健康"], "confidence": 79},
            ]

    def calculate_revenue(
        self,
        platform: str,
        views: int,
        category: str = "general",
        region: str = "us",
    ) -> dict:
        is_youtube = platform == "youtube"

        base_cpm = 7.50 if is_youtube else 2.00
        cat_mul = CATEGORY_CPM.get(category, 1.0)
        reg_mul = REGION_CPM.get(region, 1.0)
        cpm = round(base_cpm * cat_mul * reg_mul, 2)

        monetization_rate = 0.55 if is_youtube else 0.30
        creator_share_rate = 0.55 if is_youtube else 0.50

        monetized_views = int(views * monetization_rate)
        total_ad_revenue = round((monetized_views / 1000) * cpm, 2)
        creator_share = round(total_ad_revenue * creator_share_rate, 2)

        low = round(creator_share * 0.3, 2)
        high = round(creator_share * 2.0, 2)

        return {
            "cpm": cpm,
            "monetized_views": monetized_views,
            "monetization_rate": monetization_rate,
            "total_ad_revenue": total_ad_revenue,
            "creator_share": creator_share,
            "creator_share_rate": creator_share_rate,
            "low": low,
            "high": high,
        }
