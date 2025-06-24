from api.repository.topcharts_repository import TopChartsRepository
from datetime import timedelta

class TopChartsService:
    @staticmethod
    def get_top_songs(today):
        try:
            country_codes = ["TW", "JP", "KR", "US"]
            result = {}
            yesterday = today - timedelta(days=1)

            for code in country_codes:
                today_latest = TopChartsRepository.get_latest_by_country_and_date(code, today)
                yesterday_latest = TopChartsRepository.get_latest_by_country_and_date(code, yesterday)

                today_songs = []
                if today_latest:
                    today_songs = TopChartsRepository.get_songs_by_country_and_retrieved_at(code, today_latest)

                yesterday_songs_map = {}
                if yesterday_latest:
                    yesterday_songs_map = TopChartsRepository.get_rank_map_by_country_and_retrieved_at(code, yesterday_latest)

                for song in today_songs:
                    track_id = song['track_id']
                    current_rank = song['rank']
                    prev_rank = yesterday_songs_map.get(track_id)

                    if prev_rank is None:
                        song['rank_change'] = 'NEW'
                    else:
                        diff = prev_rank - current_rank
                        if diff > 0:
                            song['rank_change'] = f'\u2191{diff}'
                        elif diff < 0:
                            song['rank_change'] = f'\u2193{abs(diff)}'
                        else:
                            song['rank_change'] = '-'

                result[code] = today_songs
            return result, None
        except Exception as e:
            return None, str(e) 