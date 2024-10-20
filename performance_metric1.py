from cortex import Cortex
import time
import random
from pythonosc import osc_message_builder
from pythonosc import udp_client
import openai
import ast
from dotenv import load_dotenv
import os
import re
import asyncio
import statistics
from concurrent.futures import ThreadPoolExecutor

# Initialize OpenAI and OSC client
openai.api_key = ""

# Read the prompt file
with open('music_generation_prompt.txt', 'r') as file:
    prompt = file.read()

# Create an OSC client
ip = "127.0.0.1"
port = 4560
client = udp_client.SimpleUDPClient(ip, port)

class MusicGenerator:
    def __init__(self):
        self.last_generation = None
        self.last_focus = None

    def format_music_for_prompt(self, result):
        """Convert the music result into a readable format for the prompt"""
        formatted_lines = []
        for item in result:
            if item[0] == 'synth':
                formatted_lines.append(f"synth :{item[1]}, note: :{item[2]}, release: {item[3]}, amp: {item[4]}")
            elif item[0] == 'sleep':
                formatted_lines.append(f"sleep {item[3]}")
        return "\n".join(formatted_lines)

    async def generate_music(self, average_focus):
        """Asynchronous function to generate music using OpenAI"""
        try:
            continuation_prompt = ""
            if self.last_generation and self.last_focus is not None:
                continuation_prompt = f"""
The previous music segment (at focus level {self.last_focus}/100) was:

{self.format_music_for_prompt(self.last_generation)}

Please create a natural musical continuation that transitions smoothly to the new focus level, maintaining thematic elements where appropriate while adjusting to the new intensity.
"""
            
            response = await asyncio.to_thread(
                openai.chat.completions.create,
                messages=[
                    {"role": "system", "content": prompt},
                    {
                        "role": "user",
                        "content": f"Generate music that, on a scale of 1 (very very slow and sad) to 100 (extremely fast, happy, and exciting, with lots of notes), has a value of {average_focus}/100. For higher values of focus, use triplets, 16th notes, sextuplets, and 32nd notes, in increasing order. For lower values of focus, use half notes, whole notes, and dotted half notes, in decreasing order. Use a variety of instruments and dynamics to create a piece that is engaging and exciting.{continuation_prompt}",
                    }
                ],
                model="gpt-4o",
            )

            result = []
            lines = response.choices[0].message.content.split('\n')

            synth_pattern = re.compile(r"synth :(\w+), note: :(\w+), release: ([\d.]+), amp: ([\d.]+)")
            sleep_pattern = re.compile(r"sleep ([\d.]+)")
            
            for line in lines:
                line = line.split('#')[0].strip()
                
                match = synth_pattern.match(line)
                if match:
                    instrument, note, release, amp = match.groups()
                    result.append(['synth', instrument, note, float(release), float(amp)])
                    continue
                
                match = sleep_pattern.match(line)
                if match:
                    duration = float(match.group(1))
                    result.append(['sleep', '', '', duration, ''])

            # Store this generation for next time
            self.last_generation = result
            self.last_focus = average_focus

            # Flatten the array
            flattened_data = []
            for sub_array in result:
                flattened_data.append("START")
                flattened_data.extend(sub_array)

            # Send OSC message
            client.send_message("/synth", flattened_data)
            if result:  # Only send ambient if we have a result
                client.send_message("/ambient", result[0][2])
            
        except Exception as e:
            print(f"Error generating music: {e}")

async def collect_eeg_data():
    """Asynchronous function to collect EEG data"""
    eeg_interval = 0.2
    previous_10_focus = [50]

    while True:
        # Simulate EEG data collection
        current_focus = random.randint(1, 100)

        previous_10_focus.append(current_focus)
        if len(previous_10_focus) > 10:
            previous_10_focus.pop(0)

        await asyncio.sleep(eeg_interval)
        average_focus = statistics.mean(previous_10_focus)
        print("current average recent focus:", average_focus)
        return average_focus

async def periodic_music_generation(music_generator):
    """Periodically generate music based on EEG data"""
    while True:
        average_focus = await collect_eeg_data()
        asyncio.create_task(music_generator.generate_music(average_focus))
        await asyncio.sleep(2)  # Wait 2 seconds before next generation

async def main():
    """Main async function to run both tasks concurrently"""
    music_generator = MusicGenerator()
    
    # Create tasks for both operations
    eeg_task = asyncio.create_task(collect_eeg_data())
    music_task = asyncio.create_task(periodic_music_generation(music_generator))
    
    try:
        # Run both tasks concurrently
        await asyncio.gather(eeg_task, music_task)
    except asyncio.CancelledError:
        print("Tasks cancelled")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program stopped by user")