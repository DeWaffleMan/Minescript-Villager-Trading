#!python
import system.pyj.minescript as m
import sys
Minecraft = JavaClass("net.minecraft.client.Minecraft")
SlotAction = JavaClass("net.minecraft.world.inventory.ClickType")
SelectMerchantTradePacket = JavaClass("net.minecraft.network.protocol.game.ServerboundSelectTradePacket")
ClickButtonPacket = JavaClass("net.minecraft.network.protocol.game.ServerboundContainerButtonClickPacket")
ItemStack = JavaClass("net.minecraft.world.item.ItemStack")
Math = JavaClass("java.lang.Math")
Exception = JavaClass("java.lang.Exception")
IllegalArgumentException = JavaClass("java.lang.IllegalArgumentException")
OutOfBoundsException = JavaClass("java.lang.ArrayIndexOutOfBoundsException")
ArrayList = JavaClass("java.util.ArrayList")

mc = Minecraft.getInstance()

def get_closest_villagers(radius:int) -> list[m.EntityData]:
    """
    Returns a list of EntityData of villagers, sorted by ascending distance from the player

    Args:
        radiues: int, maximum distance in blocks a villager will be detected from.
    Returns:
        list[m.EntityData]: List of villagers, sorted from closest to farthest from the player
    """
    return m.entities(type = "entity.minecraft.villager", max_distance = radius, sort = "nearest") 

def look_at_villager(shift_before_clicking:bool = False, radius:int = 5) -> None:
    """
    Finds and makes the player look at the head of the closest villager to the player within (radius) blocks.

    Args:
        radius: int, Set to 5 by default, maximum distance in blocks a villager will be detected from.
        shift_before_clicking : bool, False by default, sneak before opening the trade menu.
    
    If no villagers were found, return without looking at anything.
    """
    villagers = m.entities(type = "entity.minecraft.villager", max_distance = 5, sort = "nearest") 
    if villagers:
        nearest_villager = villagers[0]
    else:
        return

    m.player_look_at(nearest_villager.position[0],nearest_villager.position[1]+1.5,nearest_villager.position[2]) # Add 1.5 to the y to look at the head

    if shift_before_clicking:
        m.player_press_sneak(True)
    m.player_press_use(True)
    m.player_press_use(False)
    if shift_before_clicking:
        m.player_press_sneak(False)



def player_has_enough(stack_required,player) -> bool:
    """
    Checks if the items stack_required are present in the player's inventory.
    Different stacks containing the same type of item do not matter, only the amount in the inventory.
    If the stack is empty or None, return True.

    Args:
        stack_required (JavaObject("net.minecraft.world.item.ItemStack")|None): ItemStack to check for in inventory. 
                        If ItemStack is empty or is None, return True 
        player (JavaObject("net.minecraft.world.entity.player.Player")): Player to read its inventory

    Returns:
        bool: Is stack_required's content inside player's inventory
    """
    if stack_required is None or stack_required.isEmpty():
        return True
    need_item = stack_required.getItem()
    need_count = stack_required.getCount() # Amount of need_item required
    total = 0                              # Amount of need_item found in inventory so far
    inv = player.getInventory()
    
    for i in range(inv.getContainerSize()): 
        s = inv.getItem(i)
        if not s.isEmpty() and s.getItem() == need_item:
            total += s.getCount()
            if total >= need_count:
                return True
    return False
def check_for_space(offer) -> bool:
    """
    Checks if the player has enough space in the inventory to trade.
    If the inventory is full, but the trade will free up an inventory slot, still return True
    Assumes a merchant screen is open
    
    Args:
        offer (JavaObject("net.minecraft.world.item.trading.MerchantOffer") (class_1914)): Trade offer, can have one or two valid item costs
    Returns:
        bool: Does the player have space for the offer's sell item if they traded with it?
    """
    player = mc.player

    stack_to_insert = offer.getResult()
    buy1 = offer.getBaseCostA()
    buy2 = offer.getItemCostB() # Start as a java.util.Optional<ItemStack> or Optiona.empty if there's only one buy item
    if not buy2.isEmpty():
        buy2 = buy2.get().itemStack() # Turn into an ItemStack if there are 2 buy items
    else:
        buy2 = None
    inv = player.getInventory()
    remaining = stack_to_insert.getCount()
    insert_item = stack_to_insert.getItem()
    max_stack_size = stack_to_insert.getMaxStackSize()

    buy1_item = buy1.getItem()
    buy1_expect = buy1.getCount()
    buy1_count = 0
    if buy2:
        buy2_item = buy2.getItem()
        buy2_expect = buy2.getCount()
        buy2_count = 0

    for i in range(inv.MAIN_SIZE): # 0,1 = buy slots   2 = sell slot   3+ = inventory

        
        slot_stack = inv.getStack(i)
        count = slot_stack.getCount()
        if slot_stack.isEmpty() and i > 2: # If there's an empty slot there must be space
            return True

        if slot_stack.method_31574(insert_item): # Can't use "is" because python doesn't count it as a statement

            max_add = max_stack_size - count
            
            remaining -= max_add
        
        if slot_stack.method_31574(buy1_item):
            buy1_count += count
        if buy2:
            if slot_stack.method_31574(buy2_item):
                buy2_count += count

    if remaining <= 0:
        return True

    # If the the trade amount is equal to the amount in the inventory, a slot will free up
    if buy1_count == buy1_expect:
        return True
    if buy2:
        if buy2_count == buy2_expect:
            return True
    return False

