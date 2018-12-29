
import libtcodpy as libtcod

from game_messages import Message

from components.ai import ConfusedMonster


def heal(*args, **kwargs):
    entity = args[0]
    amount = kwargs.get("amount")

    results = []

    if entity.fighter.hp == entity.fighter.max_hp:
        results.append({"item_consumed": False, "message": Message("You are already at full health.", libtcod.yellow)})
    else:
        entity.fighter.heal(amount)
        results.append({"item_consumed": True, "message": Message("Your wounds feel healed!", libtcod.green)})

    return results


# Cast lighting spell, targets closest enemy
def cast_lightning(*args, **kwargs):
    caster = args[0]  # originator of spell
    entities = kwargs.get("entities")
    fov_map = kwargs.get("fov_map")
    damage = kwargs.get("damage")
    maximum_range = kwargs.get("maximum_range")

    results = []

    target = None
    closest_distance = maximum_range + 1

    for entity in entities:
        if libtcod.map_is_in_fov(fov_map, entity.x, entity.y) and entity.fighter and entity != caster:
            distance = caster.distance_to(entity)

            if distance < closest_distance:
                target = entity
                closest_distance = distance

    if target:
        results.append({"item_consumed": True, "message": Message("A lightning bolt strikes the {0} for {1} damage!".format(target.name, damage), libtcod.white)})
        results.extend(target.fighter.take_damage(damage))
    else:
        results.append({"item_consumed": False, "message": Message("No enemy close enough to strike.", libtcod.yellow)})

    return results


# Cast fireball spell, requires specified target, has radius
def cast_fireball(*args, **kwargs):
    entities = kwargs.get("entities")
    fov_map = kwargs.get("fov_map")
    damage = kwargs.get("damage")
    radius = kwargs.get("radius")
    target_x = kwargs.get("target_x")
    target_y = kwargs.get("target_y")

    results = []

    if not libtcod.map_is_in_fov(fov_map, target_x, target_y):
        results.append({"item_consumed": False, "message": Message("You cannot target outside your field of view.", libtcod.yellow)})
        return results

    results.append({"item_consumed": True, "message": Message("The fireball explodes, burning everything within {0} tiles!".format(radius), libtcod.orange)})

    for entity in entities:
        if entity.fighter and entity.distance_to_point(target_x, target_y) <= radius:
            results.append({"message": Message("The {0} is burned for {1} damage.".format(entity.name, damage), libtcod.orange)})
            results.extend(entity.fighter.take_damage(damage))

    return results


def cast_confusion(*args, **kwargs):
    entities = kwargs.get("entities")
    fov_map = kwargs.get("fov_map")
    target_x = kwargs.get("target_x")
    target_y = kwargs.get("target_y")

    results = []

    if not libtcod.map_is_in_fov(fov_map, target_x, target_y):
        results.append({"item_consumed": False, "message": Message("You cannot target a tile outside of your field of view.", libtcod.yellow)})
        return results

    for entity in entities:
        if entity.ai and entity.x == target_x and entity.y == target_y:
            confused_ai = ConfusedMonster(entity.ai, 10)
            confused_ai.owner = entity
            entity.ai = confused_ai

            results.append({"item_consumed": True, "message": Message("{0} starts to stumble around, looking confused.".format(entity.name), libtcod.light_green)})

            break
    else:
        results.append({"item_consumed": False, "message": Message("Nothing worth targeting there.", libtcod.yellow)})

    return results
