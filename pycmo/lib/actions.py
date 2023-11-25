# Author: Minh Hua
# Date: 08/16/2021
# Last Update: 11/24/2023
# Purpose: Encodes the action space of the game.

# imports
import collections
from typing import Tuple
from random import uniform, randint

from pycmo.lib.features import Features, FeaturesFromSteam, Unit

Function = collections.namedtuple("Function", ['id', 'name', 'corresponding_def', 'args', 'arg_types'])

# canned actions that can be called by an agent to send an action
def no_op():
  return ""

def launch_aircraft(side:str, unit_name:str, launch_yn:str) -> str:
  return f"ScenEdit_SetUnit({{side = '{side}', name = '{unit_name}', Launch = '{launch_yn}'}})"

def set_unit_course(side:str, unit_name:str, latitude:float, longitude:float) -> str:
  return f"ScenEdit_SetUnit({{side = '{side}', name = '{unit_name}', course = {{{{longitude = {longitude}, latitude = {latitude}, TypeOf = 'ManualPlottedCourseWaypoint'}}}}}})"

def manual_attack_contact(attacker_id:str, contact_id:str, weapon_id:str, qty:int, mount_id:str=None) -> str:
  return f"ScenEdit_AttackContact('{attacker_id}', '{contact_id}' , {{mode='1', " + (f"mount='{mount_id}', " if mount_id else "") + f"weapon='{weapon_id}', qty='{qty}'}})"

def auto_attack_contact(attacker_id:str, contact_id:str) -> str:
  return f"ScenEdit_AttackContact('{attacker_id}', '{contact_id}', {{mode='0'}})"

def refuel_unit(side:str, unit_name:str, tanker_name:str) -> str:
  return f"ScenEdit_RefuelUnit({{side='{side}', unitname='{unit_name}', tanker='{tanker_name}'}})"

def auto_refuel_unit(side:str, unit_name:str) -> str:
  return f"ScenEdit_RefuelUnit({{side='{side}', unitname='{unit_name}'}})"

def rtb(side:str, unit_name:str) -> str:
  return f"ScenEdit_SetUnit({{side = '{side}', name = '{unit_name}', RTB = true}})"

ARG_TYPES = {
  'no_op': ['NoneChoice'],
  'launch_aircraft': ['EnumChoice', 'EnumChoice', 'EnumChoice'],
  'set_unit_course': ['EnumChoice', 'EnumChoice', 'Range', 'Range'],
  'manual_attack_contact': ['EnumChoice', 'EnumChoice', 'EnumChoice', 'EnumChoice', 'EnumChoice'],
  'auto_attack_contact': ['EnumChoice', 'EnumChoice'],
  'refuel_unit': ['EnumChoice', 'EnumChoice', 'EnumChoice'],
  'auto_refuel_unit': ['EnumChoice', 'EnumChoice'],
  'rtb': ['EnumChoice', 'EnumChoice'],
}

class AvailableFunctionsSteam():
  def __init__(self, features:Features | FeaturesFromSteam):
    self.sides = [features.player_side]

    self.unit_ids = self.get_unit_ids(features)
    self.contact_ids = self.get_contact_ids(features)
    self.mount_ids, self.loadout_ids, self.weapon_ids, self.weapon_qtys = self.get_weapons(features)

    self.VALID_FUNCTIONS = self.get_valid_functions()

  def get_unit_ids(self, features:Features|FeaturesFromSteam) -> list[str]:
    return [unit.ID for unit in features.units]

  def get_contact_ids(self, features:Features|FeaturesFromSteam) -> list[str]:
    return [contact.ID for contact in features.contacts]
  
  def get_weapons(self, features:Features|FeaturesFromSteam) -> Tuple[list[str], list[str], list[str], list[int]]:
    mount_ids = []
    loadout_ids = []
    weapon_ids = []
    weapon_qtys = []
    for unit in features.units:
      unit_mount_ids, unit_mount_weapon_ids, unit_mount_weapon_qtys = self.get_mount_ids_weapon_ids_and_qtys(unit)
      unit_loadout_id, unit_loadout_weapon_ids, unit_loadout_weapon_qtys = self.get_loadout_id_weapon_ids_and_qtys(unit)
      mount_ids += unit_mount_ids
      if unit_loadout_id: loadout_ids.append(unit_loadout_id)
      weapon_ids += unit_mount_weapon_ids + unit_loadout_weapon_ids
      weapon_qtys += unit_mount_weapon_qtys + unit_loadout_weapon_qtys
    return mount_ids, loadout_ids, weapon_ids, weapon_qtys
  
  def get_mount_ids_weapon_ids_and_qtys(self, unit:Unit) -> Tuple[list[str], list[str], list[int]]:
    mount_ids = []
    weapon_ids = []
    weapon_qtys = []
    if unit.Mounts:
      for mount in unit.Mounts:
        mount_ids.append(mount.DBID)
        for weapon in mount.Weapons:
          weapon_ids.append(weapon.WeaponID)
          weapon_qtys.append(weapon.QuantRemaining)
    return mount_ids, weapon_ids, weapon_qtys

  def get_loadout_id_weapon_ids_and_qtys(self, unit:Unit) -> Tuple[str | None, list[str], list[int]]:
    loadout_id = None
    weapon_ids = []
    weapon_qtys = []
    loadout = unit.Loadout
    if loadout:
      loadout_id = loadout.DBID
      for weapon in loadout.Weapons:
        weapon_ids.append(weapon.WeaponID)
        weapon_qtys.append(weapon.QuantRemaining)
    return loadout_id, weapon_ids, weapon_qtys
  
  def get_valid_functions(self) -> list[Function]:
    VALID_FUNCTION_ARGS = {
      'no_op': [],
      'launch_aircraft': [self.sides, self.unit_ids, ["true", "false"]],
      'set_unit_course': [self.sides, self.unit_ids, [-90, 90], [-180, 180]],
      'manual_attack_contact': [self.unit_ids, self.contact_ids, self.weapon_ids, self.weapon_qtys, self.mount_ids],
      'auto_attack_contact': [self.unit_ids, self.contact_ids],
      'refuel_unit': [self.sides, self.unit_ids, self.unit_ids],
      'auto_refuel_unit': [self.sides, self.unit_ids],
      'rtb': [self.sides, self.unit_ids]
    }
    valid_functions = [
      Function(0, "no_op", no_op, VALID_FUNCTION_ARGS['no_op'], ARG_TYPES['no_op']),
      Function(1, "launch_aircraft", launch_aircraft, VALID_FUNCTION_ARGS['launch_aircraft'], ARG_TYPES['launch_aircraft']),
      Function(2, 'set_unit_course', set_unit_course, VALID_FUNCTION_ARGS['set_unit_course'], ARG_TYPES['set_unit_course']),
      Function(3, "manual_attack_contact", manual_attack_contact, VALID_FUNCTION_ARGS['manual_attack_contact'], ARG_TYPES['manual_attack_contact']),
      Function(4, "auto_attack_contact", auto_attack_contact, VALID_FUNCTION_ARGS['auto_attack_contact'], ARG_TYPES['auto_attack_contact']),
      Function(5, 'refuel_unit', refuel_unit, VALID_FUNCTION_ARGS['refuel_unit'], ARG_TYPES['refuel_unit']),
      Function(6, 'auto_refuel_unit', auto_refuel_unit, VALID_FUNCTION_ARGS['auto_refuel_unit'], ARG_TYPES['auto_refuel_unit']),
      Function(7, 'rtb', rtb, VALID_FUNCTION_ARGS['rtb'], ARG_TYPES['rtb'])
    ]
    return valid_functions
  
  def sample(self) -> str:
    random_function = self.VALID_FUNCTIONS[randint(0, len(self.VALID_FUNCTIONS) - 1)]
    if len(random_function.arg_types) == 1 and random_function.arg_types[0] == "NoneChoice":
      return random_function.corresponding_def()

    function_args = []
    for valid_args, arg_type in zip(random_function.args, random_function.arg_types):
      if arg_type == "EnumChoice":
        arg = valid_args[randint(0, len(valid_args) - 1)]
      elif arg_type == "Range":
        arg = uniform(valid_args[0], valid_args[1])
      function_args.append(arg)
    
    return random_function.corresponding_def(*function_args)