def can_trade(offer) -> bool:
    """
    Checks if the player has enough items to trade with offer.
    Assumes that the first buy item of the trade is not empty.
    
    Args:
        offer (JavaObject("net.minecraft.world.item.trading.MerchantOffer")): Trade offer, can have one or two valid item costs

    Returns:
        bool: Does the player have enough resources to trade with offer?
    """
    first = offer.getBaseCostA()
    second = offer.getItemCostB() # Starts as Optional
    if not second.isEmpty():
        second = second.get().itemStack() # Now it is itemStack
    else:
        second = None
    player = mc.player
    if player_has_enough(first, player):
        if second is not None:
            if player_has_enough(second, player):
                return True
            else:
                return False
        else:
            return True
    else:
        return False

def choose_and_empty_offer(offer_index:int):
    """
    Chooses a villager offer without inputing items. Useful when there are multiple offers that require the same type of item.
    
    Args:
        offer_index (int): Index (starts from 0, top to bottom) of the trade offer 

    """
    handler = mc.screen.getMenu()
    network_handler = mc.player.connection
    packet = SelectMerchantTradePacket(offer_index)

    network_handler.send(packet)
    handler.method_20215(offer_index)
    mc.gameMode.handleInventoryMouseClick(
        handler.containerId ,        # containerId  is syncId
        0,                     
        0,                     
        SlotAction.QUICK_MOVE,     # Normal click
        mc.player)
    mc.gameMode.handleInventoryMouseClick(
        handler.containerId ,        # containerId  is syncId
        1,                     
        0,                     
        SlotAction.QUICK_MOVE,     # Normal click
        mc.player)

def input_amount_at_slot(required_stack,slot_index_target:int):
    """
    Looks for an amount of items in inventory, then inputs that exact amount into a slot in the ScreenHandler.

    Args:
        required_stack (JavaObject("net.minecraft.world.item.ItemStack")): Stack needed to be on slot number slot_index_target
        slot_index_target (int): Index of slot you need to have required_stack
    """


    handler = mc.screen.getMenu()
    player = mc.player
    required_item = required_stack.getItem()
    required_amount = required_stack.getCount()
    
    
    slots = []
    
    for i in range(handler.slots.size()):  
        stack = handler.getSlot(i).getItem()
        if stack.method_31574(required_item):
            slots.append((i,stack)) 

    for i in range(len(slots)): 
        max_index = i
        for j in range(i + 1, len(slots)):
            if slots[j][1].getCount() < slots[max_index][1].getCount():
                max_index = j
        # Swap
        temp = slots[i]
        slots[i] = slots[max_index]
        slots[max_index] = temp


    for index,stack in slots:
        amount = stack.getCount()
        mc.gameMode.handleInventoryMouseClick(
            handler.containerId ,    # containerId  is syncId
            index,                     
            0,                     # left mouse button = 0
            SlotAction.PICKUP,     # Normal click
            player)
        

        amount_bigger = amount > required_amount
        if amount_bigger:
            iterations = required_amount
            for _ in range(iterations):
                
                mc.gameMode.handleInventoryMouseClick(
                    handler.containerId ,    # containerId  is syncId
                    slot_index_target,                     
                    1,                     # right mouse button = 1
                    SlotAction.PICKUP,     # Normal click
                    player)
            required_amount -= iterations
        else:
            mc.gameMode.handleInventoryMouseClick(
                handler.containerId ,    # containerId  is syncId
                slot_index_target,                     
                0,                    
                SlotAction.PICKUP,     # Normal click
                player)
            required_amount -= amount
            
        
        if required_amount <= 0:
            mc.gameMode.handleInventoryMouseClick(
                handler.containerId ,    # containerId  is syncId
                index,                     
                0,                     # left mouse button = 0
                SlotAction.PICKUP,     # Normal click
                player)  
            break
