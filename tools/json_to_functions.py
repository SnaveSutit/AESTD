##################################### Libs #####################################

from tkinter import *
import tkinter.filedialog
import glob
import json
import os.path
import json_to_nbt

##################################### Objs #####################################

class MinecraftObject:
    def __init__(self,data,parent):
        self.name = data["name"]
        self.id = data["id"]
        self.nbt = json_to_nbt.convert_nbt(data["nbt"])
        self.data = data
        self.parent = parent
        self.attributes = []
        if "attributes" in data.keys():
            self.attributes = data["attributes"]
        if "no_build" not in self.attributes:
            self.build_commands()

    def build_commands(self):
        pass

    def write_commands(self,name,commands):
        write("Writing "+name+".mcfunction command for "+self.data["type"]+" "+self.name+"\n")
        file = open(self.parent + "/" + name + ".mcfunction",mode="w")
        file.write("# Generated by AESTD, Minecraft 18w50a\n")
        file.write("# Type: {}, name: {}\n\n".format(self.data["type"],self.name))
        list(map(lambda command: file.write(command + "\n"),commands))
        file.close()

class Block(MinecraftObject):
    def build_commands(self):
        commands_map = []
        if B_set.get() and "no_setblock" not in self.attributes: commands_map.append(self.write_setblock())
        if B_dat.get() and "no_data" not in self.attributes: commands_map.append(self.write_data())
        if B_giv.get() and "no_give" not in self.attributes: commands_map.append(self.write_give())
        for commands in commands_map:
            self.write_commands(commands[0],commands[1])

    def write_setblock(self):
        coordinates = "~ ~ ~"
        if "coordinates" in self.data.keys():
            coordinates = self.data["coordinates"]
            if coordinates[-1] == " ": coordinates = coordinates[:-1]
        
        state = ""
        if "state" in self.data.keys():
            state = self.data["state"]

        commands = ["setblock " + coordinates + " " + self.id + state + self.nbt]

        if "entity" in self.data.keys():
            self.data["entity"].update({"name": "", "type": "entity", "attributes": ["no_build"]})
            entity = Entity(self.data["entity"],parent="")
            commands.append(entity.write_summon()[1][0])
        
        return ("setblock",commands)

    def write_data(self):
        coordinates = "~ ~ ~"
        if "coordinates" in self.data.keys():
            coordinates = self.data["coordinates"]
            if coordinates[-1] == " ": coordinates = coordinates[:-1]
        
        return ("data",["data merge block " + coordinates + " " + self.nbt])

    def write_give(self):
        return ("give",["give @s " + self.id + self.nbt])

class Item(MinecraftObject):
    def build_commands(self):
        commands_map = []
        if I_giv.get() and "no_give" not in self.attributes: commands_map.append(self.write_give())
        if I_sum.get() and "no_summon" not in self.attributes: commands_map.append(self.write_summon())
        if I_rep.get() and "no_replaceitem" not in self.attributes: commands_map.append(self.write_replaceitem())
        for commands in commands_map:
            self.write_commands(commands[0],commands[1])
    
    def write_give(self):
        return ("give",["give @s " + self.id + self.nbt])

    def write_summon(self):
        return ("summon",["summon minecraft:item ~ ~ ~ {Item:{id:\"{}\",Count:1b,tag:{}}}\n".format(self.id,self.nbt)])

    def write_replaceitem(self):
        return ("replaceitem",["replaceitem entity @s mainhand {}{}".format(self.id,self.nbt)])

class Entity(MinecraftObject):
    def build_commands(self):
        commands_map = []
        if E_sum.get() and "no_summon" not in self.attributes: commands_map.append(self.write_summon())
        if E_dat.get() and "no_data" not in self.attributes: commands_map.append(self.write_data())
        if E_giv.get() and "no_give" not in self.attributes: commands_map.append(self.write_give())
        for commands in commands_map:
            self.write_commands(commands[0],commands[1])
    
    def write_summon(self):
        coordinates = "~ ~ ~"
        if "coordinates" in self.data.keys():
            coordinates = self.data["coordinates"]
            if coordinates[-1] == " ": coordinates = coordinates[:-1]

        commands = ["summon {} {} {}".format(self.id,coordinates,self.nbt)]
        if "spawn_commands" in self.data.keys():
            list(map(lambda command: commands.append(command),self.data["spawn_commands"]))
        
        return ("summon",commands)

    def write_data(self):
        commands = ["data merge entity @s " + self.nbt]
        if "data_commands" in self.data.keys():
            list(map(lambda command: commands.append(command),self.data["data_commands"]))
            
        return ("data",commands)

    def write_give(self):
        return ("give",["give @s {}_spawn_egg{{SpawnData:{}}}".format(self.id,self.nbt)])

##################################### Defs #####################################

def generate_objects():
    filenames = get_filenames()
    for filename in filenames:
        write("\n")
        open_file(filename)

