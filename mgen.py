from algorithm.genetic import Genome, generate_genome, selection_pair, single_point_crossover, mutation
import click
from datetime import datetime
from midiutil import MIDIFile
from pyo import *
from typing import List, Dict

BITS_PER_NOTE = 4
KEYS = ["C", "C#", "Db", "D", "D#", "Eb", "E", "F", "F#", "Gb", "G", "G#", "Ab", "A", "A#", "Bb", "B"]
SCALES = ["major", "minorM", "dorian", "phrygian", "lydian", "mixolydian", "majorBlues", "minorBlues"]


def int_from_bits(bits: List[int]) -> int:
    """Get a binary number in a List and returns in the decimal form"""
    return int(sum([bit * (2 ** index) for index, bit in enumerate(bits)]))


def genome_to_melody(genome: Genome, num_bars: int, num_notes: int, num_steps: int,
                     pauses: bool, key: str, scale: str, root: int) -> Dict[str, list]:
    """Convert a Genome to a Dict"""

    note_length = 4 / float(num_notes)
    
    # scl will be an object like a list
    scl = EventScale(root=key, scale=scale, first=root)

    melody = {
        "notes": [],
        "velocity": [],
        "beat": []
    }

    notes = []
    # Separate the genome in notes
    for i in range(num_bars * num_notes):
        note = genome[(i * BITS_PER_NOTE) : (i * BITS_PER_NOTE + BITS_PER_NOTE)]
        notes.append(note)

    for note in notes:
        integer = int_from_bits(note)

        if not pauses:
            # This will make the integer between 0 and (2^BITS_PER_NOTE)-1
            # By making this, the pause condition will never be satisfied
            integer = int(integer % (2 ** BITS_PER_NOTE - 1))

        if integer >= (2 ** BITS_PER_NOTE - 1):
            # This is a pause
            melody["notes"] += [0]
            melody["velocity"] += [0]
            melody["beat"] += [0]

        else:
            if len(melody["notes"]) > 0 and melody["notes"][-1] == integer:
                # This represents the same note duplicated
                # We just add more length to it's beat
                melody["beat"][-1] += note_length
            
            else:
                # Create the melody of a single note
                melody["notes"] += [integer]
                melody["velocity"] += [127]
                melody["beat"] += [note_length]
    

    steps = [[]]
    # Applying the scale on notes 
    for step in range(num_steps):
        for note in melody["notes"]:
            steps[0].append(scl[(note + step*2) % len(scl)])

    melody["notes"] = steps
    return melody


def genome_to_events(genome: Genome, num_bars: int, num_notes: int, num_steps: int,
                     pauses: bool, key: str, scale: str, root: int, bpm: int) -> List[Events]:
    """Will create the list of Events objects, given a Genome."""

    melody = genome_to_melody(genome, num_bars, num_notes, num_steps, pauses, key, scale, root)

    events = []
    for step in melody["notes"]:
        # EventSeq will create like an array of pyo
        # Events is the main object in pyo -> "the sound of a note"
        event = Events(
                    midinote=EventSeq(step, occurrences=1),  # pitch
                    midivel=EventSeq(melody["velocity"], occurrences=1),  # gain
                    beat=EventSeq(melody["beat"], occurrences=1),  # duration
                    attack=0.001, 
                    decay=0.05, 
                    sustain=0.5, 
                    release=0.005,
                    bpm=bpm
                )
        events.append(event)
    
    return events


def fitness(genome: Genome, s: Server, num_bars: int, num_notes: int, num_steps: int,
            pauses: bool, key: str, scale: str, root: int, bpm: int) -> int:
    """Evaluation of a genome."""
    
    # m = metronome(bpm)

    events = genome_to_events(genome, num_bars, num_notes, num_steps, pauses, key, scale, root, bpm)
    
    # For each sound created, play
    for e in events:
        e.play()
    s.start()

    # The user will be the fitness function
    rating = input("Rating (0-5)")

    # Stop the sound
    for e in events:
        e.stop()
    s.stop()
    time.sleep(1)

    try:
        rating = int(rating)
    except ValueError:
        rating = 0

    return rating


def save_genome_to_midi(filename: str, genome: Genome, num_bars: int, num_notes: int, num_steps: int,
                        pauses: bool, key: str, scale: str, root: int, bpm: int):
    """Function to save Genomes created to MIDIFiles."""
    
    melody = genome_to_melody(genome, num_bars, num_notes, num_steps, pauses, key, scale, root)

    if len(melody["notes"][0]) != len(melody["beat"]) or len(melody["notes"][0]) != len(melody["velocity"]):
        raise ValueError

    mf = MIDIFile(1)

    track = 0
    channel = 0

    time = 0.0
    mf.addTrackName(track, time, "Sample Track")
    mf.addTempo(track, time, bpm)

    for i, vel in enumerate(melody["velocity"]):
        if vel > 0:
            for step in melody["notes"]:
                mf.addNote(track, channel, step[i], time, melody["beat"][i], vel)

        time += melody["beat"][i]

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "wb") as f:
        mf.writeFile(f)


s = Server().boot()
print(fitness([1, 0, 1, 1, 1, 1, 0, 0, 0, 1, 0, 1, 0, 1, 1, 1], s, 1, 4, 1, False, "C", "major", 1, 100))
