# game_core.py

import pygame
import sys
import pymunk
import pymunk.pygame_util
import math
import json
import os
from settings import *
from settings import resource_path
from render_manager import RenderManager
from audio_manager import audio_manager

# ======================================================================================
# 크기 및 위치 조절을 위한 헬퍼 함수
# ======================================================================================
WIDTH, HEIGHT = 1280, 720
BASE_WIDTH, BASE_HEIGHT = 1280, 720

def scale_x(value):
    return int(value * (WIDTH / BASE_WIDTH))

def scale_y(value):
    return int(value * (HEIGHT / BASE_HEIGHT))

def scale_font(size):
    avg_scale = (WIDTH / BASE_WIDTH + HEIGHT / BASE_HEIGHT) / 2
    return int(size * avg_scale)

# ======================================================================================
# 랭킹 및 진행상황 데이터 관리
# ======================================================================================
RANKING_FILE = 'ranking.json'
PROGRESS_FILE = 'progress.json'

def load_rankings():
    try:
        with open(resource_path(RANKING_FILE), 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        num_stages = len(STAGE_DATA)
        return {str(i): [] for i in range(1, num_stages + 1)}

def save_rankings(data):
    with open(RANKING_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def add_ranking_entry(stage, name, blocks, time_seconds, eaten_count):
    rankings = load_rankings()
    stage_key = str(stage)
    new_entry = {"name": name, "blocks": blocks, "time": time_seconds, "eaten": eaten_count}
    if stage_key not in rankings:
        rankings[stage_key] = []
    rankings[stage_key].append(new_entry)
    
    rankings[stage_key].sort(key=lambda x: (x['blocks'], x.get('eaten', 0), x['time']))
    
    rankings[stage_key] = rankings[stage_key][:10]
    save_rankings(rankings)

def load_progress():
    try:
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {'highest_unlocked_stage': 1}

def save_progress(data):
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def has_player_cleared_stage(player_name, stage_num):
    rankings = load_rankings()
    stage_rankings = rankings.get(str(stage_num), [])
    for record in stage_rankings:
        if record.get("name") == player_name:
            return True
    return False

# ======================================================================================
# 게임 오브젝트 클래스들
# ======================================================================================
class Player:
    def __init__(self, space, pos):
        self.start_pos = pos
        self.body = pymunk.Body(10, float('inf'), body_type=pymunk.Body.DYNAMIC)
        self.body.position = self.start_pos
        self.custom_gravity_force = scale_y(18000)
        self.shape = pymunk.Circle(self.body, scale_x(20))
        self.shape.elasticity = 0.1
        self.shape.friction = 0.7
        self.shape.color = RED
        player_mask = TERRAIN_CATEGORY | CEILING_CATEGORY | ANIMAL_CATEGORY
        self.shape.filter = pymunk.ShapeFilter(categories=PLAYER_CATEGORY, mask=player_mask)
        self.shape.collision_type = PLAYER_COLLISION_TYPE
        space.add(self.body, self.shape)
        self.is_grounded = False

    def update(self, space):
        self.body.apply_force_at_local_point((0, self.custom_gravity_force))
        self.is_grounded = False
        def check_grounding(arbiter):
            if abs(arbiter.normal.y) > 0.7: self.is_grounded = True
        self.body.each_arbiter(check_grounding)

    def set_horizontal_velocity(self, new_vx):
        self.body.velocity = (new_vx, self.body.velocity.y)

    def jump(self):
        if self.is_grounded:
            jump_impulse = scale_y(-4000)
            self.body.velocity = (self.body.velocity.x, 0)
            self.body.apply_impulse_at_local_point((0, jump_impulse))
            audio_manager.play_sound('jump')
    
    def respawn(self):
        self.body.position = self.start_pos
        self.body.velocity = (0, 0)
        self.body.angular_velocity = 0
        self.body.angle = 0

    def draw(self, screen):
        pos = (int(self.body.position.x), int(self.body.position.y))
        radius = scale_x(20)
        shadow_pos = (pos[0] + scale_x(3), pos[1] + scale_y(3))
        pygame.draw.circle(screen, (80, 0, 0), shadow_pos, radius)
        pygame.draw.circle(screen, (255, 50, 50), pos, radius)
        pygame.draw.circle(screen, (200, 0, 0), pos, radius, int(scale_x(4)))
        eye_offset, eye_radius = scale_x(7), scale_x(4)
        left_eye, right_eye = (pos[0] - eye_offset, pos[1] - scale_y(6)), (pos[0] + eye_offset, pos[1] - scale_y(6))
        pygame.draw.circle(screen, WHITE, left_eye, eye_radius)
        pygame.draw.circle(screen, WHITE, right_eye, eye_radius)
        pygame.draw.circle(screen, BLACK, left_eye, max(1, eye_radius - scale_x(2)))
        pygame.draw.circle(screen, BLACK, right_eye, max(1, eye_radius - scale_x(2)))
        mouth_center, mouth_radius = (pos[0], pos[1] + scale_y(8)), scale_x(8)
        pygame.draw.arc(screen, BLACK, (mouth_center[0] - mouth_radius//2, mouth_center[1] - mouth_radius//2, mouth_radius, mouth_radius), 0, 3.14159, int(scale_x(2)))

class AnimalBlock:
    def __init__(self, space, pos, animal_name, block_scale, angle_degrees=0, is_ui_element=False):
        self.name, self.is_ui_element, self.head_part_offsets = animal_name, is_ui_element, []
        self.image = None
        self.is_dying = False
        self.death_time = 0
        self.death_duration = 300
        
        hash_value = hash(animal_name)
        r, g, b = (hash_value & 0xFF0000) >> 16, (hash_value & 0x00FF00) >> 8, hash_value & 0x0000FF
        self.icon_color, self.body_color, self.face_color, self.eye_color = (r, g, b), (65, 105, 225, 255), (255, 165, 0, 255), BLACK
        self.block_shape_str = ANIMAL_DATA.get(self.name, [])
        try:
            image_path = resource_path(os.path.join('assets', 'img', f'{self.name}.png'))
            self.original_image = pygame.image.load(image_path).convert_alpha()
            self.image = self.original_image
        except Exception as e:
            print(f"'{self.name}' 이미지 로드 실패: {e}")
            self.image = self.original_image = None

        if is_ui_element:
            self.rect = pygame.Rect(pos[0], pos[1], 0, 0)
            return

        self.body, self.body.position = pymunk.Body(body_type=pymunk.Body.DYNAMIC), pos
        self.body.angle = math.radians(angle_degrees)
        if not self.block_shape_str: return
        
        height = len(self.block_shape_str)
        width = len(self.block_shape_str[0]) if height > 0 else 0
        
        scale, self.shapes, head_part_local_coords = block_scale, [], []

        if self.image: 
            self.image = pygame.transform.scale(self.original_image, (int(width * scale), int(height * scale)))
        
        for r_index, row in enumerate(self.block_shape_str):
            for c_index, char in enumerate(row):
                if char in ('1', '2'):
                    x_offset, y_offset = (c_index - width / 2 + 0.5) * scale, (r_index - height / 2 + 0.5) * scale
                    if char == '2': head_part_local_coords.append((x_offset, y_offset))
                    half = scale / 2
                    verts = [(-half + x_offset, -half + y_offset), ( half + x_offset, -half + y_offset), ( half + x_offset,  half + y_offset), (-half + x_offset,  half + y_offset)]
                    square_shape = pymunk.Poly(self.body, verts)
                    square_shape.elasticity, square_shape.friction = 0.2, 1.0
                    animal_mask = PLAYER_CATEGORY | ANIMAL_CATEGORY | TERRAIN_CATEGORY
                    square_shape.filter = pymunk.ShapeFilter(categories=ANIMAL_CATEGORY, mask=animal_mask)
                    if self.image: square_shape.color = (0, 0, 0, 0)
                    else: square_shape.color = self.body_color
                    self.shapes.append(square_shape)

        if self.name in CARNIVORES and head_part_local_coords: self.head_part_offsets = [pymunk.Vec2d(x, y) for x, y in head_part_local_coords]
        for s in self.shapes: s.mass = 100
        space.add(self.body, *self.shapes)

    def draw(self, screen):
        if self.is_dying:
            elapsed = pygame.time.get_ticks() - self.death_time
            if elapsed < self.death_duration:
                progress = 1.0 - (elapsed / self.death_duration)
                width = int(self.image.get_width() * progress)
                height = int(self.image.get_height() * progress)
                if width > 0 and height > 0:
                    scaled_image = pygame.transform.scale(self.image, (width, height))
                    rotated_image = pygame.transform.rotate(scaled_image, math.degrees(self.body.angle) * -1)
                    rect = rotated_image.get_rect(center=self.body.position)
                    screen.blit(rotated_image, rect.topleft)
            return

        if self.image:
            rotated_image = pygame.transform.rotate(self.image, math.degrees(self.body.angle) * -1)
            rect = rotated_image.get_rect(center=self.body.position)
            screen.blit(rotated_image, rect.topleft)
        else: self.draw_details(screen)

    def draw_details(self, screen):
        if self.is_ui_element or self.name not in CARNIVORES or not self.head_part_offsets: return
        head_world_pos = self.body.local_to_world(self.head_part_offsets[0])
        eye_radius = scale_x(4)
        left_eye_pos, right_eye_pos = (head_world_pos.x - scale_x(8), head_world_pos.y - scale_y(5)), (head_world_pos.x + scale_x(8), head_world_pos.y - scale_y(5))
        pygame.draw.circle(screen, self.eye_color, left_eye_pos, eye_radius)
        pygame.draw.circle(screen, self.eye_color, right_eye_pos, eye_radius)

    def start_dying(self):
        if not self.is_dying:
            self.is_dying = True
            self.death_time = pygame.time.get_ticks()

class Flag:
    def __init__(self, pos):
        self.base_pos = pos
        self.pole_rect = pygame.Rect(0,0,0,0)
        self.cloth_points = []
        self.pole_color, self.cloth_color = (192, 192, 192), (220, 20, 60)
        self.update_pos()

    def update_pos(self):
        pos_x, pos_y = self.base_pos
        scaled_pos = (scale_x(pos_x), scale_y(pos_y))
        pole_height, pole_width = scale_y(60), scale_x(5)
        self.pole_rect = pygame.Rect(scaled_pos[0], scaled_pos[1] - pole_height, pole_width, pole_height)
        self.cloth_points = [(scaled_pos[0] + pole_width, scaled_pos[1] - pole_height), 
                             (scaled_pos[0] + pole_width, scaled_pos[1] - pole_height + scale_y(25)), 
                             (scaled_pos[0] + pole_width + scale_x(40), scaled_pos[1] - pole_height + scale_y(12.5))]

    def draw(self, screen):
        pygame.draw.rect(screen, self.pole_color, self.pole_rect)
        pygame.draw.polygon(screen, self.cloth_color, self.cloth_points)

# ======================================================================================
# 물리 시스템 관련 함수들
# ======================================================================================
def create_static_body(space, pos, size, category, mask):
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    body.position = pos
    shape = pymunk.Poly.create_box(body, size)
    shape.elasticity, shape.friction = 0.4, 0.9
    shape.color = (0, 0, 0, 0)
    shape.filter = pymunk.ShapeFilter(categories=category, mask=mask)
    space.add(body, shape)
    return body, shape

def setup_level(space, terrain_specs):
    terrain_mask = PLAYER_CATEGORY | ANIMAL_CATEGORY
    terrain_bodies = []
    for spec in terrain_specs:
        pos_x, pos_y, size_w, size_h = spec
        center_pos, size = (scale_x(pos_x), scale_y(pos_y)), (scale_x(size_w), scale_y(size_h))
        body, shape = create_static_body(space, center_pos, size, TERRAIN_CATEGORY, terrain_mask)
        terrain_bodies.append((body, shape))
    create_static_body(space, (WIDTH / 2, scale_y(-10)), (WIDTH, scale_y(20)), CEILING_CATEGORY, PLAYER_CATEGORY)
    create_static_body(space, (scale_x(-10), HEIGHT / 2), (scale_x(20), HEIGHT), TERRAIN_CATEGORY, terrain_mask)
    create_static_body(space, (WIDTH + scale_x(10), HEIGHT / 2), (scale_x(20), HEIGHT), TERRAIN_CATEGORY, terrain_mask)
    create_static_body(space, (WIDTH / 2, HEIGHT + scale_y(10)), (WIDTH, scale_y(20)), TERRAIN_CATEGORY, terrain_mask)
    return terrain_bodies

def get_terrain_rects(terrain_specs):
    terrain_rects = []
    for spec in terrain_specs:
        pos_x, pos_y, size_w, size_h = spec
        center_x, center_y = scale_x(pos_x), scale_y(pos_y)
        width, height = scale_x(size_w), scale_y(size_h)
        rect = pygame.Rect(center_x - width//2, center_y - height//2, width, height)
        terrain_rects.append(rect)
    return terrain_rects

# ======================================================================================
# 게임 상태 관리
# ======================================================================================
class GameState:
    def __init__(self):
        self.current_state = "start_menu"
        self.player_name = ""
        self.selected_stage = 1
        self.sound_volume = 1.0
        self.highest_unlocked = 1
        
    def change_state(self, new_state, data=None):
        self.current_state = new_state
        if data:
            if "player_name" in data: self.player_name = data["player_name"]
            if "selected_stage" in data: self.selected_stage = data["selected_stage"]
            if "volume" in data: self.sound_volume = data["volume"]

# ======================================================================================
# 게임 내 도움말 팝업 함수
# ======================================================================================
def handle_in_game_help(screen, clock, render_manager):
    scroll_y, dragging_scrollbar = 0, False
    _, text_area_rect, scroll_bar_rect, back_button_rect, text_content_height = render_manager.prepare_description_assets()
    text_surface = render_manager.text_surface_cache
    max_scroll_y = max(0, text_content_height - text_area_rect.height)

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    paused = True
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_ESCAPE):
                audio_manager.play_sound('click'); paused = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if back_button_rect.collidepoint(event.pos):
                        audio_manager.play_sound('click'); paused = False
                    if scroll_bar_rect.collidepoint(event.pos):
                        dragging_scrollbar = True
                if event.button == 4: scroll_y = max(0, scroll_y - 40)
                if event.button == 5: scroll_y = min(max_scroll_y, scroll_y + 40)
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                dragging_scrollbar = False
            if event.type == pygame.MOUSEMOTION and dragging_scrollbar and max_scroll_y > 0:
                mouse_y_rel = event.pos[1] - scroll_bar_rect.y
                scroll_ratio = max(0, min(1, mouse_y_rel / scroll_bar_rect.height))
                scroll_y = scroll_ratio * max_scroll_y

        screen.blit(overlay, (0, 0))
        ui_elements = {'text_area_rect': text_area_rect, 'scroll_bar_rect': scroll_bar_rect, 'back_button_rect': back_button_rect, 'text_content_height': text_content_height}
        render_manager.render_description_screen(text_surface, scroll_y, ui_elements, button_text="닫기")
        
        pygame.display.flip()
        clock.tick(FPS)

# ======================================================================================
# 게임 플레이 핵심 로직
# ======================================================================================
def game_play_logic(screen, clock, stage_level, player_name_param, render_manager):
    stage_data = STAGE_DATA.get(str(stage_level), STAGE_DATA["1"])
    available_animals, terrain_specs = stage_data["available_animals"], stage_data["terrain"]
    has_hazard_floor = stage_data.get("has_hazard_floor", False)

    space = pymunk.Space()
    space.gravity = (0, scale_y(981))
    
    setup_level(space, terrain_specs)
    
    player = Player(space, (scale_x(80), scale_y(280)))
    
    goal_coords = stage_data.get("goal_pos", (1200, 300))
    goal_flag = Flag(goal_coords)

    game_objects, to_be_eaten, dragging_animal = [], [], None
    blocks_used_count, eaten_blocks_count, start_time = 0, 0, pygame.time.get_ticks()
    
    player_is_dead = False
    animal_usage_counts = {name: 1 for name in available_animals}

    ui_animals = []
    for name in available_animals:
        ui_animal = AnimalBlock(space, (0,0), name, 0, is_ui_element=True)
        ui_animals.append(ui_animal)
    
    game_over_processed = False
    pause_start_time = 0

    while True:
        goal_flag.update_pos()
        goal_area = pygame.Rect(goal_flag.pole_rect.right - scale_x(10), goal_flag.pole_rect.top, scale_x(40), scale_y(60))
        restart_button_rect = pygame.Rect(scale_x(20), scale_y(20), scale_x(150), scale_y(50))
        block_scale = WIDTH / (BASE_WIDTH / 56.25)
        
        help_button_rect = pygame.Rect(restart_button_rect.right + scale_x(10), scale_y(20), scale_y(50), scale_y(50))
        help_font = pygame.font.SysFont("malgungothic", scale_font(40), bold=True)
        
        mouse_pos = pygame.mouse.get_pos()
        help_button_hover = help_button_rect.collidepoint(mouse_pos)

        for i, ui_animal in enumerate(ui_animals):
            shape_h = len(ui_animal.block_shape_str)
            shape_w = len(ui_animal.block_shape_str[0]) if shape_h > 0 else 1
            max_dim = scale_x(60)
            aspect_ratio = shape_h / shape_w if shape_w > 0 else 1
            ui_width = max_dim if shape_w >= shape_h else max_dim / aspect_ratio
            ui_height = max_dim * aspect_ratio if shape_w >= shape_h else max_dim
            ui_animal.rect.size = (ui_width, ui_height)
            if ui_animal.original_image: ui_animal.image = pygame.transform.scale(ui_animal.original_image, (int(ui_width), int(ui_height)))
            row, col = i // 7, i % 7
            cell_center_x, cell_center_y = scale_x(140) + col * scale_x(160), HEIGHT - scale_y(120) + scale_y(30) + row * scale_y(60)
            ui_animal.rect.center = (cell_center_x, cell_center_y)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if player_is_dead: continue
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB: audio_manager.play_sound('click'); return "stage_select"
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP: player.jump()
                if event.key == pygame.K_r and dragging_animal: dragging_animal["angle_degrees"] = (dragging_animal["angle_degrees"] + 90) % 360
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if help_button_hover:
                    audio_manager.play_sound('click')
                    pause_start_time = pygame.time.get_ticks()
                    handle_in_game_help(screen, clock, render_manager)
                    start_time += (pygame.time.get_ticks() - pause_start_time)
                    continue
                if restart_button_rect.collidepoint(event.pos): audio_manager.play_sound('click'); return "game_play"
                for ui_animal in ui_animals:
                    if ui_animal.rect.collidepoint(event.pos) and not dragging_animal and animal_usage_counts.get(ui_animal.name, 0) > 0:
                        img_w = int(len(ui_animal.block_shape_str[0]) * block_scale) if ui_animal.block_shape_str else 0
                        img_h = int(len(ui_animal.block_shape_str) * block_scale)
                        full_img = pygame.transform.scale(ui_animal.original_image, (img_w, img_h)) if ui_animal.original_image else None
                        dragging_animal = {"name": ui_animal.name, "image": full_img, "angle_degrees": 0}; break
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and dragging_animal:
                drop_zone_w = scale_x(680)
                drop_zone = pygame.Rect((WIDTH / 2) - (drop_zone_w / 2), scale_y(30), drop_zone_w, scale_y(130))
                if drop_zone.collidepoint(event.pos):
                    game_objects.append(AnimalBlock(space, event.pos, dragging_animal["name"], block_scale, angle_degrees=dragging_animal["angle_degrees"]))
                    blocks_used_count += 1; audio_manager.play_sound('place'); animal_usage_counts[dragging_animal["name"]] = 0
                dragging_animal = None

        if player_is_dead:
            if not game_over_processed:
                audio_manager.play_sound('game_over'); render_manager.render_game_over_screen(None, pygame.Rect(0,0,0,0)); pygame.display.flip(); game_over_processed = True
            menu_button_rect = pygame.Rect(0, 0, scale_x(300), scale_y(80)); menu_button_rect.center = (WIDTH / 2, HEIGHT / 2 + scale_y(150))
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and menu_button_rect.collidepoint(event.pos):
                    audio_manager.play_sound('click'); return "main_menu"
            render_manager.render_game_over_screen(None, menu_button_rect); pygame.display.flip(); clock.tick(FPS); continue
            
        player.update(space)
        keys = pygame.key.get_pressed()
        move_speed, target_vx = scale_x(250), 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: target_vx = -move_speed
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]: target_vx = move_speed
        player.set_horizontal_velocity(target_vx)
        
        hazard_y = HEIGHT - scale_y(20)
        player_death_y = hazard_y if has_hazard_floor else HEIGHT + scale_y(50)
        if player.body.position.y > player_death_y:
            player.respawn(); audio_manager.play_sound('error')

        for animal in game_objects[:]:
            if not animal.is_dying:
                should_die = False
                if has_hazard_floor:
                    for shape in animal.shapes:
                        # --- [수정] 각 물리 조각(shape)의 모든 꼭짓점(vertex)을 확인하여 사망 판정 ---
                        world_verts = [shape.body.local_to_world(v) for v in shape.get_vertices()]
                        if any(v.y > hazard_y for v in world_verts):
                            should_die = True
                            break
                elif animal.body.position.y > HEIGHT + scale_y(100):
                    should_die = True
                
                if should_die:
                    animal.start_dying()
                    # destroy 사운드가 없을 경우를 대비해 예외 처리
                    if audio_manager.sounds.get('destroy'):
                        audio_manager.play_sound('destroy')
                    if animal.body in space.bodies:
                        space.remove(animal.body, *animal.shapes)
        # --- 수정 끝 ---


        game_objects = [a for a in game_objects if not (a.is_dying and pygame.time.get_ticks() - a.death_time > a.death_duration)]
        for carnivore in [o for o in game_objects if o.name in CARNIVORES and not o.is_dying]:
            for prey in [o for o in game_objects if o.name not in CARNIVORES and o != carnivore and not o.is_dying]:
                if any(min(s.point_query(carnivore.body.local_to_world(offset)).distance for s in prey.shapes) < scale_x(40) for offset in carnivore.head_part_offsets if prey.shapes):
                    to_be_eaten.append(prey)
        if to_be_eaten:
            eaten_blocks_count += len(to_be_eaten)
            for animal in to_be_eaten:
                if animal in game_objects: 
                    animal.start_dying()
                    if audio_manager.sounds.get('destroy'):
                        audio_manager.play_sound('destroy')
                if animal.body in space.bodies: space.remove(animal.body, *animal.shapes)
            to_be_eaten.clear()

        render_manager.render_background("tilemap"); render_manager.render_terrain(get_terrain_rects(terrain_specs))
        if has_hazard_floor: render_manager.render_hazard_floor()
        player.draw(screen);
        for animal in game_objects: animal.draw(screen)
        goal_flag.draw(screen)
        stats = {"used": blocks_used_count, "eaten": eaten_blocks_count, "time_str": f"{(pygame.time.get_ticks() - start_time) / 1000:.2f}s"}
        render_manager.render_game_ui(ui_animals, dragging_animal, animal_usage_counts, stats, None, restart_button_rect, start_time)
        
        shadow_rect = help_button_rect.move(scale_x(3), scale_y(3))
        pygame.draw.rect(screen, (50, 50, 50), shadow_rect, border_radius=10)
        
        base_color = (200, 200, 200)
        hover_color = (230, 230, 230)
        current_color = hover_color if help_button_hover else base_color
        pygame.draw.rect(screen, current_color, help_button_rect, border_radius=10)

        help_text_surf = help_font.render("?", True, BLACK)
        help_text_rect = help_text_surf.get_rect(center=help_button_rect.center)
        screen.blit(help_text_surf, help_text_rect)

        if goal_area.collidepoint(player.body.position):
            clear_time_seconds = (pygame.time.get_ticks() - start_time) / 1000
            add_ranking_entry(stage_level, player_name_param, blocks_used_count, clear_time_seconds, eaten_blocks_count)
            return "stage_clear", {"stage": stage_level, "blocks": blocks_used_count, "eaten": eaten_blocks_count, "time": clear_time_seconds}
            
        for _ in range(5): space.step(1.0 / (FPS * 5))
        pygame.display.flip(); clock.tick(FPS)

# ======================================================================================
# 메인 게임 클래스
# ======================================================================================
class Game:
    def __init__(self):
        pygame.init()
        global WIDTH, HEIGHT
        self.game_state = GameState()
        progress = load_progress()
        self.game_state.highest_unlocked = progress['highest_unlocked_stage']

        WIDTH, HEIGHT = 1280, 720
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        
        pygame.display.set_caption("Animal Bridge")
        self.clock = pygame.time.Clock()
        self.render_manager = RenderManager(self.screen)
        audio_manager.set_sound_volume(self.game_state.sound_volume)
        
    def run(self):
        while True:
            state = self.game_state.current_state
            if state == "start_menu":
                result = self.handle_start_menu()
                if result: self.game_state.change_state("main_menu", {"player_name": result})
            elif state == "main_menu":
                next_state, _ = self.handle_main_menu()
                if next_state: self.game_state.change_state(next_state)
            elif state == "stage_select":
                next_state, stage = self.handle_stage_select()
                if next_state: self.game_state.change_state(next_state, {"selected_stage": stage})
            elif state == "game_play":
                result = game_play_logic(self.screen, self.clock, self.game_state.selected_stage, self.game_state.player_name, self.render_manager)
                if isinstance(result, tuple) and result[0] == "stage_clear":
                    clear_info = result[1]
                    cleared_stage = clear_info["stage"]
                    if cleared_stage == self.game_state.highest_unlocked and cleared_stage < len(STAGE_DATA):
                        self.game_state.highest_unlocked += 1
                        save_progress({'highest_unlocked_stage': self.game_state.highest_unlocked})
                    self.handle_ending_scene(clear_info)
                    self.game_state.change_state("stage_select")
                elif result == "game_play": continue
                else: self.game_state.change_state(result)
            elif state == "description":
                next_state, _ = self.handle_description()
                if next_state: self.game_state.change_state(next_state)
            elif state == "settings":
                command, value = self.handle_settings()
                if command:
                    self.game_state.change_state(command, value)
            elif state == "ranking":
                next_state, _ = self.handle_ranking()
                if next_state: self.game_state.change_state(next_state)
            else:
                self.game_state.change_state("main_menu")

    def handle_start_menu(self):
        player_name, input_active = "", False
        fonts = {'title': pygame.font.SysFont("malgungothic", scale_font(90), bold=True), 'prompt': pygame.font.SysFont("malgungothic", scale_font(60)), 'input': pygame.font.SysFont("malgungothic", scale_font(50)), 'placeholder': pygame.font.SysFont("malgungothic", scale_font(20), italic=True)}
        pygame.key.set_repeat(500, 50)
        while True:
            input_box = pygame.Rect(WIDTH / 2 - scale_x(200), HEIGHT / 2, scale_x(400), scale_y(80))
            next_button_rect = pygame.Rect(WIDTH / 2 - scale_x(100), HEIGHT / 2 + scale_y(120), scale_x(200), scale_y(80))
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if next_button_rect.collidepoint(event.pos) and player_name:
                        pygame.key.set_repeat(0); pygame.key.stop_text_input(); audio_manager.play_sound('click'); return player_name
                    input_active = input_box.collidepoint(event.pos)
                    if input_active: pygame.key.start_text_input(); pygame.key.set_text_input_rect(input_box)
                    else: pygame.key.stop_text_input()
                if event.type == pygame.TEXTINPUT and input_active: player_name += event.text
                if event.type == pygame.KEYDOWN and input_active:
                    if event.key == pygame.K_RETURN and player_name:
                        pygame.key.set_repeat(0); pygame.key.stop_text_input(); audio_manager.play_sound('click'); return player_name
                    elif event.key == pygame.K_BACKSPACE: player_name = player_name[:-1]
            self.render_manager.render_start_menu(player_name, input_active, input_box, next_button_rect, fonts)
            pygame.display.flip()
            self.clock.tick(FPS)

    def handle_main_menu(self):
        fonts = {'title': pygame.font.SysFont("malgungothic", scale_font(90), bold=True), 'name': pygame.font.SysFont("malgungothic", scale_font(30)), 'button': pygame.font.SysFont("malgungothic", scale_font(60))}
        while True:
            button_rects = {'start': pygame.Rect(WIDTH/2 - scale_x(150), HEIGHT/2, scale_x(300), scale_y(80)), 'desc': pygame.Rect(WIDTH/2 - scale_x(200), HEIGHT/2 + scale_y(100), scale_x(180), scale_y(70)), 'rank': pygame.Rect(WIDTH/2 + scale_x(20), HEIGHT/2 + scale_y(100), scale_x(180), scale_y(70)), 'settings': pygame.Rect(scale_x(30), scale_y(30), scale_x(50), scale_y(50))}
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if button_rects['start'].collidepoint(event.pos): audio_manager.play_sound('click'); return "stage_select", None
                    if button_rects['desc'].collidepoint(event.pos): audio_manager.play_sound('click'); return "description", None
                    if button_rects['settings'].collidepoint(event.pos): audio_manager.play_sound('click'); return "settings", None
                    if button_rects['rank'].collidepoint(event.pos): audio_manager.play_sound('click'); return "ranking", None
                if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB: return "start_menu", None
            self.render_manager.render_main_menu(self.game_state.player_name, button_rects, fonts)
            pygame.display.flip()
            self.clock.tick(FPS)

    def handle_description(self):
        scroll_y, dragging_scrollbar = 0, False
        _, text_area_rect, scroll_bar_rect, back_button_rect, text_content_height = self.render_manager.prepare_description_assets()
        text_surface = self.render_manager.text_surface_cache
        max_scroll_y = max(0, text_content_height - text_area_rect.height)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN and (event.key == pygame.K_ESCAPE or event.key == pygame.K_TAB):
                    audio_manager.play_sound('click'); return "main_menu", None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP: scroll_y = max(0, scroll_y - 30)
                    if event.key == pygame.K_DOWN: scroll_y = min(max_scroll_y, scroll_y + 30)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if back_button_rect.collidepoint(event.pos): audio_manager.play_sound('click'); return "main_menu", None
                        if scroll_bar_rect.collidepoint(event.pos): dragging_scrollbar = True
                    if event.button == 4: scroll_y = max(0, scroll_y - 40)
                    if event.button == 5: scroll_y = min(max_scroll_y, scroll_y + 40)
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1: dragging_scrollbar = False
                if event.type == pygame.MOUSEMOTION and dragging_scrollbar and max_scroll_y > 0:
                    mouse_y_rel = event.pos[1] - scroll_bar_rect.y
                    scroll_ratio = max(0, min(1, mouse_y_rel / scroll_bar_rect.height))
                    scroll_y = scroll_ratio * max_scroll_y
            self.render_manager.render_background("tilemap")
            ui_elements = {'text_area_rect': text_area_rect, 'scroll_bar_rect': scroll_bar_rect, 'back_button_rect': back_button_rect, 'text_content_height': text_content_height}
            self.render_manager.render_description_screen(text_surface, scroll_y, ui_elements)
            pygame.display.flip()
            self.clock.tick(FPS)

    def handle_settings(self):
        dragging_handle = False
        temp_volume = self.game_state.sound_volume
        while True:
            ui_elements = self.render_manager.prepare_settings_assets()
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN and (event.key == pygame.K_ESCAPE or event.key == pygame.K_TAB):
                    audio_manager.play_sound('click'); return "main_menu", {"volume": temp_volume}
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if ui_elements['back_button'].collidepoint(event.pos):
                        audio_manager.play_sound('click'); return "main_menu", {"volume": temp_volume}
                    if ui_elements['sound_handle'].collidepoint(event.pos) or ui_elements['sound_slider'].collidepoint(event.pos):
                        dragging_handle = True
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    dragging_handle = False
                if event.type == pygame.MOUSEMOTION and dragging_handle:
                    handle_rect, slider_rect = ui_elements['sound_handle'], ui_elements['sound_slider']
                    handle_rect.centerx = max(slider_rect.left, min(event.pos[0], slider_rect.right))
                    temp_volume = (handle_rect.centerx - slider_rect.left) / slider_rect.width
                    audio_manager.set_music_volume(temp_volume); audio_manager.set_sound_volume(temp_volume)
            
            self.render_manager.render_settings_screen(temp_volume, ui_elements)
            pygame.display.flip(); self.clock.tick(FPS)

    def handle_ranking(self):
        current_stage_view = 1
        while True:
            left_arrow, right_arrow, back_button = self.render_manager.prepare_ranking_assets()
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN and (event.key == pygame.K_ESCAPE or event.key == pygame.K_TAB): audio_manager.play_sound('click'); return "main_menu", None
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    if back_button.collidepoint(pos): audio_manager.play_sound('click'); return "main_menu", None
                    if left_arrow.collidepoint(pos): audio_manager.play_sound('click'); current_stage_view = max(1, current_stage_view - 1)
                    elif right_arrow.collidepoint(pos): audio_manager.play_sound('click'); current_stage_view = min(len(STAGE_DATA), current_stage_view + 1)
            rankings = load_rankings()
            self.render_manager.render_ranking_screen(current_stage_view, rankings.get(str(current_stage_view), []))
            pygame.display.flip(); self.clock.tick(FPS)

    def handle_stage_select(self):
        selected_stage_num, scroll_y, dragging_scrollbar = None, 0, False
        
        while True:
            stage_rects = []
            button_height, button_margin = scale_y(80), scale_y(20)
            list_width, start_y = scale_x(800), scale_y(200)

            for i in range(len(STAGE_DATA)):
                rect = pygame.Rect((WIDTH - list_width) / 2, start_y + i * (button_height + button_margin), list_width, button_height)
                stage_rects.append(rect)
            
            content_height = len(stage_rects) * (button_height + button_margin)
            view_height = HEIGHT - start_y
            max_scroll_y = max(0, content_height - view_height + button_margin)
            scroll_bar_rect = pygame.Rect(stage_rects[0].right + scale_x(20), start_y, scale_x(20), view_height)
            back_button_rect = pygame.Rect(scale_x(30), scale_y(30), scale_x(180), scale_y(70))

            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if not selected_stage_num:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            if back_button_rect.collidepoint(event.pos): audio_manager.play_sound('click'); return "main_menu", None
                            if scroll_bar_rect.collidepoint(event.pos): dragging_scrollbar = True
                            for i, rect in enumerate(stage_rects):
                                if rect.move(0, -scroll_y).collidepoint(event.pos) and (i + 1) <= self.game_state.highest_unlocked:
                                    selected_stage_num = i + 1; audio_manager.play_sound('click'); break
                        elif event.button == 4: scroll_y = max(0, scroll_y - 40)
                        elif event.button == 5: scroll_y = min(max_scroll_y, scroll_y + 40)
                    if event.type == pygame.MOUSEBUTTONUP and event.button == 1: dragging_scrollbar = False
                    if event.type == pygame.MOUSEMOTION and dragging_scrollbar and max_scroll_y > 0:
                        mouse_y_rel = event.pos[1] - scroll_bar_rect.y
                        scroll_y = max(0, min(1, mouse_y_rel / scroll_bar_rect.height)) * max_scroll_y
                else:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        popup_rect = pygame.Rect(0, 0, scale_x(600), scale_y(400)); popup_rect.center = (WIDTH / 2, HEIGHT / 2)
                        start_button_rect = pygame.Rect(0, 0, scale_x(300), scale_y(80)); start_button_rect.center = (popup_rect.centerx, popup_rect.bottom - scale_y(80))
                        if start_button_rect.collidepoint(event.pos): audio_manager.play_sound('click'); return "game_play", selected_stage_num
                        if not popup_rect.collidepoint(event.pos): selected_stage_num = None

            self.render_manager.render_stage_select(stage_rects, selected_stage_num, back_button_rect, scroll_y, scroll_bar_rect, content_height, view_height, self.game_state.highest_unlocked)
            pygame.display.flip()
            self.clock.tick(FPS)
            
    def handle_ending_scene(self, clear_info):
        stage_num, used, eaten, time_val = clear_info["stage"], clear_info["blocks"], clear_info["eaten"], clear_info["time"]
        time_str = f"{int(time_val / 60)}분 {time_val % 60:.2f}초"
        while True:
            next_button_rect = pygame.Rect(0, 0, scale_x(200), scale_y(80))
            next_button_rect.center = (WIDTH / 2, HEIGHT / 2 + scale_y(280))
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and next_button_rect.collidepoint(event.pos):
                    audio_manager.play_sound('click'); return
            self.render_manager.render_ending_scene(stage_num, used, eaten, time_str, next_button_rect)
            pygame.display.flip(); self.clock.tick(FPS)

def main():
   game = Game()
   game.run()

if __name__ == '__main__':
   main()