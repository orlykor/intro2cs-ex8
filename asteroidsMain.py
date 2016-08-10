from torpedo import *
from asteroid import *
from spaceship import *
from gameMaster import *
import math
import sys

class GameRunner:

    def __init__(self, amnt = 3):
        self.game = GameMaster()
        self.screenMaxX = self.game.get_screen_max_x()
        self.screenMaxY = self.game.get_screen_max_y()
        self.screenMinX = self.game.get_screen_min_x()
        self.screenMinY = self.game.get_screen_min_y()
        shipStartX = (self.screenMaxX-self.screenMinX)/2 + self.screenMinX
        shipStartY = (self.screenMaxY-self.screenMinY)/2 + self.screenMinY
        self.game.set_initial_ship_cords( shipStartX, shipStartY )
        self.game.add_initial_astroids(amnt)

    def run(self):
        self._do_loop()
        self.game.start_game()


    def _do_loop(self):
        self.game.update_screen()
        self.game_loop()
        # Set the timer to go off again
        self.game.ontimer(self._do_loop,5)

    def game_loop(self):
        '''
        here is the main game.
        '''
        self.move_asteroids()
        self.move_space_ship()
        self.shoot_torpedos()
        self.move_torpedos()
        self.remove_torpedos()
        self.torpedo_asteroid_intersect()
        self.ship_asteroid_intersect()
        self.end_game()


    def move_object(self,object):
        '''
        this func makes the choosen object move. it takes the object's
        speed, corrent place and the size of the screen. with the formula
        it calculates the movement.
        '''
        speed_x,speed_y = object.get_speed_x(),object.get_speed_y()
        cor_x, cor_y = object.get_x_cor(),object.get_y_cor()
        screen_max_x, screen_max_y = self.screenMaxX,self.screenMaxY
        screen_min_x, screen_min_y = self.screenMinX,self.screenMinY
        # we calculate the new place the object is in consider the variables
        #above.
        new_cor_x = (speed_x + cor_x - screen_min_x ) % \
                    (screen_max_x - screen_min_x) + screen_min_x
        new_cor_y = (speed_y + cor_y - screen_min_y ) % \
                    (screen_max_y - screen_min_y) + screen_min_y
        object.move(new_cor_x,new_cor_y) #make the object move


    def move_asteroids(self):
        '''
        this func goes through all the asteroids in the asteroids list. 
        it sends each one to the move_object func and make them move.
        '''
        asteroids = self.game.get_asteroids()
        for item in asteroids:
            self.move_object(item)

    def move_space_ship(self):
        '''
        this func moves the space ship consider the pressed botten. if the 
        player press left and right it changes the ship angle if up it makes it
        go faster. 
        '''
        ship = self.game.get_ship()
        left, right = self.game.is_left_pressed(), self.game.is_right_pressed()
        up = self.game.is_up_pressed()
        #check what is pressed:
        if left:
            ship.decrease_angle()
        elif right == True:
            ship.increase_angle()
        elif up:
            speed_x,speed_y = ship.get_speed_x(),ship.get_speed_y()
            #convert the angle to radiands
            angle_radians = math.radians(ship.get_angle())
            #calculate the new values of the spaceship speed
            new_speed_x = speed_x + math.cos(angle_radians)
            new_speed_y = speed_y + math.sin(angle_radians)
            ship.set_speed_x(new_speed_x)
            ship.set_speed_y(new_speed_y)

        self.move_object(ship)


    def shoot_torpedos(self):
        '''
        this func adds torpedos to the game and fire them if the right key for
        fire was pressed. the ship can only fire 20 torpedos each time. 
        '''
        MAX_TORPEDOS = 20
        DOUBLE = 2
        torpedos = self.game.get_torpedos()
        ship = self.game.get_ship()
        # as long as there are les then 20 torpedos to the next commends:
        if len(torpedos) < MAX_TORPEDOS: 
            fire = self.game.is_fire_pressed()
            if fire: # if fire was pressed                
                x,y = ship.get_x_cor(),ship.get_y_cor()
                angle = ship.get_angle()
                speed_x,speed_y = ship.get_speed_x(),ship.get_speed_y()
                ship_angle_radians = math.radians(angle)
                # with all the values we took from the ship we claculate the 
                #speed of the torpedo
                new_spd_x = speed_x + DOUBLE * math.cos(ship_angle_radians)
                new_spd_y = speed_y + DOUBLE * math.sin(ship_angle_radians)
                torpedo = self.game.add_torpedo(x,y,new_spd_x,new_spd_y,angle)


    def move_torpedos(self):
        '''
        this func makes the fired torpedos move
        '''
        all_torpedos = self.game.get_torpedos()
        for torpedo in all_torpedos:
            self.move_object(torpedo)


    def remove_torpedos(self):
        '''
        this func removes the torpedos if thier time life has passed.
        '''
        RUN_OF_TIME = 0
        all_torpedos = self.game.get_torpedos()
        deadtorpedos = []
        for torpedo in all_torpedos: # i go through all the torpedos
            life_time = torpedo.get_life_span()
            if life_time <= RUN_OF_TIME:
                deadtorpedos.append(torpedo)
        self.game.remove_torpedos(deadtorpedos)

    def torpedo_asteroid_intersect(self):
        '''
        this func checks if there was an intersection between a fired torpedo
        and an asteroid. if was one then it splits the big asteroids into 2.
        consider the size of the asteroid it splits it into 2 smaller 
        asteroids, until it gets to the smallest one, then it is completly 
        removed. 
        '''

        SIZE3_SCORE = 20
        SIZE2_SCORE = 50
        SIZE1_SCORE = 100
        BIG_SIZE = 3
        MID_SIZE = 2
        SMALL_SIZE = 1
        all_torpedos = self.game.get_torpedos()
        asteroids = self.game.get_asteroids()
        # goes through all the asteroids and torpedos:
        for asteroid in asteroids:
            for torpedo in all_torpedos:
                intersect = self.game.intersect(asteroid,torpedo)
                if intersect:
                    # if there is intersection then update the score and split
                    # the asteroid if needed.
                    if asteroid.get_size() == BIG_SIZE:
                        score = self.game.add_to_score(SIZE3_SCORE)
                        self.split_asteroids(asteroid,torpedo,MID_SIZE)
                    elif asteroid.get_size() == MID_SIZE:
                        score = self.game.add_to_score(SIZE2_SCORE)
                        self.split_asteroids(asteroid,torpedo,SMALL_SIZE)
                    elif asteroid.get_size() == SMALL_SIZE:
                        score = self.game.add_to_score(SIZE1_SCORE)
                        self.game.remove_asteroid(asteroid)
                        self.game.remove_torpedos([torpedo])



    def split_asteroids (self,asteroid,torpedo,size):
        '''
        this func takes the asteroid that has been fired with the torepdo and
        split it to another two asteroids. if its a big asteroid (size 3) it
        split it to 2 small asteroids with the size of 2, and the two's to
        one's.
        '''
        DOUBLE = 2
        spd_x,spd_y = asteroid.get_speed_x(),\
            asteroid.get_speed_y()
        x,y = asteroid.get_x_cor(),asteroid.get_y_cor()
        new_spd_x = (torpedo.get_speed_x() + spd_x) / math.sqrt(DOUBLE ** \
                                                    spd_x + DOUBLE ** spd_y)
        new_spd_y = (torpedo.get_speed_y() + spd_y) / math.sqrt(DOUBLE ** \
                                                    spd_x + DOUBLE ** spd_y)
        self.game.remove_asteroid(asteroid)
        self.game.remove_torpedos([torpedo])
        self.game.add_asteroid(x,y,-new_spd_x,-new_spd_y,size)
        self.game.add_asteroid(x,y,new_spd_x,new_spd_y,size)

    def ship_asteroid_intersect(self):
        '''
        this func checks if there was an intersect between the spaceship and
        the asteroids
        '''
        asteroids = self.game.get_asteroids()
        ship = self.game.get_ship()
        WARINING_TITLE = "warning!"
        WARINING_MSG = "Youv'e just lost a life" 
        for asteroid in asteroids:
            intersect = self.game.intersect(asteroid,ship) #check if intersect
            if intersect:
                self.game.ship_down() #i take one life from the ship
                self.game.show_message(WARINING_TITLE,WARINING_MSG) 
                self.game.remove_asteroid(asteroid)

    def end_game(self):
        '''
        this func ends the game. with 3 options: if the player won and there
        are no more asteroids in the game, if he lost all his life or if he
        wants to quit the game. with every option comes a message to the
        player, then it ends the game.
        '''
        #this are the 3 options for ending the game:
        asteroids_life = self.game.get_asteroids()
        ship_life = self.game.get_num_lives()
        press_q = self.game.should_end()
        WINNING_TITLE = "wow"
        WINNIN_MSG = "You won!"
        LOSE_TITLE = "too bad"
        LOSE_MSG = "You lost"
        QUIT_TITLE = "why quit??" 
        QUIT_MSG = "Quit the game"
        NO_LIFE = 0 
        #for each option we have a different message
        if ship_life == NO_LIFE:
            self.game.show_message(LOSE_TITLE,LOSE_MSG) #show the message
            self.game.end_game()
        elif asteroids_life == []:
            self.game.show_message(WINNING_TITLE,WINNIN_MSG)
            self.game.end_game()
        elif press_q:         
            self.game.show_message(QUIT_TITLE,QUIT_MSG) 
            self.game.end_game()


        






def main(argument):
    runner = GameRunner(argument)
    runner.run()
    

if __name__ == "__main__":
    ONE_OPTION = 1
    if ONE_OPTION < len(sys.argv):
        main(int(sys.argv[1]))
    else:
        main()
    
