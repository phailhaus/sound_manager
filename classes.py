import math
import os
import time

import pygame

data_dir = "" # Gets overwritten by main script

class Song: # Class that handles data and playback for a single song
	def __init__(self, songconfig: dict) -> None:
		self.playing = False # Bool that indicates if this song is currently the active song
		self.time_started = 0 # Int giving the time.perf_counter_ns() timestamp when the song was last started. Zero if it has never been played
		self.time_stopped = 0 # Int giving the time.perf_counter_ns() timestamp when the song was last stopped. Zero if it has never stopped
		
		self.silence = False # Bool that indicates if the song is actually a silent placeholder instead of a real file. Used to toggle file-related stuff.
		if songconfig["file"] == None:
			self.silence = True
		
		self.end_early = False # Bool that indicates if the song will auto-end and move to the next song
		self.end_ms = songconfig["end_ms"] # Int of time that song will end at in milliseconds. None if the song does not auto-end
		self.end_ns = None
		if self.end_ms != None:
			self.end_early = True
			self.end_ns = self.end_ms * 1000000

		self.file = songconfig["file"]
		self.name = songconfig["name"]
		self.volume = songconfig["volume"]
		self.loop = songconfig["loop"]
		self.fade_in_ms = songconfig["fade_in_ms"]
		self.fade_out_ms = songconfig["fade_out_ms"]

		if not self.silence: # Load sound file
			self.sound = pygame.mixer.Sound(os.path.join(data_dir, self.file)) # Note: Song file is loaded into RAM here. Good for fast playback, bad for large playlists
			self.sound.set_volume(self.volume)
			self.duration_ms = self.sound.get_length() * 1000
		else: # Set settings for silent placeholder songs
			self.sound = None
			if self.end_early: # If song has autoend on, populate the duration so that it can have a progress bar
				self.duration_ms = self.end_ms
			else:
				self.duration_ms = None

		self.display_string = str() # Populate the static portion of the display text
		self.display_string += f"{self.name}"
		if self.loop:
			self.display_string += " | Looping"
		if self.end_early:
			self.display_string += f" | Ends automatically after {self.end_ms/1000} seconds"
	
	def play(self) -> None: # Function that handles playing the song
		self.time_started = time.perf_counter_ns()
		self.playing = True
		if not self.silence:
			loops = 0
			if self.loop:
				loops = -1 # Setting the loops parameter to -1 makes it loop forever.
			self.sound.play(loops= loops, fade_ms= self.fade_in_ms)
	
	def stop(self) -> None: # Function that handles stopping the song
		self.playing = False
		self.time_stopped = time.perf_counter_ns() # Stop Song timer
		if not self.silence:
			self.sound.fadeout(self.fade_out_ms) # Song doesn't actually fully stop until fade time has elapsed
	
	def get_elapsed_time_ns(self) -> int: # Function that returns the play time of the song in nanoseconds
		if self.time_started > 0: # If the song has played at some point, calculate elapsed time
			if self.time_stopped < self.time_started: # If the most recent playback of the song has not been stopped, calculate based on current time
				current_time = time.perf_counter_ns()
				return current_time - self.time_started
			else: # If most recent has stopped, calculate delta between the two stored timestamps
				return self.time_stopped - self.time_started
		else: # If the song has not played, return zero
			return 0
		
	def get_elapsed_time_ms(self) -> int: # Function that returns the play time of the song in milliseconds because converting is annoying
		return self.get_elapsed_time_ns() / 1000000
	
	def get_display_string(self) -> str: # Function that returns self.display_string with the elapsed time and duration appended
		output_string = self.display_string

		elapsed_s = self.get_elapsed_time_ms() / 1000
		elapsed_minutes = math.floor(elapsed_s / 60)
		elapsed_remaining_seconds = elapsed_s % 60
		output_string += f" | {elapsed_minutes}:{elapsed_remaining_seconds:0>4.1f}"

		if self.duration_ms != None:
			duration_s = self.duration_ms / 1000
			duration_minutes = math.floor(duration_s / 60)
			duration_remaining_seconds = duration_s % 60
			output_string += f" / {duration_minutes}:{duration_remaining_seconds:0>4.1f}"
		
		return output_string
	
	def calculate_fade_triangle(self, render_x: int, render_y: int, bar_height: int, this_bar_width: float, filled_bar_width: float, fadein: bool) -> (tuple, tuple):
		if fadein: # Set up calculation values if we are calculating the fade in triangle
			triangle_duration_ms = self.fade_in_ms
			triangle_fill = max(min(self.get_elapsed_time_ms() / self.fade_in_ms, 1), 0) # Limit to 0-1
			triangle_fade_width = (triangle_duration_ms / self.duration_ms) * this_bar_width # Width in pixels of the triangle
			triangle_coords = ((render_x, render_y + bar_height - 1), (render_x + triangle_fade_width, render_y + bar_height - 1), (render_x + triangle_fade_width, render_y))
		else: # Set up calculation values if we are calculating the fade out triangle
			triangle_duration_ms = self.fade_out_ms
			if self.time_stopped > self.time_started: # If the song is currently stopped and has been played
				triangle_fill = ((time.perf_counter_ns() - self.time_stopped) / 1000000) / self.fade_out_ms
				triangle_fill = max(min(triangle_fill, 1), 0) # Limit to 0-1
				triangle_fill = 1 - triangle_fill # Flip the value so that it is the distance from the point of the triangle, not the side
			else: # If the song hasn't been stopped
				triangle_fill = 1
			triangle_fade_width = (triangle_duration_ms / self.duration_ms) * this_bar_width # Width in pixels of the triangle
			triangle_coords = ((render_x + filled_bar_width, render_y + bar_height - 1), (render_x + filled_bar_width, render_y), (render_x + filled_bar_width + triangle_fade_width, render_y + bar_height - 1))
		
		if triangle_fill != 0 and triangle_fill != 1:
			triangle_filled_width = triangle_fade_width * triangle_fill # Position of the fill line in pixels within the triangle. Measured from the point
			triangle_ratio = bar_height / triangle_fade_width
			triangle_filled_height = triangle_filled_width * triangle_ratio
			if fadein:
				fill_coords = ((render_x, render_y + bar_height - 1), (render_x + triangle_filled_width, render_y + bar_height - 1), (render_x + triangle_filled_width, render_y + bar_height - triangle_filled_height))
			else:
				fill_coords = ((render_x + filled_bar_width, render_y + bar_height - 1), (render_x + filled_bar_width, render_y), (render_x + filled_bar_width + (triangle_fade_width  - triangle_filled_width), render_y + bar_height - triangle_filled_height), (render_x + filled_bar_width + (triangle_fade_width  - triangle_filled_width), render_y + bar_height - 1))
			return fill_coords, triangle_coords
		elif (triangle_fill == 0 and not fadein) or (triangle_fill == 1 and fadein):
			return triangle_coords, triangle_coords
		else:
			return None, triangle_coords

	def check_autoend(self) -> bool: # Function that is called each frame while the song is playing to see if it should end
		if self.playing and self.end_early and not self.silence:
			if self.get_elapsed_time_ns() >= self.end_ns:
				return True
		else:
			return False