class AvailableFunctions():
  def __init__(self, features):
    sides = [features.player_side]
    units = []
    contacts = []
    if features.units != None:
      units = [unit.ID for unit in features.units]
    if features.contacts != None:
      contacts = [contact.ID for contact in features.contacts]
    weapons = [weap.WeaponID for weap in features.avai_weapons]
    mounts = []
    for unit in features.units:
      if unit.Mounts != None:
        for mount in unit.Mounts:
          mounts.append(mount.DBID)
    VALID_FUNCTION_ARGS = {
      'no_op': [],
      'launch_aircraft': [sides, units, ["true", "false"]],
      'set_unit_course': [sides, units, [-90, 90], [-180, 180]],
      'manual_attack_contact': [units, contacts, weapons, [1], mounts],
      'auto_attack_contact': [units, contacts],
      'refuel_unit': [sides, units, units],
      'rtb': [sides, units],
      'auto_refuel_unit': [sides, units]
    }
    ARG_TYPES = {
      'no_op': ['NoneChoice'],
      'launch_aircraft': ['EnumChoice', 'EnumChoice', 'EnumChoice'],
      'set_unit_course': ['EnumChoice', 'EnumChoice', 'Range', 'Range'],
      'manual_attack_contact': ['EnumChoice', 'EnumChoice', 'EnumChoice', 'EnumChoice', 'EnumChoice'],
      'auto_attack_contact': ['EnumChoice', 'EnumChoice'],
      'refuel_unit': ['EnumChoice', 'EnumChoice', 'EnumChoice'],
      'rtb': ['EnumChoice', 'EnumChoice'],
      'auto_refuel_unit': ['EnumChoice', 'EnumChoice']
    }
    self.VALID_FUNCTIONS = [
      Function(0, "no_op", no_op, VALID_FUNCTION_ARGS['no_op'], ARG_TYPES['no_op']),
      Function(1, "launch_aircraft", launch_aircraft, VALID_FUNCTION_ARGS['launch_aircraft'], ARG_TYPES['launch_aircraft']),
      Function(2, 'set_unit_course', set_unit_course, VALID_FUNCTION_ARGS['set_unit_course'], ARG_TYPES['set_unit_course']),
      Function(3, "manual_attack_contact", manual_attack_contact, VALID_FUNCTION_ARGS['manual_attack_contact'], ARG_TYPES['manual_attack_contact']),
      Function(4, "auto_attack_contact", auto_attack_contact, VALID_FUNCTION_ARGS['auto_attack_contact'], ARG_TYPES['auto_attack_contact']),
      Function(5, 'refuel_unit', refuel_unit, VALID_FUNCTION_ARGS['refuel_unit'], ARG_TYPES['refuel_unit']),
      Function(6, 'rtb', rtb, VALID_FUNCTION_ARGS['rtb'], ARG_TYPES['rtb']),
      Function(7, 'auto_refuel_unit', auto_refuel_unit, VALID_FUNCTION_ARGS['auto_refuel_unit'], ARG_TYPES['auto_refuel_unit'])
    ]