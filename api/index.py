from flask import Flask, request
from flask_cors import CORS
import json
import csv
import base64
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/', methods=["POST"])
def home():
    if request.method == "POST":
        data = request.get_json()
        encoded_output = generate_outfile(data["inputFile"])
        print(type(encoded_output))
        return json.dumps({"status": "SUC", "data": encoded_output})

    else:
        return json.dumps({"status": "ERR", "message": "Endpoint expected POST request"})

# Rower class to represent data a bit better
class Rower:
    # Constructor
    def __init__(self, first_name, last_name, seed, event_num):
        self.first_name = first_name
        self.last_name = last_name
        self.seed = seed
        self.event_num = event_num
        self.formatted_name = self.last_name + self.first_name[:3] # Format names as lastname and the first three letters of the first name
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.seed}"
    
    def __repr__(self):
        return f"{self.first_name} {self.last_name} - {self.seed}"
    
    # Convert the time in seconds back into a readable format
    def seed_in_seconds_to_mins(self):
        if self.seed == 9999:
            # resolve the workaround I did for no time entries
            return "0:00"
        else:
            mins = self.seed // 60
            seconds = self.seed - (mins * 60)
            return f"{mins}:{str(seconds).zfill(2)}"

def generate_outfile(encoded_infile):
    # decode our input file from base64 into a readable format
    encoded = base64.b64decode(encoded_infile)
    with open("/tmp/temp.csv", "w") as temp_file:
        temp_file.write(encoded.decode("utf-8"))

    #  ------------------------------------------------
    # CONSTANTS - Used for referencing column numbers so that code is more readable
    EVENT_ID = 0
    FIRST_NAME = 6
    LAST_NAME = 7
    SEED = 11

    rowers = [] # list for all rower objects
        
    #  ------------------------------------------------
    # READING INPUT CSV

    with open("/tmp/temp.csv", "r") as csv_file:
        csv_reader = csv.reader(csv_file)
        # disregard column headers
        next(csv_reader)
        for row in csv_reader:
            # Convert the seeding times into seconds using string manipulation (makes sorting much easier and can be easily converted back and forth)
            seed = row[SEED].split(":")
            seed_in_seconds = int(seed[0]) * 60 + int(seed[-1])
            if seed_in_seconds == 0:
                # arbitrarily high number so that 0:00 seed entries get sorted last
                seed_in_seconds = 9999
            # Populate our list of rowers
            rowers.append(Rower(row[FIRST_NAME], row[LAST_NAME], seed_in_seconds, row[EVENT_ID]))

    #  ------------------------------------------------
    # POSTPROCESSING

    # sort all rowers by their seed times
    rowers.sort(key=lambda x: x.seed)

    # dictionary (key, value pairs) that represent the events and their participants
    event_dict = {}

    # populate the event_dict, should preserve seeding order since we sorted beforehand
    for rower in rowers:
        # check if event has been discovered yet
        if rower.event_num not in event_dict.keys():
            # hasn't been discovered so create new list for its participants and add the first entry
            event_dict[rower.event_num] = []
            event_dict[rower.event_num].append(rower)
        else:
            # has been discovered so just add the next entry
            event_dict[rower.event_num].append(rower)

    #  ------------------------------------------------

    # WRITING TO OUTPUT
    with open("/tmp/race-entries.csv", "w") as file:
        csv_writer = csv.writer(file, delimiter=",")
        for k, v in event_dict.items():
            bow_num = 1
            csv_writer.writerow([f"EVENTID: {k}"])
            for rower in v:
                csv_writer.writerow([bow_num, rower.formatted_name, rower.seed_in_seconds_to_mins()])
                if bow_num == 16:
                    csv_writer.writerow(["END OF HEAT"])
                    bow_num = 1
                else:
                    bow_num += 1

    # convert to base64 string and return
    with open("/tmp/race-entries.csv", "r") as file:
        contents = file.read()

    file_bytes = contents.encode("utf-8")
    encoded_bytes = base64.b64encode(file_bytes)

    # raise Exception(f"{type(encoded_bytes.decode("utf-8"))} - {encoded_bytes.decode("utf-8")}")

    return encoded_bytes.decode("utf-8")

