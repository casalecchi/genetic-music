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
                     pauses: int, key: str, scale: str, root: int) -> Dict[str, list]:
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
    

    steps = []
    # Applying the scale on notes 
    for step in range(num_steps):
        for note in melody["notes"]:
            steps.append(scl[(note + step*2) % len(scl)])

    melody["notes"] = steps
    return melody

# print(genome_to_melody([1, 0, 1, 1, 1, 1, 0, 0, 0, 1, 0, 1, 0, 1, 1, 1], 1, 4, 1, 0, "C", "major", 1))
