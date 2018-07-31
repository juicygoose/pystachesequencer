import time
import pygame
import os
import threading, queue

def sleep_time_calculation(bpm, time_spent_for_sound_play):
    if time_spent_for_sound_play:
        return (60 / (int(bpm) * 4) - time_spent_for_sound_play)
    return (60 / (int(bpm) * 4))

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def set_sounds_dict(step_seq_sounds, samples):
    kick01 = samples['kick01.wav']
    for i in range(16):
        step_seq_sounds[i] = None
    step_seq_sounds[0] = kick01
    step_seq_sounds[4] = kick01
    step_seq_sounds[8] = kick01
    step_seq_sounds[12] = kick01
    return step_seq_sounds

def play_one_step(bpm, step_seq_sounds, step):
    if step_seq_sounds[step]:
        start_time = time.time()
        channel = pygame.mixer.find_channel()
        channel.play(step_seq_sounds[step])
        end_time = time.time()
        time_delta = end_time - start_time
    else:
        time_delta = None

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


def print_step_seq_state(step_seq_sounds):
    print('Samples loaded on sequencer:\n')
    for step, sample in step_seq_sounds.items():
        if not sample is None:
            print('STEP ' + str(step) + ' CONTAINS SAMPLE')
        else:
            print('STEP ' + str(step) + ' CONTAINS no sample :\'(')

def discover_and_load_samples(samples_path):
    samples_dict = {}
    for root, directories, filenames in os.walk(samples_path):
        for filename in filenames:
            sample = { filename : pygame.mixer.Sound(os.path.join(samples_path, filename)) }
            samples_dict.update(sample)
    return samples_dict

def print_samples(samples):
    i = 0
    for key, value in samples.items():
        print(str(i) + ' - ' + str(key))
        i += 1

def switch_sample_for_one_step(samples, step_seq_sounds, queue_for_sounds_dict):
    print_samples(samples)
    sample_selected = input('\nEnter sample name...\n')
    step_selected = int(input('\nEnter step that will play sample...\n'))
    step_seq_sounds[step_selected] = samples[sample_selected]
    queue_for_sounds_dict.put(step_seq_sounds)

def switch_bpm(bpm_queue):
    bpm = int(input('\nEnter new BPM pleasey...\n'))
    bpm_queue.put(bpm)

def sequencer_menu(samples, step_seq_sounds, queue_for_sounds_dict, start_stop_queue, bpm_queue):
    while True:
        print('\nActions:\n\n'
              '1. Start and stop sequencer\n'
              '2. Show sequencer\'s load\n'
              '3. Switch with available samples\n'
              '4. Update BPM for more fun\n')
        action = int(input('\n\nWaiting for input dear...\n'))
        if action == 1:
            start_stop_queue.put(action)
        elif action == 2:
            print_step_seq_state(step_seq_sounds)
        elif action == 3:
            switch_sample_for_one_step(samples, step_seq_sounds, queue_for_sounds_dict)
        elif action == 4:
            switch_bpm(bpm_queue)

def main():
    pygame.mixer.init(44100, -16, 2, 1024)
    pygame.mixer.set_num_channels(32)
    pygame.init()
    clear_screen()
    bpm_queue = queue.Queue()
    bpm = input('Give me a BPM, I will create a party...\n\n')
    bpm_queue.put(bpm)

    print('Adding default samples on sequencer...\n\n')
    step_seq_sounds = {}
    samples = discover_and_load_samples('lo_fi_drum_kit')
    step_seq_sounds = set_sounds_dict(step_seq_sounds, samples)
    queue_for_sounds_dict = queue.Queue()
    start_stop_queue = queue.Queue()
    queue_for_sounds_dict.put(step_seq_sounds)
    print_step_seq_state(step_seq_sounds)

    sequencer_thread = threading.Thread(target=sequencer, args=(bpm_queue, queue_for_sounds_dict, start_stop_queue))
    sequencer_thread.start()

    menu_thread = threading.Thread(target=sequencer_menu, args=(samples, step_seq_sounds, queue_for_sounds_dict, start_stop_queue, bpm_queue))
    menu_thread.start()
    menu_thread.join()

if __name__ == '__main__':
    main()
