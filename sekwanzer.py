import time
import pygame

def sleep_time_calculation(bpm, time_spent_for_sound_play):
    if time_spent_for_sound_play:
        return (60 / (int(bpm) * 4) - time_spent_for_sound_play)
    return (60 / (int(bpm) * 4))

def init_16_step_sequencer():
    step_seq_sound = {}
    for i in range(16):
        step_seq_sound[i] = None
    return step_seq_sound

def play_one_step(bpm, step_seq_sounds, step):
    start_time = time.time()
    for step_seq_sound in step_seq_sounds:
        if step_seq_sound[step]:
            channel = pygame.mixer.find_channel()
            channel.play(step_seq_sound[step])
    end_time = time.time()
    time_delta = end_time - start_time
    time.sleep(sleep_time_calculation(bpm, time_delta))

def sequencer(bpm_queue, queue_for_sounds_dict, start_stop_queue):
    step = 0
    step_seq_sounds = queue_for_sounds_dict.get() # should not be empty the first time we start sequencer
    bpm = bpm_queue.get()
    sequencer_active = False
    while True:
        if not start_stop_queue.empty():
            start_stop_queue.get() # empty the queue
            sequencer_active = not sequencer_active
        if sequencer_active:
            play_one_step(bpm, step_seq_sounds, step)
            step += 1
            if step == 16:
                step = 0
                #Refresh sound dict and bpm
                if not queue_for_sounds_dict.empty():
                    step_seq_sounds = queue_for_sounds_dict.get()
                if not bpm_queue.empty():
                    bpm = bpm_queue.get()
