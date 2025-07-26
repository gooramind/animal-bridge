# audio_manager.py - 오디오 관리

import pygame
import os
from typing import Dict, Optional
from settings import resource_path

class AudioManager:
    def __init__(self, sound_volume: float = 1.0, music_volume: float = 1.0):
        try:
            pygame.mixer.init()
            # 성공 메시지를 명확하게 출력
            freq, size, channels = pygame.mixer.get_init()
            print(f"✓ Pygame Mixer 초기화 성공! (주파수: {freq}, 채널: {channels})")
        except pygame.error as e:
            # 실패 시 오류 메시지 출력
            print(f"✗ Pygame Mixer 초기화 실패: {e}")

        self.sound_volume = sound_volume
        self.music_volume = music_volume
        
        # 사운드 캐시
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        
        # 기본 사운드 파일 경로
        self.sound_paths = {
            'click': resource_path('assets/Sound/select_002.ogg'),
            'jump': resource_path('assets/Sound/confirmation_001.ogg'),
            'place': resource_path('assets/Sound/switch_002.ogg'),
            'game_over': resource_path('assets/Sound/error_005.ogg'),
            'card_slide': resource_path('assets/Sound/card-slide-2.ogg'),
            'error': resource_path('assets/Sound/error_008.ogg'),
            'tap': resource_path('assets/Sound/tap-a.ogg')
        }
        
        # 사운드 로드
        self.load_sounds()
    
    def load_sounds(self):
        """사운드 파일들을 로드"""
        print("\n--- 사운드 로딩 시작 ---")
        for name, path in self.sound_paths.items():
            print(f"'{name}' 로딩 시도 -> 경로: {path}")
            try:
                if os.path.exists(path):
                    sound = pygame.mixer.Sound(path)
                    sound.set_volume(self.sound_volume)
                    self.sounds[name] = sound
                    print("  -> ✓ 성공!")
                else:
                    print("  -> ✗ 실패: 파일을 찾을 수 없습니다.")
            except pygame.error as e:
                print(f"  -> ✗ 실패: Pygame 오류 - {e}")
        print("--- 사운드 로딩 완료 ---\n")
    
    def play_sound(self, sound_name: str):
        """사운드 재생"""
        if sound_name in self.sounds:
            self.sounds[sound_name].play()
        else:
            print(f"사운드를 찾을 수 없습니다: {sound_name}")
    
    def load_music(self, music_path: str):
        """배경음악 로드"""
        try:
            full_path = resource_path(music_path)
            if os.path.exists(full_path):
                pygame.mixer.music.load(full_path)
                pygame.mixer.music.set_volume(self.music_volume)
                return True
            else:
                print(f"음악 파일을 찾을 수 없습니다: {full_path}")
                return False
        except pygame.error as e:
            print(f"음악 로드 오류: {e}")
            return False
    
    def play_music(self, loops: int = -1):
        """배경음악 재생"""
        try:
            pygame.mixer.music.play(loops)
        except pygame.error as e:
            print(f"음악 재생 오류: {e}")
    
    def stop_music(self):
        """배경음악 정지"""
        pygame.mixer.music.stop()
    
    def pause_music(self):
        """배경음악 일시정지"""
        pygame.mixer.music.pause()
    
    def unpause_music(self):
        """배경음악 재개"""
        pygame.mixer.music.unpause()
    
    def set_sound_volume(self, volume: float):
        """사운드 볼륨 설정 (0.0 - 1.0)"""
        self.sound_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.sound_volume)
    
    def set_music_volume(self, volume: float):
        """음악 볼륨 설정 (0.0 - 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
    
    def get_sound_volume(self) -> float:
        """현재 사운드 볼륨 반환"""
        return self.sound_volume
    
    def get_music_volume(self) -> float:
        """현재 음악 볼륨 반환"""
        return self.music_volume
    
    def add_sound(self, name: str, path: str):
        """새로운 사운드 추가"""
        try:
            full_path = resource_path(path)
            if os.path.exists(full_path):
                sound = pygame.mixer.Sound(full_path)
                sound.set_volume(self.sound_volume)
                self.sounds[name] = sound
                return True
            else:
                print(f"사운드 파일을 찾을 수 없습니다: {full_path}")
                return False
        except pygame.error as e:
            print(f"사운드 추가 오류 ({name}): {e}")
            return False
    
    def remove_sound(self, name: str):
        """사운드 제거"""
        if name in self.sounds:
            del self.sounds[name]
    
    def is_music_playing(self) -> bool:
        """음악이 재생 중인지 확인"""
        return pygame.mixer.music.get_busy()
    
    def fade_out_music(self, time_ms: int):
        """음악 페이드 아웃"""
        pygame.mixer.music.fadeout(time_ms)
    
    def get_available_sounds(self) -> list:
        """사용 가능한 사운드 목록 반환"""
        return list(self.sounds.keys())

# 전역 오디오 매니저 인스턴스
audio_manager = AudioManager()