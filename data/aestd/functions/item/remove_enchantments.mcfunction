# Written by Aeldrion, Minecraft 19w05a
# Removes enchantments from an item (see aestd:item/save for slot index)
# Input: sender|aestd.item_slot

function aestd:item/save
data remove block 1519204 6 0 RecordItem.tag.aestd.SavedItem.tag.Enchantments
function aestd:item/load