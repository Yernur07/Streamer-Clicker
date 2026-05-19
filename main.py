import pygame
import sys
import random
import json

pygame.init()

WIDTH = 1280
HEIGHT = 720
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Streamer Clicker")
clock = pygame.time.Clock()

class InteractiveElement:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

class Streamer(InteractiveElement):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self.money_per_click = 1

    def click(self, game_state_obj):
        game_state_obj.coins += self.money_per_click

class ShopItem(InteractiveElement):
    def __init__(self, x, y, width, height, name, cost, click_bonus):
        super().__init__(x, y, width, height)
        self.name = name
        self.cost = int(cost)
        self.level = 0
        self.click_bonus = click_bonus

    def buy(self, game_state_obj):
        if game_state_obj.coins >= self.cost:
            game_state_obj.coins -= self.cost
            self.level += 1
            game_state_obj.streamer.money_per_click += self.click_bonus
            self.cost = (self.cost * 15) // 10  
            return True
        return False

class WeaponSkin:
    def __init__(self, name, price, rarity):
        self.name = name
        self.price = price
        self.rarity = rarity

class GameProgress:
    def __init__(self, streamer_obj):
        self.coins = 0
        self.subscribers = 0
        self.viewers = 0
        self.inventory = []
        self.streamer = streamer_obj
        self.load_game()

    def save_game(self, mouse_item):
        data = {
            "coins": self.coins,
            "subscribers": self.subscribers,
            "viewers": self.viewers,
            "money_per_click": self.streamer.money_per_click,
            "mouse_level": mouse_item.level,
            "mouse_cost": mouse_item.cost
        }
        with open("save_data.json", "w") as file:
            json.dump(data, file)

    def load_game(self):
        try:
            with open("save_data.json", "r") as file:
                data = json.load(file)
                self.coins = data.get("coins", 0)
                self.subscribers = data.get("subscribers", 0)
                self.viewers = data.get("viewers", 0)
                self.streamer.money_per_click = data.get("money_per_click", 1)
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            self.coins = 0
            self.subscribers = 0
            self.viewers = 0
            self.streamer.money_per_click = 1
            return {}

def chat_message_generator():
    nicknames = ["ka1ser_007", "erubissss", "odyvan16", "ivka_007", "gik3y", "romme1", "che_pauk113", "d_a_n_4_1_k", "cloudez", "ten","ekjlep4ka"]
    phrases = ["Привет! 💜", "Давай!", "Мяу", "GG!", "осуждаю", "EZ", "Жесть катка!", "WW", "бб"]
    colors = [(138, 43, 226), (255, 105, 180), (50, 205, 50), (30, 144, 255), (255, 69, 0)]
    
    while True:
        nick = random.choice(nicknames)
        phrase = random.choice(phrases)
        color = random.choice(colors)
        yield {"text": f"{nick}: {phrase}", "color": color}

streamer_target = Streamer(480, 360, 160, 220)  
progress = GameProgress(streamer_target)
chat_gen = chat_message_generator()

active_chat_messages = [] 
MAX_CHAT_LINES = 8

start_button = pygame.Rect(470, 520, 320, 120)

shop_rect = pygame.Rect(30, 590, 180, 65)
upgrade_rect = pygame.Rect(230, 590, 180, 65)
giveaway_rect = pygame.Rect(430, 590, 180, 65)
marketplace_rect = pygame.Rect(630, 590, 180, 65)

shop_open = False
close_shop_rect = pygame.Rect(840, 170, 30, 30)  

mouse_upgrade = ShopItem(330, 240, 500, 60, "Gaming Mouse", cost=15, click_bonus=1)
upgrade_open = False
marketplace_open = False

giveaway_open = False      
giveaway_active = False     
giveaway_number = 0         
giveaway_skin = None        
giveaway_timer = 0          

passive_ad_upgrade = ShopItem(330, 240, 500, 60, "Social Media Ad", cost=50, click_bonus=1)

available_skins = [
    WeaponSkin("AK-47 | Slate", 100, "Rare"),
    WeaponSkin("M4A4 | Neo-Noir", 500, "Mythical"),
    WeaponSkin("AWP | Asiimov", 2500, "Legendary")
]

saved_data = progress.load_game()
if saved_data:
    mouse_upgrade.level = saved_data.get("mouse_level", 0)
    mouse_upgrade.cost = saved_data.get("mouse_cost", 15)

