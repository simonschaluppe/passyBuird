from collections import defaultdict
import pygame, sys

# Funcs/Classes ---------------------------------------------- #
def clip(surf,x,y,x_size,y_size):
    handle_surf = surf.copy()
    clipR = pygame.Rect(x,y,x_size,y_size)
    handle_surf.set_clip(clipR)
    image = surf.subsurface(handle_surf.get_clip())
    return image.copy()

class Font():
    def __init__(self, path):
        self.spacing = 1
        self.character_order = ['A','B','C','D','E','F','G','H','I','J','K','L',
                                'M','N','O','P','Q','R','S','T','U','V','W','X',
                                'Y','Z','a','b','c','d','e','f','g','h','i','j',
                                'k','l','m','n','o','p','q','r','s','t','u','v',
                                'w','x','y','z','.','-',',',':','+','\'','!','?',
                                '0','1','2','3','4','5','6','7','8','9','(',')',
                                '/','_','=','\\','[',']','*','"','<','>',';','°',
                                '#','²','³','|','??','%', '€']
        font_img = pygame.image.load(path).convert()
        self.height = font_img.get_height()
        current_char_width = 0
        self.characters = {}
        self.missing_char_replacement = "??"
        character_count = 0
        for x in range(font_img.get_width()):
            c = font_img.get_at((x, 0))
            if c[0] == 127:
                char_img = clip(font_img, x - current_char_width, 0, current_char_width, self.height)
                self.characters[self.character_order[character_count]] = char_img.copy()
                character_count += 1
                current_char_width = 0
            else:
                current_char_width += 1
        self.space_width = self.characters['A'].get_width()

    def character(self, char):
        if char not in self.characters:
            return self.characters[self.missing_char_replacement]
        else: 
            return self.characters[char]

    def surface(self, text, size=None, color=(10,10,10)):
        if not size: size = self.height
        scale = int(size/self.height)
        xo, x_offsets = 0, [0]
        for char in text:
            if char != " ":
                xo += self.character(char).get_width() + self.spacing
            else:
                xo += self.space_width + self.spacing  
            x_offsets.append(xo)

        width = x_offsets[-1]
        small_surf = pygame.Surface((width,self.height))
        for x_offset, char in zip(x_offsets,text):
            if char != ' ':
                small_surf.blit(self.character(char), (x_offset, 0))
                
        text = pygame.transform.scale(small_surf, (width*scale, self.height*scale))
        surf= pygame.Surface(text.get_size())
        surf.fill(color)
        text.set_colorkey((255,0,0))
        surf.blit(text, (0,0))
        surf.set_colorkey((0,0,0))
        return surf

    def render(self, surf, text, loc, size=None, color=(10,10,10)):    
        textsurface = self.surface(text, size, color)
        surf.blit(textsurface, (loc[0], loc[1]))

# Init ------------------------------------------------------- #

if __name__ == '__main__':
    #!/usr/bin/python3.4
    # Setup Python ----------------------------------------------- #


    # Setup pygame/window ---------------------------------------- #
    mainClock = pygame.time.Clock()
    from pygame.locals import *
    pygame.init()
    pygame.display.set_caption('game base')
    screen = pygame.display.set_mode((500, 500),0,32)

    my_font = Font('assets/fonts/small_font.png')
    my_big_font = Font('assets/fonts/large_font.png')

        
    # Loop ------------------------------------------------------- #
    while True:
        
        # Background --------------------------------------------- #
        screen.fill((200,220,255))


        my_font.render(screen, 'Hello World!', (20, 20))
        my_big_font.render(screen, 'Press Escape to close', (20, 40))
        my_big_font.render(screen, 'Hello World! I am Simono.', (20, 120), 100)
        my_font.render(screen, 'Hello World! I have °C. and crazy "§$%³²', (20, 80), 20, color=(240,10,50))
        
        # Buttons ------------------------------------------------ #
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                    
        # Update ------------------------------------------------- #
        pygame.display.update()
        mainClock.tick(60)
        
