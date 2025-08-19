#!python
import system.pyj.minescript as m
import sys
Minecraft = JavaClass("net.minecraft.client.Minecraft")
SlotAction = JavaClass("net.minecraft.world.inventory.ClickType")
SelectMerchantTradePacket = JavaClass("net.minecraft.network.protocol.game.ServerboundSelectTradePacket")
ItemStack = JavaClass("net.minecraft.world.item.ItemStack")
Math = JavaClass("java.lang.Math")
Exception = JavaClass("java.lang.Exception")

mc = Minecraft.getInstance()

def get_closest_villagers(radius:int):
    """
    Returns a list of EntityData of villagers, in sorted by ascending distance from the player
    """
    return m.entities(type = "entity.minecraft.villager", max_distance = radius, sort = "nearest") 

def look_at_villager(shift_before_clicking:bool = False):
    villagers = m.entities(type = "entity.minecraft.villager", max_distance = 5, sort = "nearest") 
    nearest_villager = villagers[0]
    villager_id = nearest_villager.id

    m.player_look_at(nearest_villager.position[0],nearest_villager.position[1]+1.5,nearest_villager.position[2]) # Add 1.5 to the y to look at the head

    if shift_before_clicking:
        m.player_press_sneak(True)
    m.player_press_use(True)
    m.player_press_use(False)
    if shift_before_clicking:
        m.player_press_sneak(False)



def player_has_enough(stack_required,player):
    if stack_required is None or stack_required.isEmpty():
        return True
    need_item = stack_required.getItem()
    need_count = stack_required.getCount()
    inv = player.getInventory()
    total = 0
    for i in range(inv.getContainerSize()):
        s = inv.getItem(i)
        if not s.isEmpty() and s.getItem() == need_item:
            total += s.getCount()
            if total >= need_count:
                return True
    return False
def check_for_space(offer):
    stack_to_insert = offer.getResult()
    buy1 = offer.getBaseCostA()
    buy2 = offer.getItemCostB()
    if not buy2.isEmpty():
        buy2 = buy2.get().itemStack()
    else:
        buy2 = None

    player = mc.player
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

    for i in range(inv.INVENTORY_SIZE):

        inv.getItem(i)
        slot_stack = inv.getItem(i)
        count = slot_stack.getCount()
        if slot_stack.isEmpty(): # If there's an empty slot there must be space
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
    if buy1_count == buy1_expect:
        return True
    elif buy2:
        if buy2_count == buy2_expect:
            return True
    return False

def can_trade(offer):
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

    


def trade_loop(): # (main)
    screen = mc.screen
    handler = screen.getMenu()
    field = handler.getClass().getDeclaredField("field_7863") # merchant
    field.setAccessible(True)
    merchant = field.get(handler)
    offers = merchant.getOffers()

    player = mc.player
    network_handler = player.connection 
    if len(sys.argv) == 1:
        raise Exception(r"Add index of trade after script name (starts at 0) (e.g \trade 1)")
    
    try:
        offer_index = int(sys.argv[1])
    except:
        raise Exception("Trade index must be a positive integer")
    if offers.size()-1 < offer_index or offer_index < 0:
        raise Exception("Trade index is out of bounds of offer list")
    offer = offers.get(offer_index)


    maxUses = offer.getMaxUses()
    uses = int(offer.getUses() / maxUses) # Can't use // because Java treats it as a comment 
    while True:
        offer = handler.getOffers().get(offer_index)
  
        if uses >= maxUses:
            print("Trade got disabled!")
            break

        if not can_trade(offer):
            print("Ran out of items!")
            break

        if not check_for_space(offer): # Assumes that player has enough to trade
            print("Not enough space in inventory!")
            break

        network_handler.method_52787(SelectMerchantTradePacket(offer_index)) # method_52787 is sendPacket

        mc.gameMode.handleInventoryMouseClick(
            handler.field_7763,    # field_7763 is syncId
            2,                     # slot 2 is the slot with the sold item
            0,                     # left mouse button = 0
            SlotAction.QUICK_MOVE, # AKA shift-click
            player)
        uses += 1

look_at_villager()
m.set_timeout(trade_loop, 400)