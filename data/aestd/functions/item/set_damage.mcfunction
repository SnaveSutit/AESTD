# Written by Aeldrion, Minecraft 19w05a
# Changes the damage of an item (see aestd:item/save for slot index)
# Input: sender|aestd.item_slot|aestd.item_dmg

function aestd:item/save
execute store result block 1519204 6 0 RecordItem.tag.aestd.SavedItem.tag.Damage int 1 run scoreboard players get @s aestd.item_dmg
function aestd:item/load
