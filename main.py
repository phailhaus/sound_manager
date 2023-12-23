import json
import os
import sys

import pygame
from pygame.locals import *

import classes

if len(sys.argv) < 2:
	print("\nSound Management Tool\nRequires one argument naming a config defined in data\config.json\nExample: python main.py demo1")
	quit()

pygame.init()
pygame.mixer.init()

# Set directories
data_dir = "data" # Sets the folder all user files are in
config_file = "config.json" # Filename of the song list file in the data folder
config_name = sys.argv[1] # The command line argument is used to identify what list to load from the config file 

classes.data_dir = data_dir # Overwrite the data_dir variable on the class library

# Set the dimensions of the screen
screen_width = 1200 # Horizontal resolution of the window
screen_height = 800 # Vertical resolution of the window
screen = pygame.display.set_mode((screen_width, screen_height)) # Create the window surface
screen_margin_x = 25 # Sets the horizontal offset from the left edge to use when drawing stuff
screen_margin_y = 25 # Sets the vertical offset from the top edge to use when drawing stuff

# Create second surface to use for blanking
background = pygame.Surface((screen_width, screen_height)) # Create surface
background.fill(pygame.Color(0, 0,  0)) # Fill it with background

# Set up font object
font = pygame.font.Font(size=32) # Set up the font. I am using the Pygame default
font_height = font.get_linesize() # Get the height in pixels of a line of text. Used for offsetting rendering later
font_color_playing = (255, 255, 255) # Text color for playing song text and the cursor
font_color_stopped = (170, 170, 170) # Text color for other songs

# Set up progress bar parameters
bar_width = screen_width - (screen_margin_x * 2) # How wide the progress bar should be for the longest track. Other tracks will be proportionally shorter
bar_height = font_height # How tall the progress bars should be
bar_color_playing_border = (255, 255, 255)
bar_color_playing_fill = (200, 200, 200)
bar_color_stopped_border = (170, 170, 170)
bar_color_stopped_fill = (145, 145, 145)
bar_color_fade_in_triangle = (100, 255, 100, 127)
bar_color_fade_out_triangle = (255, 100, 100, 127)
bar_color_end_early_line = (100, 100, 255, 127)

# Set up the clock object
clock = pygame.time.Clock()
framerate = 30 # The rate at which the screen updates and logic such as user input and auto-end is processed

# Load config
config = dict()
with open(os.path.join(data_dir, config_file)) as jsonfile: # Load the config file
	config = json.load(jsonfile)

# Load the song set specified in the command line argument. Loads all audio files into RAM.
active_songset = classes.Songset(config[config_name])

active_songset.play() # Trigger the first track in the set

# Game loop
running = True
frame = 0
while running:
	# Limit the framerate
	clock.tick(framerate)

	# Handle events
	for event in pygame.event.get():
		if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
			running = False # Press Escape or the X in the corner to quit
		if event.type == KEYDOWN:
			if event.key == K_UP:
				active_songset.previous_song() # Press the up arrow to move back one song
			if event.key == K_DOWN:
				active_songset.next_song() # Press the down arrow to move forward one song
	
	screen.blit(background, (0, 0)) # Clear the screen

	active_songset.check_autoend() # Causes the current song to see if it has been playing longer than it is set to run for. If it has, moves to the next song
	
	list_start_x, list_start_y = screen_margin_x, screen_margin_y # Set top-left corner of song list. Set this way so that it could be customized easily.

	render_x = list_start_x
	render_y = list_start_y
	
	for song in active_songset.song_list: # Iterate through the songs, rendering each to the screen
		if song.playing: # Pick the text color based on whether the song is playing
			this_text_color = font_color_playing
		else:
			this_text_color = font_color_stopped
		
		text_surface = font.render(song.get_display_string(), True, this_text_color) # Render the song title and other details. Note that song.display_string is everything except for current playtime and duration. song.get_display_string() appends the time information.
		screen.blit(text_surface, (render_x,  render_y))
		render_y += font_height # Shift the y component of the rendering position down one line of text
		
		if song.duration_ms != None: # If the song isn't infinite silence, draw a progress bar
			this_bar_width = (song.duration_ms / active_songset.max_duration_ms) * bar_width # Calculate the width of the progress bar proportional to the longest song in the set
			elapsed_time_ms = song.get_elapsed_time_ms()
			
			if song.loop and elapsed_time_ms > song.duration_ms: # Correct for loops so that the bar doesn't overfill
				elapsed_time_ms = elapsed_time_ms % song.duration_ms
			
			filled_bar_width = (elapsed_time_ms / song.duration_ms) * this_bar_width # Calculate how wide the bar fill rectangle should be
			
			if song.playing: # Pick the bar colors based on whether the song is playing
				this_bar_color_fill = bar_color_playing_fill
				this_bar_color_border = bar_color_playing_border
			else:
				this_bar_color_fill = bar_color_stopped_fill
				this_bar_color_border = bar_color_stopped_border
			
			pygame.draw.rect(screen, this_bar_color_fill, (render_x, render_y, filled_bar_width, bar_height)) # Draw the interior fill of the progress bar
			
			if song.fade_in_ms > 0: # If the song has a fade in, draw a triangle indicating the length of the fade
				fill_coords, triangle_coords = song.calculate_fade_triangle(render_x, render_y, bar_height, this_bar_width, filled_bar_width, True)
				
				if fill_coords != None:
					pygame.draw.polygon(screen, bar_color_fade_in_triangle, fill_coords)
				
				pygame.draw.polygon(screen, bar_color_fade_in_triangle, triangle_coords, 1)
			
			if song.fade_out_ms > 0: # If the song has a fade out, draw a triangle indicating the length of the fade
				fill_coords, triangle_coords = song.calculate_fade_triangle(render_x, render_y, bar_height, this_bar_width, filled_bar_width, False)
				
				if fill_coords != None:
					pygame.draw.polygon(screen, bar_color_fade_out_triangle, fill_coords)
				
				pygame.draw.polygon(screen, bar_color_fade_out_triangle, triangle_coords, 1)
			
			if song.end_early: # If the song is set to end at a set time and move to the next song, draw a line at that point
				end_marker_position = (song.end_ms / song.duration_ms) * this_bar_width
				pygame.draw.line(screen, bar_color_end_early_line, (render_x + end_marker_position, render_y), (render_x + end_marker_position, render_y + bar_height - 1))
			
			pygame.draw.rect(screen, this_bar_color_border, (render_x, render_y, this_bar_width, bar_height), 1) # Draw the border of the progress bar
		
		render_y += bar_height * 1.75 # Shift the y component of the rendering position down the height of the bar, plus some more to give space before the next song
		
	text_surface = font.render(">", True, font_color_playing) # Render the cursor indicating which song is currently selected
	screen.blit(text_surface,  (list_start_x - text_surface.get_width() - 2,  list_start_y + ((font_height + (bar_height * 1.75)) * active_songset.current_song)))
	
	pygame.display.flip() # Update the display to the new state of the screen surface
