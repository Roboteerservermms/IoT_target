import vlc
'''
vlc event signal
MediaPlayerNothingSpecial: vlc is idle, just waiting to issue a command
MediaPlayerOpening: vlc is opening the media resource locator (MRL)
MediaPlayerBuffering (int cache): vlc is buffering
MediaPlayerPlaying: vlc is playing media
MediaPlayerPaused: vlc is paused
MediaPlayerStopped: vlc is in a stopped state
MediaPlayerForward: vlc fast forward through media (this will never be called)
MediaPlayerBackward: vlc is rewinding (this will never be called)
MediaPlayerEncounteredError: vlc encountered an error and cannot continue
MediaPlayerEndReached: vlc has reached the end of the current playlist
MediaPlayerTimeChanged: Time has changed
MediaPlayerPositionChanged: The progress has changed
MediaPlayerSeekableChanged: Whether the searchable state of the streaming media has changed (true means searchable, false means not searchable)
MediaPlayerPausableChanged: Whether the media can be paused or not (true means it can be paused, false means it cannot be paused)
MediaPlayerMediaChanged: The media has changed
MediaPlayerTitleChanged: The title has changed (DVD/Blu-ray)
MediaPlayerChapterChanged: Chapter changed (DVD/Blu-ray)
MediaPlayerLengthChanged: (Only for Mozilla in vlc version <2.2.0) length has changed
MediaPlayerVout: The number of video outputs has changed
MediaPlayerMuted: Mute
MediaPlayerUnmuted: Unmute
MediaPlayerAudioVolume: The volume has changed
''' 
def onEnd(event):
    global doTrashCode
    if event.type == vlc.EventType.MediaPlayerEndReached:
        doTrashCode = True

class VlcPlayer:
    '''
    args: VLC인스턴스 생성옵션
    '''
    
    def __init__(self, *args):
        global instance
        instance = vlc.Instance(*args)
        self.medialist = instance.media_list_new()
        self.medialistplayer = instance.media_list_player_new()
        self.medialistplayer.set_playback_mode(vlc.PlaybackMode.loop)
        self.mediaplayer = instance.media_player_new()
        self.mediaplayer.set_fullscreen(True)

    def add_media(self, mrl):
        '''
        스트리밍 url주소 또는 로컬 재생파일을 설정
        :param mrl: 스트리밍주소
        :return:
        '''
        new_media = instance.media_new(mrl)
        self.medialist.add_media(new_media)
        self.medialistplayer.set_media_list(self.media_list)
        return self.medialist.count

    def find_item(self, item):
        new_media = instance.media_new(item)
        return self.medialist.index_of_item(item)

    def play(self, index=None):
        '''
        미디어 재생
        :param path:
        :return: 성공:0, 실패:-1
        '''
        if index:
            return self.medialistplayer.play_item_at_index(index)
        else:
            return self.medialistplayer.play()

    def pause(self):
        '''
        재생 멈춤
        :return:
        '''
        self.medialistplayer.pause()
 
    def resume(self):
        '''
        재생 다시 시작
        :return:
        '''
        self.medialistplayer.set_pause(0)
 
    def stop(self):
        '''
        재생 멈춤
        :return:
        '''
        self.medialistplayer.stop()
 
    def release(self):
        '''
        미디어 소스 초기화
        :return:
        '''
        return self.medialistplayer.release()
 
    def is_playing(self):
        '''
        플레이 상태 확인
        :return: 재생중 : 1, 재생중이지 않음 : 0
        '''
        return self.medialistplayer.is_playing()
 
    def get_time(self):
        '''
        Elapsed time, return millisecond value
        :return:
        '''
        return self.mediaplayer.get_time()
 
    def set_time(self, ms):
        '''
        미디어 특정시간으로 이동.
        :param ms:
        :return: 성공 : 0, 실패 : -1
        '''
        return self.mediaplayer.get_time(ms)
 
    # The total length of audio and video, returns the value in milliseconds
    def get_length(self):
        '''
        미디어소스의 재생길이
        :return: 재생길이(ms)
        '''
        return self.mediaplayer.get_length()
 
    def get_volume(self):
        '''
        :return: 현재 볼륨 상태 값 (0~100)
        '''
        return self.mediaplayer.audio_get_volume()
 
    def set_volume(self, volume):
        '''
        볼륨 설정
        :param volume: 0~100 사이 값
        :return:
        '''
        return self.mediaplayer.audio_set_volume(volume)
 
    # Return to the current state: playing; paused; other
    def get_state(self):
        '''
        현재 플레이어 상태 확인
        :return: playing : 1, paused : 0, 그외 -1
        '''
        state = self.medialistplayer.get_state()
        if state == vlc.State.Playing:
            return 1
        elif state == vlc.State.Paused:
            return 0
        else:
            return -1
 
    def get_position(self):
        '''
        현재 playback 진척도
        :return: 미디어의 재생율 (1 이하 소숫점)
        '''
        return self.mediaplayer.get_position()
 
    def set_position(self, float_val):
        '''
        특정 재생율로 미디어의 재생위치를 변경.
        :param float_val: 0~1 사이 float값
        :return:
        '''
        return self.mediaplayer.set_position(float_val)
 
    def get_rate(self):
        '''
        :return: 재생속도
        '''
        return self.mediaplayer.get_rate()
 
    def set_rate(self, rate):
        '''
        재생속도 설정
        :param rate: 배속
        :return:
        '''
        return self.mediaplayer.set_rate(rate)
 
    def set_ratio(self, ratio):
        '''
        Set the aspect ratio (such as "16:9", "4:3")
        :param ratio:
        :return:
        '''
        # Must be set to 0, otherwise the screen width and height cannot be modified
        self.mediaplayer.video_set_scale(0) 
        self.mediaplayer.video_set_aspect_ratio(ratio)
 
    def add_callback(self, event_type, callback):
        '''
        콜백 listener 설정
        :param event_type: vlc listener 환경변수
        :param callback: 콜백함수
        :return:
        '''
        self.medialistplayer.event_manager().event_attach(event_type, callback)
 
    def remove_callback(self, event_type, callback):
        '''
        Remove listener
        :param event_type:
        :param callback:
        :return:
        '''
        self.medialistplayer.event_manager().event_detach(event_type, callback)