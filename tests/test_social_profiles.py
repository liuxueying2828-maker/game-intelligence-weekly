import unittest

from output.html import build_dashboard_html
from sources.social_profiles import _merge_profiles


class SocialProfileTests(unittest.TestCase):
    def test_registry_survives_missing_live_search(self):
        games = [{"company": "Tencent", "title_cn": "湮灭之潮", "title_en": "Tides of Annihilation"}]
        registry = [{
            "title_cn": "湮灭之潮",
            "title_en": "Tides of Annihilation",
            "checked_at": "2026-10-29",
            "accounts": [
                {"platform": "x", "url": "https://x.com/play_toa", "status": "discovered"},
                {"platform": "youtube", "url": "https://www.youtube.com/@tidesofannihilation", "status": "official_confirmed"},
            ],
        }]
        profiles = _merge_profiles(games, [], registry)
        self.assertEqual(len(profiles), 1)
        self.assertEqual({a["platform"] for a in profiles[0]["accounts"]}, {"x", "youtube"})

    def test_steamdb_cannot_be_official_confirmed(self):
        games = [{"title_cn": "湮灭之潮", "title_en": "Tides of Annihilation"}]
        live = [{
            "title_en": "Tides of Annihilation",
            "accounts": [{"platform": "steamdb", "url": "https://steamdb.info/app/3292470/", "status": "official_confirmed"}],
        }]
        account = _merge_profiles(games, live, [])[0]["accounts"][0]
        self.assertEqual(account["status"], "discovered")

    def test_dashboard_renders_static_social_profile(self):
        html = build_dashboard_html({
            "date": "2026-10-29",
            "headline": "测试",
            "social_profiles": [{
                "company": "腾讯游戏",
                "title_cn": "湮灭之潮",
                "title_en": "Tides of Annihilation",
                "checked_at": "2026-10-29",
                "accounts": [{"platform": "x", "url": "https://x.com/play_toa", "status": "discovered"}],
            }],
        })
        self.assertIn("重点游戏海外阵地", html)
        self.assertIn("https://x.com/play_toa", html)
        self.assertIn("Tides of Annihilation", html)


if __name__ == "__main__":
    unittest.main()
