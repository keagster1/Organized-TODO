import json
import sys
import os
import datetime
import random
import shutil

# Object to store master JSON data
MASTER = []

# List of implemented commands
MasterCommands = ["-c", "-s", "m", "-cu"]

# Arrays to store command arguments
searchArgs = []
consolidateArgs = []
metaDataArgs = []

# JSON data that will be displayed
DISPLAY = []

# Debug flag to determine what logging information should be printed.
# VERBOSE, MINIMAL, NONE, SUPPRESSED
#   VERBOSE prints most operations and variable information. Very useful for debugging.
#   MINIMAL prints status information
#   NONE prints nothing except errors
#   SUPPRESSED will hide even errors
DEBUG_MODE = "VERBOSE"

# List of logs and their message type.
logs = []

logs.append(f"[LOG-VERBOSE]: ({datetime.datetime.now()}) Organized-TODO Interface Started")

def createJSONFromTODO():
    temp = []
    data = ''
    with open('./Tasks.otodo', 'r') as file:
        # Flags to improve parsing abilities
        task_flag = 0
        category_flag = 0
        status_flag = 0
        description_flag = 0
        metadata_flag = 0
        current_task = []
        tasks = []
        # Get tasks in current TODO list and store in object array for conversion
        for line in file:
            # search for beginning of task and ignore nested words with colons
            if(line.strip() == ''):
                continue
            if(":" in line and task_flag == 0):
                task_flag = 1
                category_flag = 0
                status_flag = 0
                description_flag = 0
                metadata_flag = 0
                current_task.append(f'"name": "{line.split(":")[0]}",') # should become the name without the colon
                description = ""
                logs.append(f"[LOG-VERBOSE] {datetime.datetime.now()} Found task: {current_task[0]}")
            # current_task details (category, description, metadata)
            if(task_flag == 1):
                # need to search for categories, status, description, and metadata.
                # Should I allow this in any order? I'm thinking no for now.
                # "categories": ["High Priority", "test"],
                if("Categories=" in line and category_flag == 0):
                    category_flag = 1
                    current_task.append(f'"categories": "{line.split(":")[0]}",') # ['High Priority', 'test']
                    continue

                # status
                if("#" in line and status_flag == 0):
                    status_flag = 1
                    status = line.split(":")[0].split("#")[1].replace("\n", "")
                    current_task.append(f'"status": "{status}",')
                    continue

                # find description start (metadata will mark the end I guess)
                if("Description:" in line and description_flag == 0):
                    description_flag = 1
                    description = '"description": "'
                    continue
                
                # Assume we are parsing description until metadata: is reached
                if(description_flag == 1 and "metadata:" not in line): # Still parsing description
                    # escape quotations
                    description = description + line.replace('"', '\"').replace('"', '\\"').replace("\t", '\\t')
                elif("metadata:" in line and metadata_flag == 0): # check if metadata was reached
                    if(description_flag == 0): # this shouldn't happen so error
                        logs.append(f"[Error] ({datetime.datetime.now()}) Task details are out of order. Please ensure that you follow title, description, and then metadata")
                        return
                    description = description.replace("\n", "\\n")
                    current_task.append(f'{description}",')
                    description_flag = 2 #indicates that we are done with description
                    metadata_flag = 1

                # Parse meta data (should be one line)
                if(metadata_flag == 1):
                    metadata = line.split('metadata:')[1].split("@")
                    current_task.append(f'{metadata[1]},')
                    current_task.append(f'{metadata[2]},')
                    current_task.append(f'{metadata[3]},')
                    current_task.append(f'{metadata[4]},')
                    metadata_flag = 3
                    tasks.append(current_task)
                    current_task = []
                    task_flag = 0
                    continue
    
    # covert metadata, categories, status, and description to JSON format
    for task in tasks:
        if("id" in task[4]): # @id(0) => "id": 0,
            temp = task[4] # should be where id is stored
            num = temp.split("(")[1].split(")")[0]
            task[4] = f'"id": {num},'
        if("created" in task[6]): # task_created(2018-11-28T01:01:01)\n => "created": "2018-11-28T01:01:01"
            temp = task[6] # should be where id is stored
            date = temp.split("(")[1].split(")")[0]
            task[6] = f'"created": "{date}",'
        if("last" in task[5]): # task_created(2018-11-28T01:01:01)\n => "created": "2018-11-28T01:01:01"
            temp = task[5] # should be where id is stored
            date = temp.split("(")[1].split(")")[0]
            task[5] = f'"lastEdited": "{date}",'
        if("delete" in task[7]):
            temp = task[7] # should be where id is stored
            delete_flag = temp.split("(")[1].split(")")[0]
            task[7] = f'"delete": {delete_flag.lower()}'
        if("categories" in task[1]):
            # get categories from string - Categories=['High Priority', 'test']
            temp = task[1].split("[")[1].split("]")[0]
            temp = temp.replace("'", '"')

            # form JSON string
            categories = '"categories": ['
            for cat in temp.split(","):
                categories = categories + f'{cat},'
            categories = categories[0:len(categories)-1] + "],"
            task[1] = categories

    # Convert stored tasks to readable format
    json_text = []
    json_text.append("[\n")
    for task in tasks:
        json_text.append('\t{\n')
        json_text.append(f'\t\t{task[4]}\n') # "id": <id> Need to parse this more
        json_text.append(f'\t\t{task[0]}\n') # name
        json_text.append(f'\t\t{task[6]}\n') # task created
        json_text.append(f'\t\t{task[5]}\n') # last edited
        json_text.append(f'\t\t{task[1]}\n') # categories
        json_text.append(f'\t\t{task[3]}\n') # description
        json_text.append(f'\t\t{task[2]}\n') # status
        json_text.append(f'\t\t{task[7]}\n') # delete flag
        json_text.append('\t},\n')
    json_text.pop() # remove trailing comma
    json_text.append('\t}\n')
    json_text.append("]")

    # save JSON
    with open('./.ignore/consolidate.json', 'w') as file:
        for line in json_text:
            file.write(line)

    return True

