#!/usr/bin/python
#
#Short Adventurer
#Version: 0.1
#By Soeren Pilgaard
#
#LICENSE:
#----------------------------------------------------------------------------
#"THE BEER-WARE LICENSE" (Revision 42):
#<fiskomaten@gmail.com> wrote this file. As long as you retain this notice you
#can do whatever you want with this stuff. If we meet some day, and you think
#this stuff is worth it, you can buy me a beer in return. Soeren E. Pilgaard
#----------------------------------------------------------------------------

###
###================================================================================================================================
###LOAD MODULES:
try:
    import os, sys, random, math, pickle, pygame
    from pygame.locals import *
except ImportError, err:
    print'Cannot load module: {0}'.format(err)
    sys.exit(1) # Exit with a failure


#Define some objects we want global access to
mapCon = None
G_allEntities = pygame.sprite.Group()   #These are sprite groups, grouping stuff, when i create objects i add them to the apropiate groups
G_allEnemies = pygame.sprite.Group()
G_allItems = pygame.sprite.Group()
dwarf = None

###
###================================================================================================================================
###RESOURCE HANDLING:
def load_image(filename, colorkey = None):
    '''A function for loading images, can take colorkeys into account'''
    filename = os.path.join('images', filename) #Connects the path and the filename with the os specific character
    try:
        image = pygame.image.load(filename)
    except pygame.error, message:
        print'Cannot load image: {0}'.format(message)
        raise SystemExit, message
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()      #Returns the image and its rect


def load_sound(filename):
    pass
def save_game():
    pass
def load_game():
    pass


###
###================================================================================================================================
###GAME OBJECT CLASSES:
class Map(pygame.sprite.Sprite):
    '''This class controls the map. 
    as the game was intented to contain more levels, i decided to place a lot of functionality in here'''
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        
        self.levelName = 'dungeon'
        self.background, trash = load_image('background.bmp')   #We dont need the rect from load_image, but if we dont assign it, background will end up as a tuple
        self.items = [None] #A list of items laying about in the world
        self.goblins = [None]   #A list of goblins
        
#Eksperimental work, just ignore:
##        self.tileset, tilesetrect = load_image('tileset.bmp')
##        self.tile = (0,32,32,32)        
##        self.background = pygame.Surface(pygame.display.get_surface().get_size()).convert()
##        self.rect = self.background.get_rect()
##        self.background.fill((0,0,0))
##        self.background.blit(self.tileset, (128,128), self.tile)
        
    def load_level(self, levelname):
        '''Function meant to load levels, not working yet, just ignore'''
        #levelname = os.path.join('data', 'levels', levelname)
        f = open(levelname+'.map', 'rb')
        self.level = pickle.load(f)
        f.close()
        print self.level
    def update(self):
        pass
    def user_action(self):
        '''If the user does any actions this method is run.
        The method is currently just used for spawning goblins at random'''
        if random.randint(0, 5) == 0:   #Randomly spawn goblins
            self.spawn_goblin()
            
    def create_item(self, pos):
        '''The method for creating items'''
        newitem = Item(pos)
        self.items.append(newitem)
    def spawn_goblin(self):
        '''Spawns a goblin at a random position'''
        goblin = Goblin(random.randint(0, 19)*32, random.randint(0, 14)*32)
        self.goblins.append(goblin)

    
class Dwarf(pygame.sprite.Sprite):
    '''The main character of the game.'''
    def __init__(self):
        global G_allEntities
        pygame.sprite.Sprite.__init__(self)
        self.add(G_allEntities)
        
        self.image, self.rect = load_image('dwarf.bmp', -1)
        self.rect.topleft = 64, 64
        self.health = 100
        self.strength = 10
        self.gold = 0
        
    def update(self):
        pass
        
    def move(self, move):
        '''The method for moving around, also detects if the player is attacking a goblin'''
        global G_allEnemies
        move[0] *= 32
        move[1] *= 32
        oldpos = self.rect
        self.rect = self.rect.move(move) #move towards the vector 'move'. The *32 is to make you move 1 tile
        
        #Check for collisions in new place. if any; move back and activate the enemys struck method
        for enemy in pygame.sprite.spritecollide(self, G_allEnemies, 0):
            self.rect = oldpos
            dmg = random.randint(1, self.strength) #Determine damage
            enemy.struck(dmg)
    
    def struck(self, attacker, dmg):
        '''If the dwarf is hit, this method takes care of the health-regulation and check if you die'''
        print '{0} attacks you and deal {1} damage!'.format(attacker.name, dmg)
        self.health -= dmg
        if self.health <= 0:    #Check if dead
            print 'You were killed by {0}'.format(attacker.name)
            game_over()
        
        