def trade_once(offer_index:int, print_exit_messages:bool = True) -> bool:
    """
    Trades with the offer one time. Will return early if one of these conditions are met:
    a. Trade got disabled/ran out of uses (red X on offer arrow)
    b. Ran out of items to trade with
    c. Ran out of inventory space

    Notice: Does NOT select the trade before hand, to avoid needless calls. Use choose_and_empty_offer first.

    Args:
        offer_index (int): The index (starts at 0, top to bottom) of the trade offer to be traded with
        print_exit_messages (bool): True by default, if True print according messages when function returns early
    Returns:
        bool: True if traded successfully, False if met one of the conditions above
    Raises:
        IllegalArgumentException: offer_index is out of bounds of the offer list
        NullPointerException: No merchantMenu is open
    """
    handler = mc.screen.getMenu()
    if handler is None:
        raise NullPointerException("Villager Menu not found")
    offers = handler.getOffers()
    if offer_index > offers.size() or offer_index < 0:
        raise IllegalArgumentException(f"offer_index must be a positive Integer (got {offer_index})")
    
    offer = offers.get(offer_index)
    maxUses = offer.getMaxUses()
    uses = offer.getUses()%maxUses

    if uses >= maxUses:
        if print_exit_messages:
            print("Trade got disabled!")
        return False
    if not can_trade(offer):
        if print_exit_messages:
            print("Ran out of items!")
        return False
    if not check_for_space(offer):
        if print_exit_messages:
            print("Ran out of inventory space!")
        return False
    
    input_amount_at_slot(offer.getBaseCostA(),0)
    if not offer.getItemCostB().isEmpty():
        input_amount_at_slot(offer.getItemCostB(),1)
    mc.gameMode.handleInventoryMouseClick(
        handler.containerId ,    # containerId  is syncId
        2,                     
        0,                    
        SlotAction.QUICK_MOVE,     # Normal click
        mc.player)
    return True

def break_block_at(pos:list[int,int,int]) -> None:
    """
    Look at the block in pos and break it.
    If block at pos is already broken (minecraft:air), return immediately
    
    Args:
        pos (List[int,int,int]): Position of block
    Raises:
        IllegalStateException: Desired position is out of reach or something in the way
    """
    if "air" in m.getblock(*pos):
        return
    m.player_look_at(pos[0]+0.5,pos[1]+0.5,pos[2]+0.5)
    targeted = m.player_get_targeted_block(4.5)
    if not targeted:
        raise IllegalStateException(f"Player can't reach {pos}")
    targeted = targeted.position
    if targeted != pos:
        raise IllegalStateException(f"Block at position {targeted} is in the way between player and {pos}")
    
    m.player_press_attack(True)
    while not "air" in m.getblock(*pos):
        sleep(0.05)
    m.player_press_attack(False)

def trade_loop(offer_index:int|None = None, print_exit_messages = True) -> None:
    """
    Will trade with the current villager until
    a. Ran out of items to trade
    b. Not enough space in the inventory to put the sold item
    c. Trade got disabled/Ran out of trade uses (The red X on the arrow)
    

    Args:
        offer_index (int|None): None by default, the number of the trade offer from top to bottom (starts at 0)
                                If None, use the system argv
        print_exit_messages (bool): True by default, if True print an corresponding message to reasons a,b,c when finished trading

    Raises:
        OutOfBoundsException:     offer_index is negative or too large
        IllegalArgumentException: Got None for offer_index but no argv[1]
        IllegalArgumentException: Got None for offer_index but argv[1] is not an integer 
    """

    
    screen = mc.screen
    handler = screen.getMenu()
    field = handler.getClass().getDeclaredField("field_7863") # merchant
    field.setAccessible(True)
    merchant = field.get(handler)
    offers = merchant.getOffers()

    player = mc.player
    network_handler = player.connection
    if offer_index is None:
        if len(sys.argv) == 1:
            raise IllegalArgumentException(r"Add index of trade after script name (starts at 0) (e.g \trade 1)") # use raw string to avoid escape character error
    
        try:
            offer_index = int(sys.argv[1])
        except:
            raise IllegalArgumentException("Trade index must be a positive integer")
    if offers.size()-1 < offer_index or offer_index < 0:
        raise OutOfBoundsException("Trade index is out of bounds of offer list")
    offer = offers.get(offer_index)

    choose_and_empty_offer(offer_index)
    #input_amount_at_slot(offer.getBaseCostA(), 0)

    # maxUses = offer.getMaxUses()
    # uses = int(offer.getUses() / maxUses) # Can't use // because Java treats it as a comment 
    # while True:
    #     offer = handler.getOffers().get(offer_index)
  
    #     if uses >= maxUses:
    #         if print_exit_messages:
    #             print("Trade got disabled!")
    #         break

    #     if not can_trade(offer):
    #         if print_exit_messages:
    #             print("Ran out of items!")
    #         break

    #     if not check_for_space(offer): # Assumes that player has enough to trade
    #         if print_exit_messages:
    #             print("Not enough space in inventory!")
    #         break

    #     network_handler.method_52787(SelectMerchantTradePacket(offer_index)) # method_52787 is sendPacket

    #     mc.gameMode.handleInventoryMouseClick(
    #         handler.field_7763,    # field_7763 is syncId
    #         2,                     # slot 2 is the slot with the sold item
    #         0,                     # left mouse button = 0
    #         SlotAction.QUICK_MOVE, # AKA shift-click
    #         player)
    #     uses += 1

look_at_villager()
m.set_timeout(trade_loop, 400)