def createTODOFromJSON():
    global DISPLAY

    logs.append(f"[LOG-VERBOSE]: ({datetime.datetime.now()}) Generating TODO from JSON")

    # Array to store lines of to-be-created TODO file
    txt = []
    for task in DISPLAY:
        txt.append(f"{task['name']}:\n")
        txt.append(f"\tCategories={task['categories']}\n")
        txt.append(f"\t#{task['status']}\n")
        txt.append(f"\tDescription:\n{task['description']}\n")
        txt.append(f"\tmetadata: @id({task['id']}) @last_edited({task['lastEdited']}) @task_created({task['created']}) @delete({task['delete']})")
        txt.append("\n\n")

    logs.append(f"[LOG-VERBOSE]: ({datetime.datetime.now()}) Saving generated TODO to Tasks.otodo")
    with open("Tasks.otodo", "w") as file:
        for line in txt:
            file.write(line)
    
    return True

def log():
    for entry in logs:
        if(DEBUG_MODE != "SUPPRESSED" and (DEBUG_MODE in entry or "ERROR" in entry)):
            print(entry)
        
"""
    Generates an unsused ID to use for new tasks.
    Called when a new task is detected in consolidate().
"""
def generateID():
    global MASTER

    logs.append(f"[LOG-VERBOSE] {datetime.datetime.now()} Found new task, generating unused ID")

    found_ids = []
    for task in MASTER:
        found_ids.append(task['id'])

    # initialize randomizer
    random.seed(a=None)
    num = 0
    while(num in found_ids):
        num = random.randint(0,100000)

    logs.append(f"[LOG-VERBOSE] {datetime.datetime.now()} Set ID to {num}")
    return num

# Merge edited tasks with master task list
def consolidate(index):
    global MASTER
    merge_flag = 0

    # if any file is found in the merge folder, use those files insted of consolidate.json. 
    root_dir = './merge/'
    merge_files = []
    try:
        merge_files = [item for item in os.listdir(root_dir) if os.path.isfile(os.path.join(root_dir, item))]
    except:
        print("No merge files found. Using Tasks.otodo")

    if(len(merge_files) > 0):
        merge_flag = 1

        # merge each file in found order
        for f in merge_files:
            merge(f"./merge/{f}")

    else:
        # convert TODO into JSON
        createJSONFromTODO()

        # Finally merge files
        merge("./.ignore/consolidate.json")

    # load master file
    with open("./.ignore/master_list.json", "r") as file:
        MASTER = json.load(file)

    # Delete any tasks in MASTER that have the deleted flag set to true
    delete_flag = 0
    for task in MASTER:
        if(task['delete'] == True):
            delete_flag = 1
            print("found delete")
            MASTER.remove(task)

    # If any tasks are deleted, update MASTER file
    with open("./.ignore/master_list.json", "w") as file:
        json.dump(MASTER, file, indent=4)

    # Delete merge files afterwards to avoid duplicate merging
    cleanUp()

