# Pyjinn Villager Trading

**Authors:** DeWaffleMan, 4ndr3js, JulianIsLost

Library for performing villager related tasks in Minecraft using [Minescripts Pyjinn](https://minescript.net/pyjinn/).  
This module should be imported by other scripts and not run directly.

---

## Prerequisites

Before you start, make sure you have:

- **Fabric** mod loader configured
- **Minescript 5.x** installed (Pyjinn)
- **Mappings** installed

---

## Usage

- Download the **trade_pyjinn.py** file
- Place it directly in the minescript folder
- Import the module into your script (must end on `.pyj`):

---
## Example Use
Trade with a villager's first offer until the player can't trade anymore:
```py
from trade_pyjinn import trade_once,look_at_villager,choose_and_empty_offer
import minescript as m

def main():
    choose_offer(0)

    while True:
        result = trade_once(0)
        if not result:
            break

look_at_villager()
m.set_timeout(main, 400)
```
---

## Methods

- **get_closest_villagers(radius: int) -> list[EntityData]**

   Returns a list of EntityData of villagers, sorted by ascending distance from the player

   - **radius:** `int` — The radius around the player that is searched

   Example:
   ```python
   villagers_near_me = get_closest_villagers(5)
   ```
   
- **look_at_villager(shift_before_clicking:bool = False, radius:int = 5) -> None**

   Finds and makes the player look at the head of the closest villager to the player within (radius) blocks

   - **shift_before_clicking:** `bool` - `False` by default, sneak before opening the trade menu
   - **radius:** `int` — Set to 5 by default, maximum distance in blocks a villager will be detected from

   Example:
   ```python
   look_at_villager()
   ```

- **find_trade(item_stack: ItemStack) -> int**
    
  Checks if the villagers sells the item provided in item_stack.\
  If yes, return the index of the trade, otherwise return -1.

  - **item_stack:** `ItemStack` - `ItemStack` to check for in the trades

  Note: [Here](https://github.com/JulianIsLost5/minescript-scripts/tree/main/tools) you can find a Helperscript to create ItemStack instances

- **player_has_enough(stack_required: ItemStack, player: LocalPlayer) -> bool**

  Checks if the items `stack_required` are present in the player's inventory
  
  - **stack_required:** `Itemstack` - `ItemStack` to check for in inventory
  - **player:** `LocalPlayee` — Player whoms inventory to be checked

- **check_for_space(offer: MerchantOffer) -> bool**

  Checks if the player has enough space in the inventory to trade
  
  - **offer:** `MerchantOffer` - Trade offer, can have one or two valid item costs

- **can_trade(offer: MerchantOffer) -> bool**

  Checks if the player has enough items to trade with the offer
  
  - **offer:** `MerchantOffer` - Trade offer, can have one or two valid item costs

- **choose_offer(offer_index: int)**

  Chooses a villager offer without inputing items. Useful when there are multiple offers that require the same type of item
  
  - **offer_index:** `int` - Index (starts from 0, top to bottom) of the trade offer

- **input_amount_at_slot(required_stack: ItemStack, slot_index_target: int)**

  Looks for an amount of items in inventory, then inputs that exact amount into a slot in the ScreenHandler

  - **required_stack:** `ItemStack` - Stack needed to be on slot number slot_index_target
  - **slot_index_target:** `int` - Index of slot you need to have required_stack

- **choose_and_empty_offer(offer_index:int)**
  Chooses a villager offer without inputing items. Useful when there are multiple offers that require the same type of item.
    
  - **offer_index**: `int` Index (starts from 0, top to bottom) of the trade offer
   
- **trade_once(offer_index: int, print_exit_messages:bool = True) -> bool**

  Trades with the offer one time. Will return early if one of these conditions are met:\
    a. Trade got disabled/ran out of uses (red X on offer arrow)\
    b. Ran out of items to trade with\
    c. Ran out of inventory space

  Notice: Does NOT select the trade before hand, to avoid needless calls. Use choose_and_empty_offer first.

  - **offer_index:** `int` - The index (starts at 0, top to bottom) of the trade offer to be traded with
  - **print_exit_messages:** `bool` - True by default, if True print according messages when function returns early
   
## Useful Links

- [Minecraft Internal Mappings](https://mappings.dev) 
- [Minescript Discord](https://discord.gg/NjcyvrHTze)
