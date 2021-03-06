# Written by Aeldrion, Minecraft 19w05a
# Checks if the save chunk is marked for force loading

execute store success score #aestd.chunk_loaded aestd.var run forceload query 1519204 0
# If the chunk isn't loaded, ask the player to load it
execute if score #aestd.chunk_loaded aestd.var matches 0 run function aestd.internal:load/ask_forceload
# If the chunk is loaded but not set up, set it up
execute if score #aestd.chunk_loaded aestd.var matches 1 unless score #aestd.chunk_setup aestd.var matches 1 run function aestd.internal:load/setup_save_chunk