try:
    background = pygame.image.load("assets/background.png")
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
    room = pygame.image.load("assets/room1.jpg")
    room = pygame.transform.scale(room, (WIDTH, HEIGHT))
    
    img_coins = pygame.image.load("assets/ui_coins.png")
    img_coins = pygame.transform.scale(img_coins, (240, 60))
    
    img_subs = pygame.image.load("assets/ui_subs.png")
    img_subs = pygame.transform.scale(img_subs, (240, 60))
    
    img_viewers = pygame.image.load("assets/ui_viewers.png")
    img_viewers = pygame.transform.scale(img_viewers, (240, 60))

    btn_shop = pygame.image.load("assets/ui_shop.png")
    btn_shop = pygame.transform.scale(btn_shop, (180, 65))
    
    btn_upgrade = pygame.image.load("assets/ui_upgrade.png")
    btn_upgrade = pygame.transform.scale(btn_upgrade, (180, 65))
    
    btn_giveaway = pygame.image.load("assets/ui_giveways.png")
    btn_giveaway = pygame.transform.scale(btn_giveaway, (180, 65))
    
    btn_marketplace = pygame.image.load("assets/ui_marketplace.png")
    btn_marketplace = pygame.transform.scale(btn_marketplace, (180, 65))
    
except pygame.error:
    print("Ошибка загрузки картинок! Проверь папку assets.")
    sys.exit()

try:
    ui_font = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 10)
    chat_font = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 9)
except pygame.error:
    ui_font = pygame.font.SysFont("Courier New", 13, bold=True)
    chat_font = pygame.font.SysFont("Courier New", 11, bold=True)

game_state = "menu"

start_button = pygame.Rect(470, 520, 320, 120)

PASSIVE_INCOME_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(PASSIVE_INCOME_EVENT, 1000)

CHAT_UPDATE_EVENT = pygame.USEREVENT + 2
pygame.time.set_timer(CHAT_UPDATE_EVENT, 2000)

