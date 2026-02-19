"""
Safety Gamification Engine - محرك التحفيز والنقاط
نظام تحفيزي لرفع ثقافة السلامة
"""

import json
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List


@dataclass
class PlayerProfile:
    """ملف تعريف اللاعب"""

    player_id: str
    display_name: str
    points: int = 0
    level: int = 1
    badges: List[str] = field(default_factory=list)
    achievements: List[Dict] = field(default_factory=list)
    streak_days: int = 0
    team: str = ""


@dataclass
class Achievement:
    """إنجاز"""

    id: str
    name: str
    description: str
    points_reward: int
    badge: str
    criteria: Dict[str, Any]


class SafetyGamificationEngine:
    """محرك التحفيز"""

    def __init__(self):
        self.players: Dict[str, PlayerProfile] = {}
        self.teams: Dict[str, List[str]] = defaultdict(list)
        self.achievements = self._initialize_achievements()
        self.leaderboard = {"individual": [], "team": [], "site": []}

    def register_player(self, player_data: Dict) -> Dict:
        """تسجيل لاعب جديد"""
        player = PlayerProfile(
            player_id=player_data["id"],
            display_name=player_data["name"],
            team=player_data.get("team", "default"),
        )

        self.players[player.player_id] = player
        self.teams[player.team].append(player.player_id)

        # مكافأة الانضمام
        player.points += 100

        return {
            "player_id": player.player_id,
            "welcome_points": 100,
            "message": "مرحباً في نظام السلامة التحفيزي! 🎮",
        }

    def record_safe_behavior(self, behavior_data: Dict) -> Dict:
        """تسجيل سلوك آمن"""
        player_id = behavior_data["player_id"]
        behavior_type = behavior_data["behavior_type"]

        if player_id not in self.players:
            return {"error": "اللاعب غير مسجل"}

        player = self.players[player_id]

        # منح النقاط
        points_map = {
            "wearing_ppe": 10,
            "reporting_hazard": 25,
            "helping_colleague": 15,
            "following_procedure": 10,
            "safety_suggestion": 30,
        }

        points = points_map.get(behavior_type, 5)
        player.points += points

        # تحديث المستوى
        old_level = player.level
        player.level = self._calculate_level(player.points)
        leveled_up = player.level > old_level

        # التحقق من الإنجازات
        new_achievements = self._check_achievements(player, behavior_data)

        # تحديث السلسلة
        player.streak_days += 1

        return {
            "player_id": player_id,
            "points_earned": points,
            "total_points": player.points,
            "level": player.level,
            "leveled_up": leveled_up,
            "new_achievements": new_achievements,
            "streak": player.streak_days,
            "message": self._get_encouragement_message(points, leveled_up),
        }

    def get_leaderboard(
        self, leaderboard_type: str = "individual", limit: int = 10
    ) -> Dict:
        """الحصول على لوحة الصدارة"""

        if leaderboard_type == "individual":
            sorted_players = sorted(
                self.players.values(), key=lambda p: p.points, reverse=True
            )[:limit]

            return {
                "type": "individual",
                "leaderboard": [
                    {
                        "rank": i + 1,
                        "player": p.display_name,
                        "points": p.points,
                        "level": p.level,
                        "badges": len(p.badges),
                    }
                    for i, p in enumerate(sorted_players)
                ],
            }

        elif leaderboard_type == "team":
            team_scores = {}
            for team, members in self.teams.items():
                team_scores[team] = sum(self.players[pid].points for pid in members)

            sorted_teams = sorted(
                team_scores.items(), key=lambda x: x[1], reverse=True
            )[:limit]

            return {
                "type": "team",
                "leaderboard": [
                    {
                        "rank": i + 1,
                        "team": team,
                        "total_points": points,
                        "members": len(self.teams[team]),
                    }
                    for i, (team, points) in enumerate(sorted_teams)
                ],
            }

    def award_badge(self, player_id: str, badge_name: str) -> Dict:
        """منح وسام"""
        if player_id not in self.players:
            return {"error": "اللاعب غير موجود"}

        player = self.players[player_id]

        if badge_name not in player.badges:
            player.badges.append(badge_name)
            player.points += 50  # مكافأة إضافية

            return {
                "badge": badge_name,
                "bonus_points": 50,
                "total_badges": len(player.badges),
                "message": f"تهانينا! حصلت على وسام {badge_name} 🏆",
            }

        return {"message": "الوسام محصل عليه مسبقاً"}

    def create_challenge(self, challenge_data: Dict) -> Dict:
        """إنشاء تحدي"""
        challenge = {
            "id": f"ch_{datetime.now().timestamp()}",
            "name": challenge_data["name"],
            "description": challenge_data["description"],
            "start_date": challenge_data["start_date"],
            "end_date": challenge_data["end_date"],
            "goal": challenge_data["goal"],
            "reward_points": challenge_data.get("reward_points", 100),
            "participants": [],
        }

        return challenge

    def _initialize_achievements(self) -> Dict[str, Achievement]:
        """تهيئة الإنجازات"""
        return {
            "first_day": Achievement(
                id="first_day",
                name="اليوم الأول",
                description="أكمل أول يوم عمل آمن",
                points_reward=50,
                badge="newcomer",
                criteria={"days": 1},
            ),
            "safety_week": Achievement(
                id="safety_week",
                name="أسبوع السلامة",
                description="7 أيام متتالية بدون حوادث",
                points_reward=200,
                badge="week_warrior",
                criteria={"streak": 7},
            ),
            "safety_champion": Achievement(
                id="safety_champion",
                name="بطل السلامة",
                description="1000 نقطة",
                points_reward=500,
                badge="champion",
                criteria={"points": 1000},
            ),
        }

    def _calculate_level(self, points: int) -> int:
        """حساب المستوى"""
        return min(points // 100 + 1, 100)

    def _check_achievements(
        self, player: PlayerProfile, behavior_data: Dict
    ) -> List[str]:
        """التحقق من الإنجازات الجديدة"""
        new_achievements = []

        for achievement in self.achievements.values():
            if achievement.id in [a["id"] for a in player.achievements]:
                continue

            # التحقق من المعايير
            if self._achievement_unlocked(player, achievement):
                player.achievements.append(
                    {
                        "id": achievement.id,
                        "name": achievement.name,
                        "unlocked_at": datetime.now().isoformat(),
                    }
                )
                player.points += achievement.points_reward
                if achievement.badge:
                    player.badges.append(achievement.badge)
                new_achievements.append(achievement.name)

        return new_achievements

    def _achievement_unlocked(
        self, player: PlayerProfile, achievement: Achievement
    ) -> bool:
        """التحقق من فتح الإنجاز"""
        if "points" in achievement.criteria:
            return player.points >= achievement.criteria["points"]
        if "streak" in achievement.criteria:
            return player.streak_days >= achievement.criteria["streak"]
        if "days" in achievement.criteria:
            return player.streak_days >= achievement.criteria["days"]
        return False

    def _get_encouragement_message(self, points: int, leveled_up: bool) -> str:
        """رسالة تحفيزية"""
        if leveled_up:
            return "🎉 تهانينا! ارتقيت إلى مستوى جديد!"
        elif points > 20:
            return "رائع! سلوك ممتاز في السلامة! 🌟"
        else:
            return "أحسنت! استمر في العمل الآمن! ✅"
