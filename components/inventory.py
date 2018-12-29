
import libtcodpy as libtcod

from game_messages import Message


class Inventory:
    def __init__(self, capacity):
        self.capacity = capacity
        self.items = []

    def add_item(self, item):
        results = []

        if len(self.items) >= self.capacity:
            results.append({
                "item_added": None,
                "message": Message("You cannot carry any more items, your inventory is full.", libtcod.yellow)
            })
        else:
            results.append({
                "item_added": item,
                "message": Message("You pick up the {0}!".format(item.name), libtcod.light_blue)
            })

            self.items.append(item)

        return results

    def use_item(self, item_entity, **kwargs):
        results = []

        item_component = item_entity.item

        # Handle player using inventory item
        if item_component.use_function is None:
            results.append({"message": Message("The {0} cannot be used".format(item_entity.name), libtcod.yellow)})
        else:
            # If item requires targeting, initiate that before using
            if item_component.targeting and not (kwargs.get("target_x") or kwargs.get("target_y")):
                results.append({"targeting": item_entity})
            else:
                kwargs = {**item_component.function_kwargs, **kwargs}
                item_use_results = item_component.use_function(self.owner, **kwargs)

                for item_use_result in item_use_results:
                    if item_use_result.get("item_consumed"):
                        self.remove_item(item_entity)

                results.extend(item_use_results)

        return results

    def remove_item(self, item):
        """
        Removes item from inventory item list.
        :param item: item contained in inventory item list.
        """
        self.items.remove(item)

    def drop_item(self, item):
        results = []

        item.x = self.owner.x
        item.y = self.owner.y

        self.remove_item(item)
        results.append({"item_dropped": item, "message": Message("You dropped the {0}".format(item.name), libtcod.yellow)})

        return results