class Songset: # Class that holds all songs in the set and handles moving between them
	def __init__(self, songconfiglist: list) -> None:
		self.song_list = list() # Stores all songs in the set in order
		self.max_duration_ms = 0 # Int storing the duration of the longest song. Used for scaling progress bars
		for songconfig in songconfiglist: # Load all of the songs in the playlist
			self.song_list.append(Song(songconfig))
			if self.song_list[-1].duration_ms != None and self.song_list[-1].duration_ms > self.max_duration_ms: # Update max duration if greater
				self.max_duration_ms = self.song_list[-1].duration_ms

		self.current_song = 0 # Int that identifies the selected song
		self.song_count = len(self.song_list) # Int that stores the total number of songs so that we don't overrun
	
	def play(self) -> None: # Function that just plays the current song
		self.song_list[self.current_song].play()
	
	def next_song(self) -> None: # Function that stops the current song, then moves to the next song and starts it.
		self.song_list[self.current_song].stop()
		if self.current_song + 1 < self.song_count:
			self.current_song += 1
			self.song_list[self.current_song].play()

	def previous_song(self) -> None: # Function that stops the current song, then moves to the previous song and starts it.
		self.song_list[self.current_song].stop()
		if self.current_song - 1 >= 0:
			self.current_song -= 1
			self.song_list[self.current_song].play()

	def check_autoend(self) -> None: # Function that is called every frame to check if the currently-playing song is supposed to stop. If so, move to the next song
		if self.song_list[self.current_song].check_autoend():
			self.next_song()