def open_file(filename):
    file = open(filename,mode="r")
    try:
        data = json.load(file)
        parent = os.path.abspath(os.path.join(filename,os.pardir))
        file.close()

        if type(data) != dict: raise_error("no_compound",filename)
        elif "type" in data.keys() and data["type"] in ["item","block","entity"] and "id" in data.keys() and "nbt" in data.keys() and "name" in data.keys():
            if data["type"] == "item": items.append(Item(data,parent))
            elif data["type"] == "block": blocks.append(Block(data,parent))
            elif data["type"] == "entity": entities.append(Entity(data,parent))
            
        elif "type" not in data.keys(): raise_error("no_type",filename)
        elif "id" not in data.keys(): raise_error("no_id",filename)
        elif "nbt" not in data.keys(): raise_error("no_nbt",filename)
        elif "name" not in data.keys(): raise_error("no_name",filename)
        elif "type" in data.keys(): raise_error("wrong_type",filename)
    except json.decoder.JSONDecodeError:
        raise_error("invalid_json",filename)

def raise_error(reason,filename=""):
    message = MESSAGES[reason].format(filename.replace("\\","/"))
    write(message+"\n")

def write(text_):
    text.config(state=NORMAL)
    text.insert(END,text_)
    text.config(state=DISABLED)
    text.update()

def get_filenames():
    if mode.get() == "directory":
        if directory != "":
            write("Finding json files...\n")
            files = glob.glob(directory+"/**/*.json",recursive=True)
            write("Found "+str(len(files))+" files, generating commands\n")
            return files
        else:
            raise_error("no_directory")
    if mode.get() == "file":
        if directory != "":
            return [directory]
        else:
            raise_error("no_file")
    return []

def change_directory():
    global directory
    if mode.get() == "directory": directory = tkinter.filedialog.askdirectory(title="Select a folder")
    if mode.get() == "file": directory = tkinter.filedialog.askopenfilename(title="Select a file",initialdir=directory,filetypes=(("JSON files","*.json"),("All files","*.*"),("The subtlety of this Easter egg is too damn high","*.cvm")))

##################################### Main #####################################

## Window
window = Tk()
window.title("NBT to function generator")

## Variables

directory = ""
# Objects
items, entities, blocks = [], [], []
# Menu
mode = StringVar()
mode.set("directory")
E_sum = BooleanVar(); E_giv = BooleanVar(); E_dat = BooleanVar(); B_set = BooleanVar(); B_dat = BooleanVar(); B_giv = BooleanVar(); I_giv = BooleanVar(); I_sum = BooleanVar(); I_rep = BooleanVar()
E_sum.set(True); E_giv.set(True); E_dat.set(True); B_set.set(True); B_dat.set(True); B_giv.set(True); I_giv.set(True); I_sum.set(True); I_rep.set(True)
# Text
MESSAGES = {
        "wrong_type": "Could not load file {}: wrong type (must be item, entity or block)",
        "no_type": "Could not load file {}: missing type key",
        "invalid_json": "Could not load file {}: invalid json (Tip: verify json at https://jsonlint.com)",
        "no_id": "Could not load file {}: missing id key. Add an asterisk (*) for any",
        "no_nbt": "Could not load file {}: missing nbt key",
        "no_name": "Could not load file {}: missing name key",
        "missing_directory": "Could not load file {}: directory does not exist",
        "no_directory": "No files found, please select a directory",
        "no_file": "Please select a file",
        "no_compound": "Could not load file {}: root is not a compound"
    }

## Widgets

text = Text(window)
##text.config(state=DISABLED)
text.grid(row=0,column=0)

button = Button(window)
button.config(text="Generate files",command=generate_objects)
button.grid(row=1,column=0)

# Menu

menu = Menu(window)
file_menu = Menu(menu,tearoff=0)
options_menu = Menu(menu,tearoff=0)
functions1_menu = Menu(options_menu,tearoff=0)
functions2_menu = Menu(options_menu,tearoff=0)
functions3_menu = Menu(options_menu,tearoff=0)

menu.add_cascade(label="File",menu=file_menu)
menu.add_cascade(label="Options",menu=options_menu)

file_menu.add_command(label="Generate",command=generate_objects)
file_menu.add_command(label="Directory",command=change_directory)
file_menu.add_separator()
file_menu.add_command(label="Exit",command=window.destroy)

options_menu.add_cascade(label="Entity functions",menu=functions1_menu)
options_menu.add_cascade(label="Block functions",menu=functions2_menu)
options_menu.add_cascade(label="Item functions",menu=functions3_menu)
options_menu.add_separator()
options_menu.add_radiobutton(label="Single file mode",variable=mode,value="file")
options_menu.add_radiobutton(label="Directory mode",variable=mode,value="directory")

functions1_menu.add_checkbutton(label="Summon entity",variable=E_sum)
functions1_menu.add_checkbutton(label="Give spawn egg",variable=E_giv)
functions1_menu.add_checkbutton(label="Data merge entity",variable=E_dat)

functions2_menu.add_checkbutton(label="Set block",variable=B_set)
functions2_menu.add_checkbutton(label="Data merge block",variable=B_dat)
functions2_menu.add_checkbutton(label="Give block",variable=B_giv)

functions3_menu.add_checkbutton(label="Give item",variable=I_giv)
functions3_menu.add_checkbutton(label="Summon item",variable=I_sum)
functions3_menu.add_checkbutton(label="Replace mainhand",variable=I_rep)

window.config(menu=menu)
window.mainloop()
