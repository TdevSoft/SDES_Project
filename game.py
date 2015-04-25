#!/usr/bin/env python

# Lines should be lists of dots strictly of size 2
# Boxes should be quadruples of lines starting from roof and continuing clock-wise.
# Have to take care of the fact that the line finalized is not already drawn. Done now.
# Have to incorporate the handling of successive frames. Done now.
# Player to draw the next line should be kept track of. Very IMP. Done now.
# What about the co-ordinates of the dots? Convert to standard unitless Cartesian co-ordinates.

from grid import *
from dot import *
from video import *
from errorhandling import *

class Game(object):
    def __init__(self,grid_size,dot_size,no_of_players):
        self.new_grid=grid(left_top,grid_size,dot_size)
        self.grid_size=grid_size
        self.no_of_players=no_of_players
        self.owner_of_next_line=0
        self.owner_of_last_line=self.no_of_players-1
        self.list_of_lines_drawn=[]
        self.no_of_boxes_of_players=[0,0]

    def _grid_filled(self):
        return sum(no_of_boxes_of_players)==(self.grid_size[0]-1)*(self.grid_size[1]-1)

    def game_ended(self):
        return self._grid_filled()

    def user_wants_to_stop():
        while True:
            k=cv2.waitKey(5) & 0xFF
            if(k==27):
                return True
            break

    def new_game(self):
        video_handle=start_video_capture()
        while True:
            latest_frame=get_next_frame()
            self.new_grid.draw_grid_on(latest_frame)
            my_input=self.received_input()
            if(my_input==None):
                continue
            else:
                latest_line=my_input
                if(latest_line in list_of_lines_drawn):
                    print "This line is already drawn. Choose another."
                    continue
                self.new_grid.draw_line(latest_line)
                self.update_list_of_drawn_lines_with(latest_line)
                box_formed,box=box_formed_by(latest_line)
                self.set_owner_of_next_line(box_formed)
                if(box_formed):
                    owner_of_the_box=self.get_owner_of_last_line()
                    fill_box(box,owner_of_the_box)
                    self.update_no_of_boxes_of_players(owner_of_the_box)
                    if(game_ended()):
                        print "The entire grid is filled"
                        self.declare_winner()
                        if(user_wants_to_stop()):
                            stop_video_capture(video_handle)
                            print "Thanks for playing!"
                        break

    def set_owner_of_next_line(self,box_formed):
        if not box_formed:
            self.owner_of_next_line=self.player_next_to(self.owner_of_next_line)
            self.owner_of_last_line=self.player_next_to(self.owner_of_last_line)
        else:
            self.owner_of_next_line=self.owner_of_next_line
            self.owner_of_last_line=self.owner_of_next_line

    def player_next_to(self,player):
        return (player+1)%self.no_of_players

    def get_owner_of_next_line(self):
        return self.owner_of_next_line

    def declare_winner(self):
        if(self.no_of_boxes_of_players[0]>self.no_of_boxes_of_players[1]):
            print "Player 1 is the winner"
        else if(self.no_of_boxes_of_players[0]>self.no_of_boxes_of_players[1]):
            print "Player 2 is the winner"
        else:
            print "This is a tie"
        pass

    def update_no_of_boxes_of_players(self,owner_of_the_box):
        self.no_of_boxes_of_players[owner_of_the_box]+=self.no_of_boxes_of_players[owner_of_the_box]

    def out_of_grid(self,dot_under_test):
        pass

    def get_line_selected_by_pointer(self):
        pass

    def received_input(self):
        position_of_pointer=detect_pointer() # detect_pointer() can be a global function, right?
        if(self.out_of_grid(position_of_pointer)):
            return None
        else:
            initial_line=self.get_line_selected_by_pointer()
            counter=0
            while(counter<max_count):
                wait(delay)
                position_of_pointer=detect_pointer()
                if(self.out_of_grid(position_of_pointer)):
                    return None
                else:
                    final_line=self.get_line_selected_by_pointer()
                    if(initial_line[0]!=final_line[0] and initial_line[1]!=final_line[1]):
                        return None
            return initial_line

    def get_owner_of_last_line(self):
        return self.owner_of_last_line

    def update_list_of_lines_drawn_with(self,latest_line): # Update the list with the lines expressed in the correct format,i.e.,top-to-bottom or left-to-right
        if(self.is_horizontal(latest_line)):
            if(latest_line[0]~=self.dot_to_left_of(latest_line[1])):
                latest_line=latest_line[::-1]
            self.list_of_lines_drawn.append(latest_line)
            return
        else:
            if(latest_line[0]~=self.dot_above(latest_line[1])):
                latest_line=latest_line[::-1]
            self.list_of_lines_drawn.append(latest_line)
            return

    def is_horizontal(self,line):
        return ((line[0]==self.dot_to_left_of(line[1])) or (line[0]==self.dot_to_right_of())):

    def line_above(self,line):
        if(self.is_horizontal()):
            return [self.new_grid.dot_above(line[0]),self.new_grid.dot_above(line[1])]

    def line_below(self,line):
        if(self.is_horizontal()):
            return [self.new_grid.dot_below(line[0]),self.new_grid.dot_above(line[1])]

    def line_to_the_right_of(self,line):
        if(not self.is_horizontal):
            return [self.new_grid.dot_to_right_of(line[0]),self.new_grid.dot_to_right_of(line[1])]

    def line_to_the_left_of(self,line):
        if(not self.is_horizontal):
            return [self.new_grid.dot_to_left_of(line[0]),self.new_grid.dot_to_left_of(line[1])]

    def pillar_lines(self,roof_line,floor_line):
        left_pillar=[roof_line[0],floor_line[0]]
        right_pillar=[roof_line[1],floor_line[1]]
        return left_pillar,right_pillar

    def roof_and_floor(self,left_pillar,right_pillar):
        roof_line=[left_pillar[0],right_pillar[0]]
        floor_line=[left_pillar[1],right_pillar[1]]
        return roof_line,floor_line

    def box_formed_by(self,latest_line):
        if(self.is_horizontal(latest_line)):
            if(self.line_above(latest_line) in self.list_of_lines_drawn):
                left_pillar,right_pillar=pillar_lines(self.line_above(latest_line),latest_line)
                if((left_pillar in list_of_lines_drawn) and (right_pillar in list_of_lines_drawn)):
                    return True,[self.line_above(latest_line),right_pillar,latest_line,left_pillar]
                else:
                    return False,None
            elif(self.line_below(latest_line) in self.list_of_lines_drawn):
                left_pillar,right_pillar=pillar_lines(latest_line,self.line_below(latest_line))
                if((left_pillar in list_of_lines_drawn) and (right_pillar in list_of_lines_drawn)):
                    return True,[latest_line,right_pillar,self.line_below(latest_line),left_pillar]
                else:
                    return False,None
             else:
                return False,None
        else:
            if(self.line_to_the_left_of(latest_line) in self.list_of_lines_drawn):
                roof,floor=roof_and_floor(self.line_to_the_left_of(latest_line),latest_line)
                if((roof in list_of_lines_drawn) and (floor in list_of_lines_drawn)):
                    return True,[roof,latest_line,floor,self.line_to_the_left_of(latest_line)]
                else:
                    return False,None
            elif(self.line_to_the_right_of(latest_line) in self.list_of_lines_drawn):
                roof,floor=roof_and_floor(latest_line,self.line_to_the_right_of(latest_line))
                if((roof in list_of_lines_drawn) and (floor in list_of_lines_drawn)):
                    return True,[roof,self.line_to_the_right_of(latest_line),floor,latest_line]
                else:
                    return False,None
            else:
                return False,None

    def fill_box(self,box,owner_of_the_box)
        pass