class Goblin(pygame.sprite.Sprite):
    '''The foul enemies who invaded our stronghold.'''
    def __init__(self, x, y):
        global G_allEntities, G_allEnemies
        pygame.sprite.Sprite.__init__(self)
        self.add(G_allEntities)
        self.add(G_allEnemies)
        
        self.image, self.rect = load_image('goblin.bmp', -1)
        self.rect.topleft = x, y
        self.name = 'a Goblin'
        self.health = 30
        self.strength = 3
        self.viewRange = 32*10   #Goblins can see 10 tiles away
    def update(self, userAction=0):
        '''update, is run every frame, if user has done anything activate the ai, else just stand idle'''
        if userAction:
            self.act()
    def act(self):
        '''AI stuff go here'''
        global dwarf
        distance = distance_to(self.rect, dwarf.rect)
        if distance <= 32:  #Goblin is close enough to attack
            self.attack()
        elif distance_to(self.rect, dwarf.rect) <= self.viewRange:          #I can see you!
            moveStr, moveVector = walk_direction_to(self.rect, dwarf.rect)  #And i'm coming for you! Find diection to go
            self.move(moveVector)
            
    def move(self, move):
        '''Calculate movement.
        Takes a movement vector as move'''
        move[0] *= 32
        move[1] *= 32
        oldpos = self.rect
        self.rect = self.rect.move(move)
        
    def attack(self):
        '''calculate damage against dwarf'''
        dmg = random.randint(1, self.strength) #determines damage
        dwarf.struck(self, dmg)
        
    def struck(self, dmg):
        '''if goblin is hit this is done'''
        print 'You hit {0} for {1} damage'.format(self.name, dmg)
        self.health -= dmg
        if self.health <= 0:
            print 'You killed {0}'.format(self.name)
            self.die()
            
    def die(self):
        global mapCon
        '''when die create a random item through mapCon'''
        mapCon.create_item(self.rect)
        self.kill()
        del self    #How do we kill it? we dont need any ghosts lurking!
        

class Item(pygame.sprite.Sprite):
    '''The treasures of the ancient stronghold'''
    def __init__(self, position):
        global G_allEntities, G_allItems
        pygame.sprite.Sprite.__init__(self)
        self.add(G_allEntities)
        self.add(G_allItems)
        
        #this item is a random choice of type, load image after that
        self.type = random.choice(('Health Potion', 'Weapon', 'Gold', 'Stick'))
        self.image, self.rect = load_image(self.type.lower().replace(' ', '')+'.bmp', -1)
        self.rect = position
    def update(self):
        pass



###
###================================================================================================================================
###OTHER GAME FUNCTIONS:
def distance_to(pos1, pos2):
    '''Pythagoras in python ;)'''
    return math.sqrt(math.pow(abs(pos1[0]-pos2[0]),2) + math.pow(abs(pos1[1]-pos2[1]),2))

def walk_direction_to(pos1, pos2):
    '''Gives the horisontal or vertical direction to... Used for AI movement.
    This is a rather crude way to basic path finding, checks horisontaly then verticaly
    Returns both a string and a vector, the string was used for debugging/future implementations and should be ignored
    '''
    if pos1[0] - pos2[0] < 0:
        return 'right', [1,0]
    elif pos1[0] - pos2[0] > 0:
        return 'left', [-1,0]
    elif pos1[1] - pos2[1] < 0:
        return 'down', [0,1]
    elif pos1[1] - pos2[1] > 0:
        return 'up', [0,-1]
    else:
        return 0    #failure, on top of eachother

def game_over():
    '''You Lost'''
    global dwarf
    print '===GAME OVER===\nYou earned {0} gold on your Short Adventure!'.format(dwarf.gold)
    sys.exit()
    
###
###================================================================================================================================
###INITIALISING THE GAME:
def main():
    pygame.init()   #Initialise pygame
    screen = pygame.display.set_mode((640,480))
    pygame.display.set_caption('Short Adventurer')
    global mapCon, G_allEntities, G_allEnemies, G_allItems, dwarf
    
    clock = pygame.time.Clock() #Create an instance of Clock to keep track of timing
    mapCon = Map()  #Map controls
    dwarf = Dwarf()

    G_allEntities = pygame.sprite.RenderClear((dwarf))
    
    screen.blit(mapCon.background, (0, 0))
    pygame.display.update()

###
###================================================================================================================================
###MAIN LOOP:
    while True:
        clock.tick(60)  #Set gamespeed/framerate, the clock will wait untill at least 60 milliseconds has passed before proceeding
        #Reset stuff
        move = [0, 0]
        userAction = 0

        #Check eventqueue for user inputs
        for event in pygame.event.get():
            if event.type == QUIT:
                return  #return out of main, there by ending the loop and program
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return   #return out of main, there by ending the loop and program
                if event.key == K_d:
                    move[0] += 1
                if event.key == K_a:
                    move[0] -= 1
                if event.key == K_w:
                    move[1] -= 1
                if event.key == K_s:
                    move[1] += 1
                if event.key == K_l:
                    mapCon.load_level('dungeon')    #Experimental maploading stuff
                    print dir()
                if event.key == K_TAB:  #The print stats key
                    print 'HP: {0}   Str: {1}   Gold: {2}'.format(dwarf.health, dwarf.strength, dwarf.gold)
                    
                if event.key == K_SPACE: #The action key
                    userAction = 1
                    for item in pygame.sprite.spritecollide(dwarf, G_allItems, 0):
                        print 'You picked up a', item.type + '!'
                        if item.type == 'Health Potion':
                            dwarf.health += 20
                        elif item.type == 'Weapon':
                            dwarf.strength += 2
                        elif item.type == 'Gold':
                            dwarf.gold += 1
                        else:
                            print 'But it prooved unusable...'
                        item.kill() #removes the item from all groups and deletes it


        #No strafing alowed
        if move[0] and move[1] :
            move[0] = 0
        #If any of these, got any values there is movement
        if move[0] or move[1]:
            dwarf.move(move)
            userAction = 1
        if userAction:
            G_allEnemies.update(1)
            mapCon.user_action()
            print '\n\n'
        
        
        #run the update command and render game
        G_allEntities.update()
        G_allEntities.clear(screen, mapCon.background)
        G_allEntities.draw(screen)
        pygame.display.update()

###
###================================================================================================================================
###MAIN CALL
        
#Call the 'Main' function when script is executed on its own (always)
if __name__ == '__main__': main()
