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

def set_sounds_dict_preset_1(samples):
    kick01 = samples['kick01.wav']
    step_seq_sound = {}
    for i in range(16):
        step_seq_sound[i] = None
    step_seq_sound[0] = kick01
    step_seq_sound[4] = kick01
    step_seq_sound[8] = kick01
    step_seq_sound[12] = kick01
    return step_seq_sound

def set_sounds_dict_preset_2(samples):
    hat = samples['hat 10.wav']
    step_seq_sound = {}
    for i in range(16):
        step_seq_sound[i] = None
    step_seq_sound[0] = hat
    step_seq_sound[4] = hat
    step_seq_sound[8] = hat
    step_seq_sound[12] = hat
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


def print_step_seq_state(step_seq_sounds):
    for step_seq_sound in step_seq_sounds:
        print('\nSamples loaded on sequencer:\n')
        for step, sample in step_seq_sound.items():
            if not sample is None:
                print('STEP ' + str(step) + ' FULL')
            else:
                print('STEP ' + str(step) + ' EMPTY :\'(')

def discover_and_load_samples(samples_path):
    samples_dict = {}
    for root, directories, filenames in os.walk(samples_path):
        for filename in filenames:
            sample = { filename : pygame.mixer.Sound(os.path.join(samples_path, filename)) }
            samples_dict.update(sample)
    return samples_dict

def print_samples(samples):
    i = 0
    samples_dict = {}
    for key, value in samples.items():
        print(str(i) + ' - ' + str(key))
        samples_dict[i] = key # {id = sample_name} to be able to select just with id
        i += 1
    return samples_dict

def switch_sample_for_one_step(active_sequencer, samples, step_seq_sounds, queue_for_sounds_dict):
    samples_dict = print_samples(samples)
    sample_selected = int(input('\nEnter sample number...\n'))
    step_selected = int(input('\nEnter step that will play sample (from 0 to 15)...\n'))
    step_seq_sounds[active_sequencer][step_selected] = samples[samples_dict[sample_selected]]
    queue_for_sounds_dict.put(step_seq_sounds)

def switch_bpm(bpm_queue):
    bpm = int(input('\nEnter new BPM pleasey...\n'))
    bpm_queue.put(bpm)

def play_samples(samples):
    samples_dict = print_samples(samples)
    sample_selected = int(input('\nEnter sample number...\n'))
    channel = pygame.mixer.find_channel()
    channel.play(samples[samples_dict[sample_selected]])

def sequencer_menu(samples, step_seq_sounds, queue_for_sounds_dict, start_stop_queue, bpm_queue):
    active_sequencer = 0
    while True:
        print('\nActions:\n\n'
              '1. Start and stop sequencer\n'
              '2. Show all sequencers state\n'
              '3. Switch with available samples\n'
              '4. Update BPM for more fun\n'
              '5. Listen to samples\n'
              '6. Switch active sequencer\n')
        action = int(input('\n\nWaiting for input dear...\n'))
        if action == 1:
            start_stop_queue.put(action)
        elif action == 2:
            print_step_seq_state(step_seq_sounds)
        elif action == 3:
            switch_sample_for_one_step(active_sequencer, samples, step_seq_sounds, queue_for_sounds_dict)
        elif action == 4:
            switch_bpm(bpm_queue)
        elif action == 5:
            play_samples(samples)
        elif action == 6:
            if active_sequencer == 0:
                active_sequencer = 1
                print('\nActive sequencer is now seq 1')
            else:
                active_sequencer = 0
                print('\nActive sequencer is now seq 0')

def init_pygame_module():
    pygame.mixer.init(44100, -16, 2, 1024)
    pygame.mixer.set_num_channels(32)
    pygame.init()

def main():
    init_pygame_module()
    clear_screen()

    bpm_queue = queue.Queue()
    bpm = input('Give me a BPM, I will create a party...\n\n')
    bpm_queue.put(bpm)

    print('Adding default samples on sequencer...\n\n')
    step_seq_sounds = []
    samples = discover_and_load_samples('lo_fi_drum_kit')
    step_seq_sounds.append(set_sounds_dict_preset_1(samples))
    step_seq_sounds.append(set_sounds_dict_preset_2(samples))
    queue_for_sounds_dict = queue.Queue()
    start_stop_queue = queue.Queue()
    queue_for_sounds_dict.put(step_seq_sounds)
    print_step_seq_state(step_seq_sounds)

    sequencer_thread = threading.Thread(target=sequencer, args=(bpm_queue, queue_for_sounds_dict, start_stop_queue))
    sequencer_thread.start()

    menu_thread = threading.Thread(target=sequencer_menu, args=(samples, step_seq_sounds, queue_for_sounds_dict, start_stop_queue, bpm_queue))
    menu_thread.start()

if __name__ == '__main__':
    main()
