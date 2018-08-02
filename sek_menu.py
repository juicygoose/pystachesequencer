def print_step_seq_state(step_seq_sounds):
    for step_seq_sound in step_seq_sounds:
        print('\nSamples loaded on sequencer:\n')
        for step, sample in step_seq_sound.items():
            if not sample is None:
                print('STEP ' + str(step) + ' FULL')
            else:
                print('STEP ' + str(step) + ' EMPTY :\'(')

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
