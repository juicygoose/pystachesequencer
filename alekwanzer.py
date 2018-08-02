import sek_menu
import sekwanzer

import pygame
import os
import threading, queue

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def set_sounds_dict_preset_1(samples):
    kick01 = samples['kick01.wav']
    step_seq_sound = sekwanzer.init_16_step_sequencer()
    step_seq_sound[0] = kick01
    step_seq_sound[4] = kick01
    step_seq_sound[8] = kick01
    step_seq_sound[12] = kick01
    return step_seq_sound

def set_sounds_dict_preset_2(samples):
    hat = samples['hat 10.wav']
    step_seq_sound = sekwanzer.init_16_step_sequencer()
    step_seq_sound[0] = hat
    step_seq_sound[4] = hat
    step_seq_sound[8] = hat
    step_seq_sound[12] = hat
    return step_seq_sound

def discover_and_load_samples(samples_path):
    samples_dict = {}
    for root, directories, filenames in os.walk(samples_path):
        for filename in filenames:
            sample = { filename : pygame.mixer.Sound(os.path.join(samples_path, filename)) }
            samples_dict.update(sample)
    return samples_dict

def init_pygame_module():
    pygame.mixer.init(44100, -16, 2, 1024)
    pygame.mixer.set_num_channels(32)
    pygame.init()

def main():
    init_pygame_module()
    clear_screen()

    # Queues used to share variables between sequencer thread and menu thread
    bpm_queue = queue.Queue()
    queue_for_sounds_dict = queue.Queue()
    start_stop_queue = queue.Queue()

    bpm = input('Give me a BPM, I will create a party...\n\n')
    bpm_queue.put(bpm)

    print('Adding default samples on sequencer...\n\n')
    step_seq_sounds = []
    samples = discover_and_load_samples('lo_fi_drum_kit')

    # Adding two sequencers with default samples loaded
    step_seq_sounds.append(set_sounds_dict_preset_1(samples))
    step_seq_sounds.append(set_sounds_dict_preset_2(samples))
    queue_for_sounds_dict.put(step_seq_sounds)

    sequencer_thread = threading.Thread(target=sekwanzer.sequencer, args=(bpm_queue, queue_for_sounds_dict, start_stop_queue))
    sequencer_thread.start()

    menu_thread = threading.Thread(target=sek_menu.sequencer_menu, args=(samples, step_seq_sounds, queue_for_sounds_dict, start_stop_queue, bpm_queue))
    menu_thread.start()

if __name__ == '__main__':
    main()