def merge(f):
    # iterate through master_list and find differences
    # id's found in consolidate.json but not master will be treated as a new task
    # id's found in master but not consolidate will be ignored

    consolidate = ""

    # load JSON into DISPLAY
    with open(f, "r") as file:
        consolidate = json.load(file)

    update_count = 0
    for task in MASTER:
        if(update_count >= len(consolidate)):
            break
        for ctask in consolidate:
            if(ctask['id'] == 'new'):
                ctask['id'] = generateID()
                ctask['created'] = f'{datetime.datetime.now().isoformat()}'
                ctask['lastEdited'] = f'{datetime.datetime.now().isoformat()}'
                MASTER.append(ctask)
                update_count += 1
            elif(ctask['id'] == task['id']): # found match, update values
                update_count += 1
                changed = 0
                if ctask['name'] != task['name']:
                    task['name'] = ctask['name']
                    changed = 1
                if ctask['created'] != task['created']:
                    task['created'] = ctask['created']                     
                if ctask['categories'] != task['categories']:
                    task['categories'] = ctask['categories'] 
                    changed = 1
                if ctask['description'] != task['description']:
                    task['description'] = ctask['description']
                    changed = 1
                if ctask['status'] != task['status']:
                    task['status'] = ctask['status'] 
                    changed = 1
                if ctask['delete'] != task['delete']:
                    task['delete'] = ctask['delete']
                    changed = 1
                if changed == 1:
                    task['lastEdited'] = f'{datetime.datetime.now().isoformat()}'

    with open('./.ignore/master_list.json', "w") as file:
        json.dump(MASTER, file, indent=4)

    print(f"{update_count}/{len(consolidate)} Tasks successfully consolidated. ")

    return True

def search(index):
    global MasterCommands, DEBUG_MODE, MASTER, DISPLAY

    # Valid/Implemented arguments
    arguments = {
        "-aa",
        "-ao"
    }

    current_command = []

    # Get arguments
    for i in range(index, len(sys.argv)):
        arg = sys.argv[i]

        # Only gather search related commands
        if(arg not in MasterCommands):
            if(arg in arguments):
                logs.append(f"[LOG-VERBOSE]: ({datetime.datetime.now()}) Found valid arg {arg}")
                current_command.append(arg)
            else: #i.e. not a command but a value to be added to last mentioned command
                logs.append(f"[LOG-VERBOSE]: ({datetime.datetime.now()}) Found value {arg}")
                current_command.append(arg)

    # Add full command to searchAruguments once the next command is reached or last arg is reached.
    if(True):
        searchArgs.append(current_command)
        current_command = []

    # iterate over commands
    DISPLAY = []
    for command in searchArgs:
        if(len(searchArgs) < 1):
            return
        if(command[0] == '-aa'): # Search everything (AND) This means that the task must contain all specified strings
            logs.append(f"[LOG-VERBOSE]: ({datetime.datetime.now()}) Searching all details of task with AND logic")
            # -aa has 1 required value and 0 optional values
            search = command[1].split(",")
            # Iterate over MASTER and check each piece for any of the given strings
            for task in MASTER:
                # search for each word
                # if a word is not found then found_flag is changed to 0 and the task wont be added.
                found_flag = 1
                for word in search:
                    word = word.strip()
                    if(word in task['name'] or word in task['created'] or word in task['lastEdited'] or word in task['created'] or word in task['lastEdited'] or word in task['categories'] or word in task['description'] or word in task['description'] or word in task['status']):
                       continue
                    else:
                        found_flag = 0
                        logs.append(f"[LOG-VERBOSE] {datetime.datetime.now()} Word {word} not found in task. {task['name']}")
                        break
                if(found_flag == 1):
                    logs.append(f"[LOG-VERBOSE]: ({datetime.datetime.now()}) Found matching task")
                    DISPLAY.append(task)
        elif(command[0] == '-ao'): # Search everything (OR) This means that the task must contain one of the specified strings
            logs.append(f"[LOG-VERBOSE]: ({datetime.datetime.now()}) Searching all details of task with OR logic")
            # -ao has 1 required value and 0 optional values
            search = command[1].split(",")
            # Iterate over MASTER and check each piece for any of the given strings
            count = 0
            for task in MASTER:
                # search for each word
                for word in search:
                    count += 1
                    word = word.strip()
                    if(word in task['name'] or word in task['created'] or word in task['lastEdited'] or word in task['categories'] or word in task['description'] or word in task['status']):
                        logs.append(f"[LOG-VERBOSE]: ({datetime.datetime.now()}) Found matching task")
                        DISPLAY.append(task)
                        break

    print(DISPLAY)

    # Don't do anything else if no results were found
    if(len(DISPLAY) == 0):
        logs.append("[ERROR]: No tasks found with that search query.")
        return False

    # Store DISPLAY in DISPLAY.json list for viewing and editing purposes.
    logs.append(f"[LOG-VERBOSE]: ({datetime.datetime.now()}) Saving results in /.ignore/display.json")
    with open("./.ignore/display.json", "w") as file:
        json.dump(DISPLAY, file)

    # Covert JSON to TODO format. Automatically uses DISPLAY
    createTODOFromJSON()

    # open file in VS Code
    logs.append(f"[LOG-VERBOSE]: ({datetime.datetime.now()}) Opening Tasks.otodo in VS Code")
    os.system('code ./Tasks.otodo')

    return True

