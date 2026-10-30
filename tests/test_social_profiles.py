import unittest
from datetime import date

from output.html import build_dashboard_html
from intelligence.normalization import normalize_dashboard_data, refresh_time_sensitive_recommendations
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

    def test_dashboard_shows_only_one_link_per_social_platform(self):
        html = build_dashboard_html({
            "date": "2026-10-30",
            "headline": "测试",
            "social_profiles": [{
                "title_cn": "湮灭之潮",
                "title_en": "Tides of Annihilation",
                "accounts": [
                    {"platform": "steam", "url": "https://store.steampowered.com/app/3292470/", "status": "official_confirmed"},
                    {"platform": "steam", "url": "https://store.steampowered.com/app/3292470/Tides_of_Annihilation/", "status": "official_confirmed"},
                ],
            }],
        })
        self.assertEqual(html.count("Steam · 已确认"), 1)

    def test_domestic_only_card_is_removed_from_main_timeline(self):
        data = normalize_dashboard_data({
            "platform": [{
                "name": "[腾讯游戏-示例游戏-Example Game]",
                "normalized_stage": "open_beta_or_launch",
                "overseas_stage": "",
                "summary_points": ["国内参考：国服公测", "海外节点：未公布"],
                "link": "https://example.com/domestic",
            }]
        })
        self.assertEqual(data["platform_intelligence"], [])

    def test_overseas_timeline_starts_with_preparation(self):
        html = build_dashboard_html({
            "date": "2026-10-30",
            "headline": "测试",
            "platform_intelligence": [{
                "name": "[腾讯游戏-湮灭之潮-Tides of Annihilation]",
                "overseas_stage": "overseas_preparation",
                "summary_points": ["海外节点：海外官网与社媒已建立"],
                "link": "https://global.playtoa.com/",
            }],
        })
        self.assertIn("海外准备", html)
        self.assertIn('aria-label="海外发行阶段"', html)

    def test_past_quarter_is_not_presented_as_current_intervention_window(self):
        data = {
            "retail_innovation": [{
                "marketing_opportunity": "创作者合作与社区投放建议 Q2-Q3 时间段重点介入",
                "summary_points": ["营销成熟度：中｜机会：创作者合作与社区投放建议 Q2-Q3 时间段重点介入"],
                "event_date": "Q3 2026",
            }]
        }
        refreshed = refresh_time_sensitive_recommendations(data, date(2026, 10, 30))
        card = refreshed["retail_innovation"][0]
        self.assertEqual(
            card["marketing_opportunity"],
            "当前需依据最新官方节点重新评估：创作者合作与社区投放。",
        )
        self.assertNotIn("Q2-Q3", card["marketing_opportunity"])
        self.assertNotIn("Q2-Q3 时间段重点介入", card["summary_points"][0])
        self.assertEqual(card["event_date"], "Q3 2026")

    def test_current_quarter_is_shown_as_remaining_window(self):
        data = {"retail_innovation": [{"marketing_opportunity": "建议 Q4 重点介入"}]}
        refreshed = refresh_time_sensitive_recommendations(data, date(2026, 10, 30))
        self.assertEqual(
            refreshed["retail_innovation"][0]["marketing_opportunity"],
            "建议 本季度剩余窗口 重点介入",
        )

    def test_future_quarter_remains_unchanged(self):
        data = {"retail_innovation": [{"marketing_opportunity": "建议 Q1 2027 介入"}]}
        refreshed = refresh_time_sensitive_recommendations(data, date(2026, 10, 30))
        self.assertEqual(refreshed["retail_innovation"][0]["marketing_opportunity"], "建议 Q1 2027 介入")

    def test_quarter_refresh_is_idempotent_for_existing_preview(self):
        data = {"retail_innovation": [{
            "marketing_opportunity": (
                "当前需依据最新官方节点重新评估：创作者合作；"
                "原建议窗口已结束，当前需依据最新官方节点重新评估。"
            )
        }]}
        refreshed = refresh_time_sensitive_recommendations(data, date(2026, 10, 30))
        self.assertEqual(
            refreshed["retail_innovation"][0]["marketing_opportunity"],
            "当前需依据最新官方节点重新评估：创作者合作。",
        )


if __name__ == "__main__":
    unittest.main()
