# Organized-TODO (In-Progress)
Organized-TODO is a python utility that allows users to manage a TODO list where all of the corresponding tasks are maintained in a master json file. The utility is being designed to be compatible with any app/service that can work with JSON data which means any developer can use this to quickly create their own custom TODO app.

This utillity is a command line utliity with a wide range of functionality. While I am still in the early phases of development I already have core functionality working (see feature list below).

--

## Features
  - Install Anywhere (Testing):
    This utility has been developed using relative paths which means this utility should work anywhere.
  - Advanced Search (In Development):
    There are several passable arguments that allow for advanced filtering (see syntax guide below)
  - Custom Status and Tags (In Development):
    Most TODO applications lock the status to a limited set of options. This utility has been designed to allow for free form statuses and 
    tags.
  - Categories (Testing):
    In order to better organize the possibly large amounts of tasks that a user may have, I have designed a simple category system. Each 
    task can be assigned to multiple categories.
  - Built in TODO list generator (Done) @temp @might_get_depreciated:
    More for testing purposes but this comes packaged with the ability to generate readable todo lists for VS Code. After perfoming a 
    search, the utliity will automatically generate the result and display it in VS Code. The interface is not ideal but it is functional.
    Make changes, save, and then run the utility with -c and it will merge your changes to the master.
  - Merge Multiple JSON Files:
    Any JSON file that follows the proper format (see JSON format section below) that is placed in the merge folder will be merged into the 
    master json file. You can place any number of files in the merge directory. run the utility with -c to merge. Note: the merge directory
    gets deleted during the clean up process so don't put files here unless you are 100% ready to merge.
--

## JSON Format

Tasks currently use the following information:
- id (number)
- name (string)
- created (datetime string)
- lastEdited (datetime string)
- categories (string array)
- description (string)
- status (string)

### General Format
The corresponding JSON file should be formatted as follows:
Schema:
  - ID (number)
  - name (string)
  - created (datetime string)
  - lastEdited (datetime string)
  - categories (string array)
  - description (string)
  - status (string)

Example:
```JSON
[
    {
        "id": 0,
        "name": "Example",
        "created": "<datetime>",
        "lastEdited": "<datetime>",
        "categories": [
          "High Priority", "Phase 1"
        ],
        "description": "This is an example task",
        "status": "Created"
    },
    ...
]
```

### Creating New Tasks
In order to create a new task, simply enter a task that has the <strong>id</strong> "new". The command line utility will detect this and generate a new unique id. If you leave created and/or lastEdited blank, the utility will use the current datetime. 