def getMetaData():
    # Display statistics and other information about the MASTER list
    # In the future I may allow arguments that change the behavior
    #   For example: display statistics after a search
    return True

def getTotalTasks():
    count = 0
    global MASTER
    for task in MASTER:
        count += 1
    return count

def cleanUp():
    display_path = './.ignore/display.json'
    consolidate_path = './.ignore/consolidate.json'
    merge_path = './merge/'
    if os.path.isfile(display_path):
        os.remove(display_path)
    #if os.path.isfile(consolidate_path):
     #   os.remove(consolidate_path)
    
    # Delete merge directory
    try:    
        shutil.rmtree(merge_path)
    except:
        print("")

def runCommand(arg, index):
    if(arg == '-s'):
        logs.append(f"[LOG-MINIMAL]: ({datetime.datetime.now()}) Searching")
        logs.append(f"[LOG-VERBOSE]: ({datetime.datetime.now()}) Found search command")
        logs.append(f"[LOG-VERBOSE]: ({datetime.datetime.now()}) Cleaning up files for new search")
        cleanUp() # always clean up when a new search is performed.
        logs.append(f"[LOG-VERBOSE]: ({datetime.datetime.now()}) Entering Search")
        return(search(index))
    elif(arg == '-c'):
        logs.append(f"[LOG-MINIMAL]: ({datetime.datetime.now()}) Consolidating")
        logs.append(f"[LOG-VERBOSE]: ({datetime.datetime.now()}) Entering Consolidate")
        return(consolidate(index))
    elif(arg == 'm'):
        logs.append(f"[LOG-MINIMAL]: ({datetime.datetime.now()}) Getting Metadata")
        logs.append(f"[LOG-VERBOSE]: ({datetime.datetime.now()}) Entering Metadata")
        return(getMetaData())
    elif(arg == '-cu'):
        logs.append(f"[LOG-MINIMAL]: ({datetime.datetime.now()}) Cleaning Up")
        logs.append(f"[LOG-VERBOSE]: ({datetime.datetime.now()}) Entering Clean up")
        return(cleanUp())
    else:
        return False


# Load JSON data into global object
def load():
    global MASTER
    with open('./.ignore/master_list.json', 'r') as f:
        MASTER = json.load(f)

# Parse and organize passed commands
def parse():
    # start at 0 because name of file is arg[0]
    index = 0
    for arg in sys.argv:
        index += 1
        if("-" in arg):
            # validate and run
            runCommand(arg, index)
        else:
            continue        

if __name__ == "__main__":
    load()
    parse()
    logs.append(f"[LOG-MINIMAL]: ({datetime.datetime.now()}) Done")
    log()