running = True
while running:
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == PASSIVE_INCOME_EVENT and game_state == "game":
            passive_income = 1 + passive_ad_upgrade.level
            progress.subscribers += passive_income
            progress.viewers = int(progress.subscribers * 0.15) + random.randint(1, 5)

        if event.type == CHAT_UPDATE_EVENT and game_state == "game":
            if giveaway_active:
                viewer_guess = random.randint(1, 20)
                nicknames = ["ka1ser_007", "erubissss", "odyvan16", "ivka_007", "gik3y", "romme1", "che_pauk113", "d_a_n_4_1_k", "cloudez", "ten","ekjlep4ka"]
                nick = random.choice(nicknames)
                
                new_msg = {"text": f"{nick}: Это число {viewer_guess}?", "color": (30, 144, 255)}
                active_chat_messages.append(new_msg)
                
                if viewer_guess == giveaway_number:
                    giveaway_active = False
                    sub_bonus = giveaway_skin.price * 2
                    progress.subscribers += sub_bonus
                    
                    active_chat_messages.append({"text": f"{nick} УГАДАЛ! Бонус +{sub_bonus} Сабов!", "color": (50, 205, 50)})
                    active_chat_messages.append({"text": f"СИСТЕМА: {giveaway_skin.name} отправлен победителю!", "color": (255, 215, 0)})
                    giveaway_skin = None
            else:
                new_msg = next(chat_gen)
                active_chat_messages.append(new_msg)
                
            if len(active_chat_messages) > MAX_CHAT_LINES:
                active_chat_messages.pop(0)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = pygame.mouse.get_pos()

                if game_state == "menu":
                    if start_button.collidepoint(mouse_pos):
                        game_state = "game"
                        
                elif game_state == "game":
                    if shop_open:
                        if close_shop_rect.collidepoint(mouse_pos):
                            shop_open = False
                        if mouse_upgrade.is_clicked(mouse_pos):
                            mouse_upgrade.buy(progress)
                    
                    elif upgrade_open:
                        if close_shop_rect.collidepoint(mouse_pos): 
                            upgrade_open = False
                        if passive_ad_upgrade.is_clicked(mouse_pos):
                            if progress.coins >= passive_ad_upgrade.cost:
                                progress.coins -= passive_ad_upgrade.cost
                                passive_ad_upgrade.level += 1
                                passive_ad_upgrade.cost = (passive_ad_upgrade.cost * 15) // 10
                    
                    elif marketplace_open:
                        if close_shop_rect.collidepoint(mouse_pos):
                            marketplace_open = False
                        
                        for i in range(len(available_skins) - 1, -1, -1):
                            skin = available_skins[i]
                            skin_click_rect = pygame.Rect(330, 240 + (i * 70), 300, 60)
                            
                            if skin_click_rect.collidepoint(mouse_pos):
                                if progress.coins >= skin.price:
                                    progress.coins -= skin.price
                                    progress.inventory.append(skin)
                                    available_skins.pop(i)
                                    print(f"Куплен скин: {skin.name}")
                                    break
                    
                    elif giveaway_open:
                        if close_shop_rect.collidepoint(mouse_pos):
                            giveaway_open = False
                        
                        start_guess_rect = pygame.Rect(410, 260, 360, 50)
                        if start_guess_rect.collidepoint(mouse_pos) and not giveaway_active:
                            if len(progress.inventory) > 0:
                                giveaway_skin = progress.inventory.pop(0) 
                                giveaway_number = random.randint(1, 20)
                                giveaway_active = True
                                giveaway_open = False
                                
                                active_chat_messages.append({"text": f"СИСТЕМА: Розыгрыш {giveaway_skin.name}!", "color": (255, 215, 0)})
                                active_chat_messages.append({"text": "Загадано число от 1 до 20!", "color": (255, 255, 255)})
                    
                    else:
                        if streamer_target.is_clicked(mouse_pos):
                            streamer_target.click(progress)
                        
                        if shop_rect.collidepoint(mouse_pos):
                            shop_open = True
                            upgrade_open = False      
                            marketplace_open = False  
                            giveaway_open = False
                        elif upgrade_rect.collidepoint(mouse_pos):
                            upgrade_open = True
                            shop_open = False         
                            marketplace_open = False  
                            giveaway_open = False
                        elif marketplace_rect.collidepoint(mouse_pos):
                            marketplace_open = True
                            shop_open = False         
                            upgrade_open = False
                            giveaway_open = False
    
                        elif giveaway_rect.collidepoint(mouse_pos):
                            giveaway_open = True
                            shop_open = False
                            upgrade_open = False
                            marketplace_open = False

    if game_state == "menu":
        screen.blit(background, (0, 0))
        if start_button.collidepoint(mouse_pos):
            glow_surface = pygame.Surface((320, 120), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (0, 255, 100, 45), (0, 0, 320, 120), border_radius=14)
            screen.blit(glow_surface, (470, 520))

    elif game_state == "game":
        screen.blit(room, (0, 0))

        screen.blit(img_coins, (160, 15))
        coins_text = ui_font.render(f"{progress.coins:,}", True, (255, 220, 120))
        screen.blit(coins_text, (260, 44)) 

        screen.blit(img_subs, (430, 15))
        subs_text = ui_font.render(f"{progress.subscribers:,}", True, (210, 120, 255))
        screen.blit(subs_text, (535, 44))  

        screen.blit(img_viewers, (700, 15))
        viewers_text = ui_font.render(f"{progress.viewers:,}", True, (180, 120, 255))
        screen.blit(viewers_text, (805, 44))  

        panel_bg = pygame.Surface((810, 110), pygame.SRCALPHA)
        pygame.draw.rect(panel_bg, (20, 16, 28, 200), (0, 0, 810, 110), border_radius=12)
        pygame.draw.rect(panel_bg, (48, 38, 68), (0, 0, 810, 110), width=2, border_radius=12)
        screen.blit(panel_bg, (15, 575))

        screen.blit(btn_shop, (shop_rect.x, shop_rect.y))
        screen.blit(btn_upgrade, (upgrade_rect.x, upgrade_rect.y))
        screen.blit(btn_giveaway, (giveaway_rect.x, giveaway_rect.y))
        screen.blit(btn_marketplace, (marketplace_rect.x, marketplace_rect.y))

        for rect in [shop_rect, upgrade_rect,giveaway_rect, marketplace_rect]:
            if rect.collidepoint(mouse_pos) and not shop_open:
                hover_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                pygame.draw.rect(hover_surf, (255, 255, 255, 40), (0, 0, rect.width, rect.height), border_radius=6)
                screen.blit(hover_surf, (rect.x, rect.y))

        chat_x = 990
        chat_y = 110
        chat_w = 270
        chat_h = 440

        chat_bg = pygame.Surface((chat_w, chat_h), pygame.SRCALPHA)
        pygame.draw.rect(chat_bg, (15, 10, 20, 180), (0, 0, chat_w, chat_h), border_radius=10)
        pygame.draw.rect(chat_bg, (138, 43, 226, 255), (0, 0, chat_w, chat_h), width=2, border_radius=10)
        screen.blit(chat_bg, (chat_x, chat_y))

        chat_title = ui_font.render("LIVE CHAT", True, (255, 105, 180))
        screen.blit(chat_title, (chat_x + 15, chat_y + 15))

        max_text_width = chat_w - 30 
        
        current_line_index = 0
        for msg in active_chat_messages:
            words = msg["text"].split(' ')
            current_line = ""
            
            for word in words:
                test_line = current_line + (" " if current_line else "") + word
                test_surface = chat_font.render(test_line, True, msg["color"])
                
                if test_surface.get_width() <= max_text_width:
                    current_line = test_line
                else:
                    if current_line_index < MAX_CHAT_LINES:
                        msg_y = chat_y + 45 + (current_line_index * 30)
                        chat_surface = chat_font.render(current_line, True, msg["color"])
                        screen.blit(chat_surface, (chat_x + 15, msg_y))
                        current_line_index += 1
                    current_line = word
            
            if current_line and current_line_index < MAX_CHAT_LINES:
                msg_y = chat_y + 45 + (current_line_index * 30)
                chat_surface = chat_font.render(current_line, True, msg["color"])
                screen.blit(chat_surface, (chat_x + 15, msg_y))
                current_line_index += 1

        if shop_open:
            shop_box = pygame.Surface((560, 360), pygame.SRCALPHA)
            pygame.draw.rect(shop_box, (30, 22, 44, 240), (0, 0, 560, 360), border_radius=14)
            pygame.draw.rect(shop_box, (0, 255, 150), (0, 0, 560, 360), width=3, border_radius=14)
            screen.blit(shop_box, (310, 160))

            shop_header = ui_font.render("STREAMER SHOP", True, (0, 255, 150))
            screen.blit(shop_header, (340, 190))

            pygame.draw.rect(screen, (220, 60, 60), close_shop_rect, border_radius=5)
            close_text = ui_font.render("X", True, (255, 255, 255))
            screen.blit(close_text, (close_shop_rect.x + 10, close_shop_rect.y + 10))

            pygame.draw.rect(screen, (45, 35, 65), mouse_upgrade.rect, border_radius=8)
            if mouse_upgrade.is_clicked(mouse_pos):
                pygame.draw.rect(screen, (60, 50, 85), mouse_upgrade.rect, border_radius=8)
            pygame.draw.rect(screen, (65, 55, 95), mouse_upgrade.rect, width=2, border_radius=8)

            item_name = ui_font.render(f"{mouse_upgrade.name} (Lvl {mouse_upgrade.level})", True, (255, 255, 255))
            item_cost = ui_font.render(f"Cost: {mouse_upgrade.cost}", True, (255, 215, 0) if progress.coins >= mouse_upgrade.cost else (160, 100, 100))
            item_bonus = ui_font.render(f"+1 Click Power", True, (150, 140, 170))

            screen.blit(item_name, (mouse_upgrade.rect.x + 20, mouse_upgrade.rect.y + 15))
            screen.blit(item_bonus, (mouse_upgrade.rect.x + 20, mouse_upgrade.rect.y + 38))
            screen.blit(item_cost, (mouse_upgrade.rect.x + 320, mouse_upgrade.rect.y + 25))

        elif upgrade_open:
            upg_box = pygame.Surface((560, 360), pygame.SRCALPHA)
            pygame.draw.rect(upg_box, (30, 22, 44, 240), (0, 0, 560, 360), border_radius=14)
            pygame.draw.rect(upg_box, (160, 80, 255), (0, 0, 560, 360), width=3, border_radius=14)
            screen.blit(upg_box, (310, 160))

            upg_header = ui_font.render("STREAM UPGRADES", True, (160, 80, 255))
            screen.blit(upg_header, (340, 190))

            pygame.draw.rect(screen, (220, 60, 60), close_shop_rect, border_radius=5)
            close_text = ui_font.render("X", True, (255, 255, 255))
            screen.blit(close_text, (close_shop_rect.x + 10, close_shop_rect.y + 10))

            pygame.draw.rect(screen, (45, 35, 65), passive_ad_upgrade.rect, border_radius=8)
            if passive_ad_upgrade.is_clicked(mouse_pos):
                pygame.draw.rect(screen, (60, 50, 85), passive_ad_upgrade.rect, border_radius=8)
            pygame.draw.rect(screen, (65, 55, 95), passive_ad_upgrade.rect, width=2, border_radius=8)

            u_name = ui_font.render(f"{passive_ad_upgrade.name} (Lvl {passive_ad_upgrade.level})", True, (255, 255, 255))
            u_cost = ui_font.render(f"Cost: {passive_ad_upgrade.cost}", True, (255, 215, 0) if progress.coins >= passive_ad_upgrade.cost else (160, 100, 100))
            u_bonus = ui_font.render(f"+1 Sub/sec", True, (150, 140, 170))

            screen.blit(u_name, (passive_ad_upgrade.rect.x + 20, passive_ad_upgrade.rect.y + 15))
            screen.blit(u_bonus, (passive_ad_upgrade.rect.x + 20, passive_ad_upgrade.rect.y + 38))
            screen.blit(u_cost, (passive_ad_upgrade.rect.x + 320, passive_ad_upgrade.rect.y + 25))

        elif marketplace_open:
            fade_screen = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            fade_screen.fill((10, 8, 15, 180))
            screen.blit(fade_screen, (0, 0))

            m_w, m_h = 700, 450
            m_x, m_y = 280, 110
            pygame.draw.rect(screen, (20, 20, 30, 250), (m_x, m_y, m_w, m_h), border_radius=15)
            pygame.draw.rect(screen, (255, 215, 0), (m_x, m_y, m_w, m_h), width=3, border_radius=15)

            market_title = ui_font.render("MARKETPLACE", True, (255, 215, 0))
            screen.blit(market_title, (m_x + 30, m_y + 25))

            inv_title = ui_font.render("INVENTORY", True, (255, 215, 0))
            screen.blit(inv_title, (m_x + 400, m_y + 25))

            pygame.draw.line(screen, (60, 60, 80), (m_x + 350, m_y + 60), (m_x + 350, m_y + 420), 2)

            pygame.draw.rect(screen, (200, 50, 50), close_shop_rect, border_radius=5)
            close_text = ui_font.render("X", True, (255, 255, 255))
            screen.blit(close_text, (close_shop_rect.x + 10, close_shop_rect.y + 10))

            for i, skin in enumerate(available_skins):
                s_rect = pygame.Rect(m_x + 20, m_y + 70 + (i * 75), 310, 65)
                pygame.draw.rect(screen, (40, 40, 60), s_rect, border_radius=8)
                
                s_name = ui_font.render(skin.name, True, (255, 255, 255))
                s_price = ui_font.render(f"Price: {skin.price} coins", True, (0, 255, 150))
                s_rare = ui_font.render(skin.rarity, True, (200, 200, 200))
                
                screen.blit(s_name, (s_rect.x + 10, s_rect.y + 10))
                screen.blit(s_price, (s_rect.x + 10, s_rect.y + 35))
                screen.blit(s_rare, (s_rect.x + 200, s_rect.y + 35))

            if not progress.inventory:
                empty_txt = ui_font.render("Inventory is empty...", True, (100, 100, 120))
                screen.blit(empty_txt, (m_x + 380, m_y + 80))
            else:
                for i, owned_skin in enumerate(progress.inventory):
                    if i < 5: 
                        inv_txt = ui_font.render(f"- {owned_skin.name}", True, (255, 255, 255))
                        screen.blit(inv_txt, (m_x + 380, m_y + 80 + (i * 30)))

        elif giveaway_open:
            g_box = pygame.Surface((560, 360), pygame.SRCALPHA)
            pygame.draw.rect(g_box, (40, 15, 25, 240), (0, 0, 560, 360), border_radius=14)
            pygame.draw.rect(g_box, (255, 50, 100), (0, 0, 560, 360), width=3, border_radius=14)
            screen.blit(g_box, (310, 160))

            g_header = ui_font.render("STREAM GIVEAWAYS", True, (255, 50, 100))
            screen.blit(g_header, (340, 190))

            pygame.draw.rect(screen, (220, 60, 60), close_shop_rect, border_radius=5)
            close_text = ui_font.render("X", True, (255, 255, 255))
            screen.blit(close_text, (close_shop_rect.x + 10, close_shop_rect.y + 10))

            if len(progress.inventory) == 0:
                no_skin_txt = ui_font.render("No skins in inventory!", True, (160, 100, 100))
                buy_hint = ui_font.render("Buy skins in Marketplace first.", True, (150, 150, 150))
                screen.blit(no_skin_txt, (340, 260))
                screen.blit(buy_hint, (340, 290))
            else:
                start_guess_rect = pygame.Rect(410, 260, 360, 50)
                pygame.draw.rect(screen, (50, 180, 100), start_guess_rect, border_radius=8)
                btn_txt = ui_font.render("START 'GUESS THE NUMBER'", True, (255, 255, 255))
                screen.blit(btn_txt, (start_guess_rect.x + 15, start_guess_rect.y + 15))
                
                info_txt = ui_font.render(f"Next skin to lose: {progress.inventory[0].name}", True, (255, 215, 0))
                screen.blit(info_txt, (340, 330))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()