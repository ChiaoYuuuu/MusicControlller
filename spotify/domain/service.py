def build_song_response(song_data, room):
    # 處理商業邏輯，如組合 artist 字串、判斷 skip_votes 等
    artist_string = ", ".join([artist['name'] for artist in song_data['artists']])
    return {
        'title': song_data['name'],
        'artist': artist_string,
        'duration': song_data['duration_ms'],
        'image_url': song_data['album']['images'][0]['url'],
        'is_playing': song_data['is_playing'],
        'skip_votes': len(song_data['skip_votes']),
        'votes_required': room.votes_to_skip,
        'id': song_data['id']
    }