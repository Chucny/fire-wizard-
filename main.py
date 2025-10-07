from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from random import *
from os import _exit
app = Ursina()

window.fullscreen = True

# WORLD
spawnpoints = [(0, 4, 0)]
current_spawn = 0

Sky(texture=load_texture('background'))
corridor = Entity(model='hall', scale=0.01, collider='mesh')  # only visual
floor = Entity(model='cube', scale=(200, 0.1, 200), collider='box', color=color.clear)

# player
player = FirstPersonController(position=(0, 1, 0))
wand = Entity(position=(0.3, 1.78, 0.42), model='mwand', parent=player, rotation=(0, -45, 45), scale=0.26)
boss_killed=False
# boss
opponent = Entity(
    model='cat',
    scale=10,
    position=(27.59, 1.2, 2.55),
    collider='box', rotation=(-75, 0, 0)   # simpler and more reliable for raycast
)
boss_y = 0.05
boss_x = 27.59
boss_z = 2.55
boss_origin_health = 36

opponent.health = 36

#  dialog test, didnt work
dialog_panel = None

def show_dialog(message, on_close=None):
    """Shows a simple dialog. Closes when Enter is pressed."""
    global dialog_panel
    if dialog_panel:
        return  # only one dialog at a time

    panel_bg = color.rgb(50, 30, 20)      # dark wood
    text_color = color.rgb(240, 220, 180) # light wood

    panel = Entity(parent=camera.ui, model='quad', color=panel_bg, scale=(0.0, 0.0), z=0)
    text = Text(
        parent=camera.ui, 
        text=message, 
        origin=(0,0), 
        color=text_color, 
        scale=2, 
        y=0
    )

    dialog_panel = panel
    mouse.locked = False

    def close_dialog():
        global dialog_panel
        destroy(panel)
        destroy(text)
        dialog_panel = None
        mouse.locked = True
        if on_close:
            on_close()

    panel.close_func = close_dialog

# bullet thingy (fireballs)
bullet_list = []
bullet_speed = 20  # units per second

def input(key):
    if key == 'left mouse down':
        bullet = Entity(
            model='sphere',
            scale=0.5,
            color=color.red,
            position=(player.x, player.y + 1, player.z),
        )
        bullet.direction = camera.forward.normalized()  # store shooting direction safely
        bullet_list.append(bullet)
    if key == 'o':
        _exit(0)

# unfinished boss movement
boss_speed = 3
boss_direction = 1
boss_min_x = -5
boss_max_x = 5
boss_rotation = 0
boss_blocks = []
boss_gravity = 0.096
boss_fight = False
def update():
    global dialog_panel, boss_direction, current_spawn
    global boss_blocks, boss_fight, boss_killed, opponent
    global boss_rotation
    if player.z == player.z:
        boss_fight = True
    # Reset if player falls
    if player.y < -6:
        player.position = (0, 4, 0)
    if randint(1, 68) == 1 and boss_fight == True:
        block = Entity(model='cube', collider='mesh', scale=1.0, position=(player.x, 6, player.z))
        boss_blocks.append(block)
    for o in boss_blocks[:]:
        o.y = o.y - 0.22
        if distance(player.position, o.position) < 1.62:
            player.position = (0, 6, 0)
            print("You died! \n Game Over")
            break
            
    for b in bullet_list[:]:
        b.position += b.direction * bullet_speed * time.dt

        if hasattr(opponent, "health") and opponent.health > 0:
            if distance(b.position, opponent.position) < 3:
                opponent.health -= 1
                print(f"Opponent got hit! Health: {opponent.health}")
                destroy(b)
                bullet_list.remove(b)
                if opponent.health <= 0 and boss_killed == False:
                    destroy(opponent)
                    boss_killed = True
                    print("Opponent defeated!")
    # close dialog
    if dialog_panel and held_keys['enter']:
        dialog_panel.close_func()

    if player.y < -4:
        player.position = spawnpoints[current_spawn]

    # respawn
    if hasattr(opponent, "health") and opponent.health < 1 and boss_killed == False:
        player.position = spawnpoints[current_spawn]
        boss_killed=True
    # move boss
    cx = 27.59
    cz = 2.55
    ccx = cx + randint(0, 5)
    ccz = cz + randint(0, 5)
    if randint(1, 200) == 1 and boss_killed == False:
        opponent.position=(ccx, 1.2, ccz)
    # boss spins
    boss_rotation += 6
    if boss_killed == False:
        opponent.rotation=(0, boss_rotation, 0)
app.run()
